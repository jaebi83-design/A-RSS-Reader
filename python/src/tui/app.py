"""Main TUI application using Textual."""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label
from textual.binding import Binding
from textual.reactive import reactive

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


class ArticleDetail(Static):
    """Widget displaying article details and summary."""

    article_title = reactive("")
    article_content = reactive("")
    article_summary = reactive("")
    article_url = reactive("")

    def render(self) -> str:
        """Render the article detail."""
        if not self.article_title:
            return "[dim]No article selected[/dim]"

        content = f"[bold cyan]- Article -[/bold cyan]\n"
        content += f"[bold]{self.article_title}[/bold]\n\n"

        if self.article_url:
            content += f"[dim]{self.article_url}[/dim]\n\n"

        content += f"[yellow]- Feed Content -[/yellow]\n"
        if self.article_content:
            content += self.article_content[:500] + "...\n\n"
        else:
            content += "[dim]No content available[/dim]\n\n"

        content += f"[magenta]- AI Summary -[/magenta]\n"
        if self.article_summary:
            content += self.article_summary
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

    ArticleDetail {
        width: 70%;
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
        Binding("enter", "summarize", "Summarize"),
        Binding("o", "open", "Open"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.backend_app = None
        self.config = None
        self.current_article = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Horizontal():
            yield ArticleList(id="article_list")
            yield ArticleDetail(id="article_detail")
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the application."""
        self.title = "SpeedyReader"
        self.sub_title = "RSS Reader with AI Summaries"

        # Load config and initialize backend
        self.config = Config.load()
        self.backend_app = BackendApp(self.config)
        await self.backend_app.initialize()

        # Load articles
        article_list = self.query_one("#article_list", ArticleList)
        article_list.set_articles(self.backend_app.articles)

        # Update footer with article count
        self.sub_title = f"{len(self.backend_app.articles)} Articles"

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle article selection."""
        article_list = self.query_one("#article_list", ArticleList)
        if event.list_view.index < len(article_list.articles):
            self.current_article = article_list.articles[event.list_view.index]
            await self.update_article_detail()

    async def update_article_detail(self) -> None:
        """Update the article detail pane."""
        if not self.current_article:
            return

        detail = self.query_one("#article_detail", ArticleDetail)
        detail.article_title = self.current_article.title
        detail.article_url = self.current_article.url
        detail.article_content = self.current_article.content_text or ""

        # Check if summary exists
        summary = await self.backend_app.repository.get_summary(self.current_article.id)
        if summary:
            detail.article_summary = summary.content
        else:
            detail.article_summary = ""

    async def action_refresh(self) -> None:
        """Refresh all feeds."""
        self.sub_title = "Refreshing feeds..."
        await self.backend_app.refresh_feeds()

        # Reload article list
        article_list = self.query_one("#article_list", ArticleList)
        article_list.set_articles(self.backend_app.articles)
        self.sub_title = f"{len(self.backend_app.articles)} Articles"

    async def action_summarize(self) -> None:
        """Generate AI summary for current article."""
        if not self.current_article:
            return

        detail = self.query_one("#article_detail", ArticleDetail)
        detail.article_summary = "[dim]Generating summary...[/dim]"

        summary = await self.backend_app.generate_summary(self.current_article)
        if summary:
            detail.article_summary = summary.content
        else:
            detail.article_summary = "[red]Failed to generate summary[/red]"

    def action_open(self) -> None:
        """Open current article in browser."""
        if self.current_article:
            import webbrowser
            webbrowser.open(self.current_article.url)

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
