@echo off
REM Batch-script to run the sentiment_analysis CLI

REM Check if arguments are passed
if "%~1"=="" (
    echo Usage: sentiment [OPTIONS]
    echo Try 'sentiment --help' for help.
    exit /b 1
)

REM Execute the Python command with the passed arguments
python -m sentiment_analysis.app.main %*