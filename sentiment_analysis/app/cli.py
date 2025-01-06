from typing import Optional
import typer
import json
from pathlib import Path
import time
import asyncio

from ..workflow import SentimentAnalyzer, SentimentPlotter
from ..workflow.cleaning import TextCleaner, CsvCleaner
from ..sources.letterboxd.scraper import async_scrape_reviews, BASE_URL
from ..sources.letterboxd.db import save_reviews

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
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

@app.command(help="Scrape movie reviews from Letterboxd.")
def scrape(
    movie: str = typer.Argument(..., help="Movie name (e.g. 'wicked-2024')"),
    clean: bool = typer.Option(False, "--clean", help="Clean scraped data immediately"),
):
    """Scrape reviews for a movie from Letterboxd and optionally clean the data"""
    
    start_time = time.time()
    try:
        reviews = asyncio.run(async_scrape_reviews(BASE_URL, movie))
        save_reviews(reviews, movie)
        
        scrape_time = time.time() - start_time
        typer.echo(f"Scraped {len(reviews)} reviews in {scrape_time:.2f} seconds")
        typer.echo(f"Saved to 'out/db/letterboxd/raw/{movie}.csv'")
        
        if clean:
            cleaner = CsvCleaner(TextCleaner())
            cleaner.clean_csv(f'out/db/letterboxd/raw/{movie}.csv', movie)
            
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)
    
@app.command(help="Clean and preprocess review data.")
def clean(
    csv: str = typer.Argument(..., help="Path to CSV file to clean"),
):
    """Clean and preprocess review data"""
    
    try:
        movie_name = Path(csv).stem
        cleaner = CsvCleaner(TextCleaner())
        cleaner.clean_csv(csv, movie_name)
    except Exception as e:
        typer.echo(f"Error cleaning data: {e}")
        raise typer.Exit(1)

@app.command(help="Analyze sentiment of text or reviews in CSV.")
def analyze(
    csv: Optional[str] = typer.Option(None, "--csv", help="Path to CSV file containing reviews"),
    text: Optional[str] = typer.Option(None, "--text", help="Single text to analyze"),
    model: str = typer.Option('vader', "--model", help="Model to use (vader/logreg)"),
    graph: Optional[str] = typer.Option(None, "--graph", help="Plot type (distribution/comparison/averages/all)"),
    output: str = typer.Option('out/plots', "--output", help="Directory to save plots (default: out/plots)"),
    jsonl: bool = typer.Option(False, "--jsonl", help="Output in JSONL format. This includes vector data."),
):
    """Analyze sentiment using specified model and display/save results"""
    if not csv and not text:
        typer.echo("Either --csv or --text must be provided")
        raise typer.Exit(1)
    
    if csv and text:
        typer.echo("Cannot use both --csv and --text together")
        raise typer.Exit(1)

    analyzer = SentimentAnalyzer(model)
    plotter = SentimentPlotter(output) if graph else None
    
    if text:
        sentiment = analyzer.model.analyze(text)
        if jsonl:
            typer.echo(json.dumps({"text": text, "sentiment": sentiment}))
        else:
            typer.echo(f"Text: {text}")
            typer.echo(f"Sentiment: {json.dumps(sentiment, indent=2)}")
        return
    
    try:
        results = analyzer.analyze_reviews(csv)
        if jsonl:
            typer.echo(json.dumps(results))
        else:
            typer.echo(f"\n{model.upper()} Analysis Results")
            typer.echo("-" * 50)
            typer.echo(f"Total Reviews: {results['total_reviews']}")
            
            typer.echo("\nAverage Scores:")
            for metric, score in results['average_scores'].items():
                typer.echo(f"  {metric.title()}: {score:.3f}")
            
            typer.echo("\nSentiment Distribution:")
            for sentiment, count in results['sentiment_distribution'].items():
                typer.echo(f"  {sentiment.title()}: {count}")
            
            typer.echo("\nScore Comparison:")
            comp = results['comparison']
            typer.echo(f"  Correlation: {comp['correlation']:.3f}")
            typer.echo(f"  Mean Absolute Error: {comp['mae']:.3f}")
            typer.echo(f"  Root Mean Square Error: {comp['rmse']:.3f}")
        
        if graph and plotter:
            movie_name = Path(csv).stem
            if graph == 'distribution':
                plotter.plot_sentiment_distribution(results, movie_name, model)
            elif graph == 'comparison':
                plotter.plot_score_comparison(results, movie_name)
            elif graph == 'averages':
                plotter.plot_average_scores(results, movie_name)
            elif graph == 'all':
                plotter.plot_all(results, movie_name, model)
            else:
                typer.echo(f"Invalid graph type: {graph}")
                raise typer.Exit(1)
                
    except Exception as e:
        typer.echo(f"Error analyzing CSV: {str(e)}")
        raise typer.Exit(1)
    