from typing import Optional
import typer
import matplotlib.pyplot as plt

from . import __app_name__, __version__
from ..workflow.pipeline import process_reviews

app =  typer.Typer()

def _version_callback(value: bool):
    if value:
        typer.echo(f"{__app_name__} version: {__version__}")
        raise typer.Exit()
    
@app.callback()
def version(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

@app.command()
def analyze_sentiment(reviews_file: str, output_graph: Optional[bool] = False):
    with open(reviews_file, 'r', encoding='utf-8') as file:
        reviews = file.readlines()
    
    sentiments = process_reviews(reviews)
    
    if output_graph:
        plot_sentiments(sentiments)
    
    for review, sentiment in zip(reviews, sentiments):
        typer.echo(f"Review: {review.strip()}")
        typer.echo(f"Sentiment: {sentiment}")
        typer.echo("")

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
