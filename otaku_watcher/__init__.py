from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mov_cli.plugins import PluginHookData

from .anitaku import AnitakuScraper
from .tokyo_insider import TokyoInsider

plugin: PluginHookData = {
    "version": 1,
    "package_name": "otaku-watcher",  # Required for the plugin update checker.
    "scrapers": {
        "DEFAULT": AnitakuScraper,
        "anitaku": AnitakuScraper,
        "tokyo": TokyoInsider
    }
}

__version__ = "1.2.3"