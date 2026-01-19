# Step-by-Step Guide to Run SpeedyReader (Python)

## ✅ Prerequisites Checklist

Before starting, you need:
- [ ] Python 3.10 or higher installed
- [ ] Internet connection
- [ ] (Optional) Claude API key for AI summaries

---

## Step 1: Install Python

### Check if Python is already installed:

Open Command Prompt or PowerShell and type:
```bash
python --version
```

**If you see a version number (3.10+):** Great! Skip to Step 2.

**If you get an error:** Install Python:

1. Go to https://www.python.org/downloads/
2. Download Python 3.12 (or latest)
3. **IMPORTANT:** During installation, check ✅ "Add Python to PATH"
4. Click "Install Now"
5. **Restart your terminal** after installation

---

## Step 2: Navigate to the Python Directory

Open Command Prompt or PowerShell:

```bash
cd "C:\Users\Jim\Documents\AI Programming\A-RSS-Reader\python"
```

---

## Step 3: Install Required Packages

Run this command:

```bash
pip install -r requirements.txt
```

This will install:
- aiohttp
- aiosqlite
- feedparser
- html2text
- tomli/tomli-w

**Wait for it to complete** (should take 30-60 seconds).

---

## Step 4: Test the Installation

Run:

```bash
python -m src.main
```

You should see a help message with available commands. If you do, **installation is successful!** ✅

---

## Step 5: Add Your First Feed

Let's add Hacker News RSS:

```bash
python -m src.main --add-feed https://hnrss.org/newest
```

This will:
- Discover the feed
- Add it to the database
- Fetch initial articles

---

## Step 6: List Your Feeds

```bash
python -m src.main --list-feeds
```

You should see your Hacker News feed listed.

---

## Step 7: Refresh to Get Latest Articles

```bash
python -m src.main --refresh
```

This fetches new articles from all your feeds.

---

## Step 8: View Articles

```bash
python -m src.main --list-articles 10
```

This shows the 10 most recent articles with their IDs.

---

## Step 9: Generate AI Summary (Optional)

**Note:** This requires a Claude API key.

### Set up API key:

1. Create a file at: `C:\Users\Jim\AppData\Roaming\speedy-reader\config.toml`
2. Add this line (replace with your actual key):
   ```toml
   claude_api_key = "sk-ant-your-key-here"
   ```

### Generate summary:

```bash
python -m src.main --summarize 1
```

(Replace `1` with an actual article ID from Step 8)

---

## Common Commands Reference

### Feed Management
```bash
# Add a feed
python -m src.main --add-feed https://example.com/feed.xml

# List all feeds
python -m src.main --list-feeds

# Refresh all feeds
python -m src.main --refresh
```

### Article Management
```bash
# List recent articles
python -m src.main --list-articles 20

# Generate summary for article
python -m src.main --summarize [article_id]
```

### OPML Import/Export
```bash
# Import feeds from OPML file
python -m src.main --import feeds.opml

# Export feeds to OPML file
python -m src.main --export my-feeds.opml
```

---

## Quick Test Script

I've created a batch file that runs through all the basic commands automatically.

Just double-click: **test_run.bat**

Or run from command line:
```bash
test_run.bat
```

---

## Troubleshooting

### "python: command not found"
- Python is not installed or not in PATH
- Reinstall Python and check ✅ "Add Python to PATH"
- Restart your terminal

### "No module named 'aiohttp'" (or similar)
- Dependencies not installed
- Run: `pip install -r requirements.txt`

### "Failed to add feed"
- Check your internet connection
- Verify the feed URL is valid
- Some feeds may be temporarily unavailable

### "No Claude API key configured"
- This is normal if you haven't set up the API key
- AI summaries require a Claude API key
- Feed management works without it

---

## What's Next?

1. **Add more feeds:**
   ```bash
   python -m src.main --add-feed https://feeds.arstechnica.com/arstechnica/index
   python -m src.main --add-feed https://xkcd.com/rss.xml
   ```

2. **Set up automatic refresh:**
   - Create a scheduled task (Windows) to run `python -m src.main --refresh` hourly

3. **Get Claude API key:**
   - Visit: https://console.anthropic.com/
   - Sign up and get an API key
   - Add to config file for AI summaries

4. **Import your existing feeds:**
   - If you have an OPML file from another RSS reader:
     ```bash
     python -m src.main --import your-feeds.opml
     ```

---

## Need More Help?

- See **README_PYTHON.md** for full documentation
- See **QUICKSTART.md** for quick reference
- See **CONVERSION_NOTES.md** for technical details

---

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Add some feeds
python -m src.main --add-feed https://hnrss.org/newest
python -m src.main --add-feed https://xkcd.com/rss.xml

# 2. Refresh to get articles
python -m src.main --refresh

# 3. List articles and note their IDs
python -m src.main --list-articles 10

# 4. Generate summary for article ID 3
python -m src.main --summarize 3

# 5. Export your feeds for backup
python -m src.main --export my-feeds.opml
```

Enjoy your RSS reader! 🎉
