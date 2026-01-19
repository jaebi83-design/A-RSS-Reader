@echo off
REM Test script for SpeedyReader Python version

echo ============================================
echo SpeedyReader - Test Run
echo ============================================
echo.

echo Step 1: Showing help...
python -m src.main
echo.
echo.

echo ============================================
echo Step 2: Adding a test feed (Hacker News RSS)
echo ============================================
python -m src.main --add-feed https://hnrss.org/newest
echo.
echo.

echo ============================================
echo Step 3: Listing your feeds
echo ============================================
python -m src.main --list-feeds
echo.
echo.

echo ============================================
echo Step 4: Refreshing feeds to get articles
echo ============================================
python -m src.main --refresh
echo.
echo.

echo ============================================
echo Step 5: Showing recent articles
echo ============================================
python -m src.main --list-articles 5
echo.
echo.

echo ============================================
echo Test complete!
echo.
echo Next steps:
echo - To summarize an article: python -m src.main --summarize [article_id]
echo - To add more feeds: python -m src.main --add-feed [url]
echo - To export feeds: python -m src.main --export feeds.opml
echo ============================================
pause
