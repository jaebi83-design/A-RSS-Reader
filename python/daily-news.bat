@echo off
REM Daily News - Quick launch script for SpeedyReader
REM Clears old articles and fetches top 5 from each feed

cd /d "%~dp0"
python -m src.main --clear-articles --limit-per-feed 5
