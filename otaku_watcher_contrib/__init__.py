from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mov_cli.plugins import PluginHookData

from .animepahe import AnimePaheScraper
from .kisskh import KissKhScraper

plugin: PluginHookData = {
    "version": 1,
    "package_name": "otaku-watcher-contrib",  # Required for the plugin update checker.
    "scrapers": {
        "DEFAULT": AnimePaheScraper,
        "ANDROID.DEFAULT": AnimePaheScraper,
        "animepahe": AnimePaheScraper,
        "kisskh": KissKhScraper,
    }
}

__version__ = "1.2.10"