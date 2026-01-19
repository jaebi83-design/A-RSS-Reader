"""OPML import/export functionality."""

from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET

from ..error import OpmlParseError
from ..models import Feed, NewFeed


def parse_opml_file(path: Path) -> List[NewFeed]:
    """Parse an OPML file and return a list of feeds."""
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        feeds = []
        body = root.find("body")
        if body is not None:
            _collect_feeds(body, feeds)

        return feeds

    except ET.ParseError as e:
        raise OpmlParseError(f"Failed to parse OPML: {e}")
    except Exception as e:
        raise OpmlParseError(f"Error reading OPML file: {e}")


def _collect_feeds(element: ET.Element, feeds: List[NewFeed]):
    """Recursively collect feeds from OPML outline elements."""
    for outline in element.findall("outline"):
        xml_url = outline.get("xmlUrl")

        if xml_url:
            # This is a feed entry
            feeds.append(
                NewFeed(
                    title=outline.get("text", "Untitled"),
                    url=xml_url,
                    site_url=outline.get("htmlUrl"),
                    description=outline.get("description"),
                )
            )

        # Recursively process nested outlines (categories/folders)
        _collect_feeds(outline, feeds)


def export_opml_file(path: Path, feeds: List[Feed]):
    """Export feeds to an OPML file."""
    try:
        opml = ET.Element("opml", version="2.0")

        head = ET.SubElement(opml, "head")
        title = ET.SubElement(head, "title")
        title.text = "SpeedyReader Feeds"

        body = ET.SubElement(opml, "body")

        for feed in feeds:
            outline = ET.SubElement(
                body,
                "outline",
                text=feed.title,
                type="rss",
                xmlUrl=feed.url,
            )
            if feed.site_url:
                outline.set("htmlUrl", feed.site_url)
            if feed.description:
                outline.set("description", feed.description)

        tree = ET.ElementTree(opml)
        ET.indent(tree, space="  ", level=0)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    except Exception as e:
        raise OpmlParseError(f"Failed to export OPML: {e}")
