from typing import Optional
import typer
import matplotlib.pyplot as plt
import random as rand
import json
import sys

from ..workflow.pipeline import process_reviews
from ..workflow.vader import aggregate_sentiments

from . import __app_name__, __version__

app = typer.Typer()

def _version_callback(value: bool):
    if value:
        typer.echo(f"{__app_name__} version: {__version__}")
        raise typer.Exit()

@app.callback()
def version(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

@app.command()
def sentiment(
    csv: Optional[str] = typer.Option(None, "--csv", help="Path to the CSV file containing reviews."),
    text: Optional[str] = typer.Option(None, "--text", help="Text of the review to analyze."),
    lines: Optional[str] = typer.Option(None, "--lines", help="Line number of the review to analyze."),
    random: Optional[bool] = typer.Option(False, "--random", help="Pick a random review from the CSV file."),
    graph: Optional[bool] = typer.Option(False, "--graph", help="Output a graph of the sentiments."),
    jsonl: Optional[bool] = typer.Option(None, "--jsonl", help="Output is formatted in jsonl.")
):
    if text:
        reviews = [text]
    elif csv:
        with open(csv, 'r', encoding='utf-8') as file:
            reviews = file.readlines()
        
        if random:
            review = rand.choice(reviews)
            reviews = [review]
        elif lines is not None:
            if '-' in lines:
                start, end = map(int, lines.split('-'))
                if start > 0 and end > 0 and start < end and start < len(reviews) and end < len(reviews):
                    reviews = reviews[start:end+1]
                else:
                    typer.echo("Invalid line range.")
                    raise typer.Exit()
            else:
                line_number = int(lines)
                if line_number > 0 and line_number < len(reviews):
                    reviews = [reviews[line_number]]
                else:
                    typer.echo("Invalid line number.")
                    raise typer.Exit()
    else:
        typer.echo("Either csv or text must be provided.")
        raise typer.Exit()
    
    sentiments = process_reviews(reviews)
    
    if graph:
        plot_sentiments(sentiments)
    
    if jsonl:
        for review, sentiment in zip(reviews, sentiments):
            json_line = json.dumps({"review": review.strip(), "sentiment": sentiment}, ensure_ascii=True)
            typer.echo(json_line)
    else:
        for review, sentiment in zip(reviews, sentiments):
            review_ascii = review.strip().encode('ascii', 'backslashreplace').decode('ascii')
            sentiment_ascii = json.dumps(sentiment, ensure_ascii=True)
            typer.echo(f"Review: {review_ascii}")
            typer.echo(f"Sentiment: {sentiment_ascii}")
            typer.echo("")

@app.command()
def aggregate_sentiment(reviews_file: str, output_graph: Optional[bool] = False):
    with open(reviews_file, 'r', encoding='utf-8') as file:
        reviews = file.readlines()[1:]
    
    sentiments = process_reviews(reviews)
    total_sentiment = aggregate_sentiments(sentiments)
    
    typer.echo("Aggregated Sentiment:")
    typer.echo(f"Positive: {total_sentiment['pos']}")
    typer.echo(f"Neutral: {total_sentiment['neu']}")
    typer.echo(f"Negative: {total_sentiment['neg']}")
    typer.echo(f"Compound: {total_sentiment['compound']}")
    
    if output_graph:
        plot_aggregate_sentiment(total_sentiment)

@app.command()
def plot_sentiment(reviews_file: str):
    with open(reviews_file, 'r', encoding='utf-8') as file:
        reviews = file.readlines()[:1]
    
    sentiments = process_reviews(reviews)
    plot_sentiments(sentiments)

def plot_sentiments(sentiments):
    positive = [s['pos'] for s in sentiments]
    neutral = [s['neu'] for s in sentiments]
    negative = [s['neg'] for s in sentiments]
    
    plt.figure(figsize=(10, 5))
    plt.plot(positive, label='Positive')
    plt.plot(neutral, label='Neutral')
    plt.plot(negative, label='Negative')
    plt.xlabel('Review')
    plt.ylabel('Sentiment Score')
    plt.legend()
    plt.title('Sentiment Analysis of Reviews')
    plt.show()

def plot_aggregate_sentiment(total_sentiment):
    labels = ['Positive', 'Neutral', 'Negative', 'Compound']
    sizes = [total_sentiment['pos'], total_sentiment['neu'], total_sentiment['neg'], total_sentiment['compound']]
    
    plt.figure(figsize=(10, 5))
    plt.bar(labels, sizes, color=['green', 'blue', 'red', 'purple'])
    plt.xlabel('Sentiment')
    plt.ylabel('Average Score')
    plt.title('Aggregated Sentiment Analysis')
    plt.show()

if __name__ == "__main__":
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
    app()