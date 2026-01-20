"""Main TUI application using Textual."""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label
from textual.binding import Binding
from textual.reactive import reactive
from rich.markup import escape
from rich.text import Text

from ..config import Config
from ..app import App as BackendApp
from ..models import Article


class ArticleList(ListView):
    """Widget displaying the list of articles."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.articles = []

    def set_articles(self, articles):
        """Update the article list."""
        self.articles = articles
        self.clear()
        for article in articles:
            date_str = article.published_at.strftime("%m-%d") if article.published_at else "??-??"
            feed_name = (article.feed_title or "Unknown")[:20]
            title = article.title[:60]
            label = f"T {date_str} {feed_name}\n    {title}"
            self.append(ListItem(Label(label)))


class ArticleHeader(Static):
    """Widget displaying article title and source."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article_title = ""
        self.feed_name = ""

    def update_article(self, title: str, feed: str):
        """Update the article information and refresh display."""
        self.article_title = title or "No Title"
        self.feed_name = feed or "Unknown Source"
        self.refresh()

    def render(self) -> str:
        """Render the article header."""
        if not self.article_title:
            return "[dim]No article selected[/dim]"

        # Build content line by line
        lines = []
        lines.append("[bold cyan]- Article -[/bold cyan]")
        lines.append("[yellow]Source:[/yellow] " + escape(self.feed_name))
        lines.append("[bold]" + escape(self.article_title) + "[/bold]")

        return "\n".join(lines)


class FeedContent(Static):
    """Widget displaying scrollable feed content."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article_content = ""

    def update_content(self, content: str):
        """Update the content and refresh display."""
        self.article_content = content
        self.refresh()

    def render(self) -> str:
        """Render the feed content."""
        content = f"[bold yellow]- Feed Content -[/bold yellow]\n\n"
        if self.article_content:
            content += escape(self.article_content)
        else:
            content += "[dim]No content available[/dim]"
        return content


class AISummary(Static):
    """Widget displaying AI summary."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article_summary = ""

    def update_summary(self, summary: str):
        """Update the summary and refresh display."""
        self.article_summary = summary
        self.refresh()

    def render(self) -> str:
        """Render the AI summary."""
        content = f"[bold magenta]- AI Summary -[/bold magenta]\n\n"
        if self.article_summary:
            content += escape(self.article_summary)
        else:
            content += "[dim]Press Enter to generate summary...[/dim]"
        return content


class SpeedyReaderTUI(App):
    """SpeedyReader Terminal UI Application."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    ArticleList {
        width: 30%;
        border: solid cyan;
    }

    #detail_container {
        width: 70%;
        layout: vertical;
    }

    ArticleHeader {
        height: auto;
        border: solid cyan;
        padding: 1;
    }

    #feed_content_container {
        height: 25%;
        border: solid yellow;
    }

    FeedContent {
        height: auto;
        padding: 1;
    }

    AISummary {
        height: 1fr;
        border: solid magenta;
        padding: 1;
    }

    ListView {
        background: $surface;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem > Label {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("s", "summarize", "Summarize"),
        Binding("o", "open", "Open"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.backend_app = None
        self.config = None
        self.config_override = None  # Can be set before run()
        self.clear_articles = False  # Can be set before run()
        self.current_article = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Horizontal():
            yield ArticleList(id="article_list")
            with Vertical(id="detail_container"):
                yield ArticleHeader(id="article_header")
                with VerticalScroll(id="feed_content_container"):
                    yield FeedContent(id="feed_content")
                yield AISummary(id="ai_summary")
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the application."""
        self.title = "SpeedyReader"
        self.sub_title = "RSS Reader with AI Summaries"

        # Load config and initialize backend
        # Use config_override if provided, otherwise load from file
        self.config = self.config_override if self.config_override else Config.load()
        self.backend_app = BackendApp(self.config)
        await self.backend_app.initialize(clear_articles=self.clear_articles)

        # Load articles
        article_list = self.query_one("#article_list", ArticleList)
        article_list.set_articles(self.backend_app.articles)

        # Update footer with article count and retention period
        retention_days = self.config.article_retention_days
        limit_info = f" | Limit: {self.config.articles_per_feed}/feed" if self.config.articles_per_feed else ""
        self.sub_title = f"{len(self.backend_app.articles)} Articles | Range: {retention_days} days{limit_info}"

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle article selection (Enter key)."""
        article_list = self.query_one("#article_list", ArticleList)
        if event.list_view.index < len(article_list.articles):
            self.current_article = article_list.articles[event.list_view.index]
            await self.update_article_detail()

    async def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle article highlight change (cursor movement)."""
        article_list = self.query_one("#article_list", ArticleList)
        if event.list_view.index is not None and event.list_view.index < len(article_list.articles):
            self.current_article = article_list.articles[event.list_view.index]
            await self.update_article_detail()

    async def update_article_detail(self) -> None:
        """Update the article detail pane."""
        if not self.current_article:
            return

        # Update header
        header = self.query_one("#article_header", ArticleHeader)
        header.update_article(
            self.current_article.title,
            self.current_article.feed_title or "Unknown"
        )

        # Update feed content - use content_text if available, otherwise show content (HTML)
        content_widget = self.query_one("#feed_content", FeedContent)
        if self.current_article.content_text:
            content_widget.update_content(self.current_article.content_text)
        elif self.current_article.content:
            # Convert HTML to text if we only have HTML content
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            text_content = h.handle(self.current_article.content)
            content_widget.update_content(text_content)
        else:
            content_widget.update_content("")

        # Update AI summary
        summary_widget = self.query_one("#ai_summary", AISummary)
        summary = await self.backend_app.repository.get_summary(self.current_article.id)
        if summary:
            summary_widget.update_summary(summary.content)
        else:
            summary_widget.update_summary("")

    async def action_refresh(self) -> None:
        """Refresh all feeds."""
        self.sub_title = "Refreshing feeds..."
        await self.backend_app.refresh_feeds(limit_per_feed=self.config.articles_per_feed)

        # Reload article list
        article_list = self.query_one("#article_list", ArticleList)
        article_list.set_articles(self.backend_app.articles)

        # Update footer with article count and retention period
        retention_days = self.config.article_retention_days
        limit_info = f" | Limit: {self.config.articles_per_feed}/feed" if self.config.articles_per_feed else ""
        self.sub_title = f"{len(self.backend_app.articles)} Articles | Range: {retention_days} days{limit_info}"

    async def action_summarize(self) -> None:
        """Generate AI summary for current article."""
        if not self.current_article:
            return

        summary_widget = self.query_one("#ai_summary", AISummary)
        summary_widget.update_summary("[dim]Generating summary...[/dim]")

        summary = await self.backend_app.generate_summary(self.current_article)
        if summary:
            summary_widget.update_summary(summary.content)
        else:
            summary_widget.update_summary("[red]Failed to generate summary[/red]")

    def action_open(self) -> None:
        """Open current article in browser."""
        if self.current_article:
            import webbrowser
            webbrowser.open(self.current_article.url)

    def action_cursor_down(self) -> None:
        """Move cursor down in article list."""
        article_list = self.query_one("#article_list", ArticleList)
        article_list.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in article list."""
        article_list = self.query_one("#article_list", ArticleList)
        article_list.action_cursor_up()

    def action_help(self) -> None:
        """Show help screen."""
        self.push_screen("help")

    async def on_unmount(self) -> None:
        """Cleanup when closing."""
        if self.backend_app:
            await self.backend_app.close()


def run_tui():
    """Run the TUI application."""
    app = SpeedyReaderTUI()
    app.run()
