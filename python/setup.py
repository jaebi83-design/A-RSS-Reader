"""Setup script for SpeedyReader Python version."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent.parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="speedy-reader",
    version="1.0.0",
    description="A TUI RSS reader with AI-powered summaries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Converted from Rust to Python",
    url="https://github.com/leolaporte/rss-reader",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
        "aiosqlite>=0.19.0",
        "feedparser>=6.0.0",
        "html2text>=2024.2.26",
        "tomli>=2.0.0; python_version < '3.11'",
        "tomli-w>=1.0.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "speedy-reader=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
    ],
)
