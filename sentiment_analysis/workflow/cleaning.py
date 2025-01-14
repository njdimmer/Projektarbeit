import re
import pandas as pd
import os
from langdetect import detect, LangDetectException
import emoji
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class TextCleaner:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))

    def extract_emojis(self, text):
        """Extract emojis from text and return their descriptions"""
        emoji_list = []
        for char in text:
            if char in emoji.EMOJI_DATA:
                emoji_name = emoji.EMOJI_DATA[char]['en'].replace(':', '').replace('_', ' ')
                emoji_list.append(emoji_name)
        return ' '.join(emoji_list) if emoji_list else ''

    def clean_text(self, text):
        """Clean text and convert emojis to descriptions. Also remove non-English text."""
        emoji_content = self.extract_emojis(text)
        
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'<.*?>', '', text)
        text = ''.join([char for char in text if char.isalnum() or char.isspace()])
        
        cleaned_text = f"{text.lower()} {emoji_content}".strip()
        
        try:
            if detect(cleaned_text) != 'en':
                return ''
        except LangDetectException:
            return ''
        
        return cleaned_text

    def remove_stopwords(self, text):
        """Remove stopwords but keep emoji descriptions"""
        words = text.split()
        filtered = [word for word in words if word not in self.stopwords or 
                   any(char in emoji.EMOJI_DATA for char in word)]
        return " ".join(filtered)

    def lemmatize_text(self, text):
        """Lemmatize while preserving emoji content"""
        words = text.split()
        lemmatized = [self.lemmatizer.lemmatize(word) 
                     if not any(char in emoji.EMOJI_DATA for char in word) 
                     else word for word in words]
        return ' '.join(lemmatized)

    def preprocess_text(self, text):
        """Apply all preprocessing steps"""
        text = self.clean_text(text)
        if not text:
            return ''
        text = self.remove_stopwords(text)
        text = self.lemmatize_text(text)
        return text

class CsvCleaner:
    def __init__(self, cleaner: TextCleaner, base_path='out/db/letterboxd/clean/'):
        self.cleaner = cleaner
        self.base_path = base_path

    def normalize_rating(self, rating):
        """Normalize rating from Letterboxd scale (0.5-5.0) to range [0-1]"""
        try:
            rating = float(rating)
            if 0.5 <= rating <= 5:
                return round((rating - 0.5) / 4.5, 2)
            return None
        except ValueError:
            return None

    def remove_duplicates(self, df):
        """Remove duplicate reviews based on the 'review' column"""
        return df.drop_duplicates(subset=['review'], keep='first')

    def clean_csv(self, input_path, movie_name):
        """Clean the CSV file and store it in the specified directory"""
        df = pd.read_csv(input_path)
        
        df = df[['review', 'score']].dropna(subset=['review'])
        df['review'] = df['review'].apply(lambda x: self.cleaner.preprocess_text(x))
        df = df[df['review'] != '']
        df['score'] = df['score'].apply(self.normalize_rating)
        df = df.dropna(subset=['score'])

        df = self.remove_duplicates(df)

        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        
        output_path = os.path.join(self.base_path, f"{movie_name}.csv")
        df[['review', 'score']].to_csv(output_path, index=False)

        print(f"Cleaned data saved to {output_path}")

if __name__ == "__main__":
    text_cleaner = TextCleaner()
    csv_cleaner = CsvCleaner(text_cleaner)

    movie_name = 'wicked-2024'
    input_csv_path = f'db/letterboxd/raw/{movie_name}.csv'

    csv_cleaner.clean_csv(input_csv_path, movie_name)
