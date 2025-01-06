# workflow/plotter.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
from typing import Dict, Optional, Callable, Tuple

@dataclass
class PlotConfig:
    title: str
    figsize: Tuple[int, int]
    filename: str
    plot_func: Callable
    subplot_args: Dict = None

class SentimentPlotter:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else None
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use("seaborn-v0_8")
        plt.ioff()
    
    def _base_plot(self, config: PlotConfig, show: bool = True):
        """Base plotting method with common functionality"""
        config.plot_func(**config.subplot_args if config.subplot_args else {})
        
        if self.output_dir:
            plt.savefig(self.output_dir / config.filename)
        if show:
            plt.show()
        else:
            plt.close()

    def plot_sentiment_distribution(self, results: Dict, movie_name: str, model_type: str, show: bool = True):
        """Plot the distribution of sentiment scores"""
        def plot_pie(labels, sizes):
            plt.pie(sizes, labels=labels, autopct='%1.1f%%')
            
        config = PlotConfig(
            title=f'Sentiment Distribution - {model_type.upper()}',
            figsize=(10, 6),
            filename=f'{movie_name}_{model_type}_distribution.png',
            plot_func=plot_pie,
            subplot_args={
                'labels': list(results['sentiment_percentages'].keys()),
                'sizes': list(results['sentiment_percentages'].values())
            }
        )
        self._base_plot(config, show)
    
    def plot_score_comparison(self, results: Dict, movie_name: str, show: bool = True):
        """Plot the comparison between review scores and sentiment scores"""
        def plot_comparison(df, comparison):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            sns.kdeplot(data=df, x='score', label='Review Scores', ax=ax1)
            sns.kdeplot(data=df, x='normalized_compound', label='Sentiment Scores', ax=ax1)
            ax1.set_title('Score Distribution Comparison')
            ax1.set_xlabel('Normalized Score')
            ax1.legend()
            
            sns.regplot(data=df, x='score', y='normalized_compound', ax=ax2)
            ax2.set_title(f'Score Correlation (r={comparison["correlation"]})')
            ax2.set_xlabel('Review Score')
            ax2.set_ylabel('Sentiment Score')
            
        comparison = results['comparison']
        df = pd.DataFrame({
            'score': comparison['review_scores'],
            'normalized_compound': comparison['sentiment_scores']
        })
        
        config = PlotConfig(
            title='Score Comparison',
            figsize=(15, 5),
            filename=f'{movie_name}_score_comparison.png',
            plot_func=plot_comparison,
            subplot_args={'df': df, 'comparison': comparison}
        )
        self._base_plot(config, show)
    
    def plot_average_scores(self, results: Dict, movie_name: str, show: bool = True):
        """Plot the average sentiment scores"""
        def plot_averages(scores):
            plt.bar(scores.keys(), scores.values())
            plt.ylabel('Score')
            
        config = PlotConfig(
            title=f'Average Sentiment Scores',
            figsize=(8, 5),
            filename=f'{movie_name}_averages.png',
            plot_func=plot_averages,
            subplot_args={'scores': results['average_scores']}
        )
        self._base_plot(config, show)
    
    def plot_all(self, results: Dict, movie_name: str, model_type: str, show: bool = True):
        """Plot all visualizations in one figure"""
        def plot_combined(results, model_type):
            fig = plt.figure(figsize=(15, 10))
            gs = fig.add_gridspec(2, 2)
            
            ax1 = fig.add_subplot(gs[0, 0])
            labels = list(results['sentiment_percentages'].keys())
            sizes = list(results['sentiment_percentages'].values())
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
            ax1.set_title(f'Sentiment Distribution - {model_type}')
            
            ax2 = fig.add_subplot(gs[0, 1])
            comparison = results['comparison']
            df = pd.DataFrame({
                'score': comparison['review_scores'],
                'normalized_compound': comparison['sentiment_scores']
            })
            sns.kdeplot(data=df, x='score', label='Review Scores', ax=ax2)
            sns.kdeplot(data=df, x='normalized_compound', label='Sentiment Scores', ax=ax2)
            ax2.set_title('Score Distribution')
            ax2.set_xlabel('Normalized Score')
            ax2.legend()
            
            ax3 = fig.add_subplot(gs[1, 0])
            sns.regplot(data=df, x='score', y='normalized_compound', ax=ax3)
            ax3.set_title(f'Score Correlation (r={comparison["correlation"]})')
            ax3.set_xlabel('Review Score')
            ax3.set_ylabel('Sentiment Score')
            
            ax4 = fig.add_subplot(gs[1, 1])
            scores = results['average_scores']
            ax4.bar(scores.keys(), scores.values())
            ax4.set_title('Average Sentiment Scores')
            ax4.set_ylabel('Score')
        
        config = PlotConfig(
            title='Sentiment Analysis Overview',
            figsize=(15, 10),
            filename=f'{movie_name}_{model_type}_analysis.png',
            plot_func=plot_combined,
            subplot_args={'results': results, 'model_type': model_type}
        )
        self._base_plot(config, show)