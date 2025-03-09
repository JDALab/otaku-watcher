from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Optional, Dict

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

import json
import re
from urllib.parse import quote_plus

from mov_cli.utils import EpisodeSelector
from mov_cli import Scraper, Multi, Single, Metadata, MetadataType

__all__ = ("AnimePaheScraper",)

class AnimePaheScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient, options: Optional[ScraperOptionsT] = None) -> None:
        self.base_url = "https://animepahe.ru"
        self.api_url = f"{self.base_url}/api"
        self.search_url = f"{self.api_url}?m=search&q="
        self.release_url = f"{self.api_url}?m=release&id="
        self.play_url = f"{self.base_url}/play"
        env_config = config.get_env_config()
        http_client.headers = {"Referer": self.base_url, "Cookie": env_config("DDG2")}
        super().__init__(config, http_client, options)

    def _request(self, url: str, params: Optional[Dict] = None) -> Dict:
        response = self.http_client.get(url, params=params)
        return json.loads(response.text)

    def _request_html(self, url: str, params: Optional[Dict] = None) -> str:
        response = self.http_client.get(url, params=params)
        return response.text

    def search(self, query: str, limit: int = None) -> Iterable[Metadata]:
        response = self._request(f"{self.search_url}{quote_plus(query)}")
        animes = response.get("data", [])
        if limit is not None: animes = animes[:limit]
        for anime in animes:
            yield Metadata(
                id=anime["session"],
                title=anime["title"],
                type=MetadataType.MULTI if anime["episodes"] > 1 else MetadataType.SINGLE,
            )

    def scrape_episodes(self, metadata: Metadata) -> Dict[int | None, int]:
        response = self._request(f"{self.release_url}{metadata.id}&sort=episode_asc&page=1")
        if not response.get("data"): return {}
        get_all_eps = self._request_html(f"{self.play_url}/{metadata.id}/{response['data'][0]['session']}")

        soup = self.soup(get_all_eps)
        items = soup.find("div", {"class": "clusterize-scroll"}).findAll("a")
        urls = [items[i].get("href") for i in range(len(items))]

        episode_map = {}
        episode_map[1] = len(urls) # [season] = episodes
        if not episode_map: return {None: 1}
        return episode_map

    def parse_m3u8_link(self, text) -> str:
        '''
        parse m3u8 link using javascript's packed function implementation
        '''
        x = r"\}\('(.*)'\)*,*(\d+)*,*(\d+)*,*'((?:[^'\\]|\\.)*)'\.split\('\|'\)*,*(\d+)*,*(\{\})"
        try:
            p, a, c, k, e, d = re.findall(x, text)[0]
            p, a, c, k, e, d = p, int(a), int(c), k.split('|'), int(e), {}
        except Exception as e:
            raise Exception('m3u8 link extraction failed. Unable to extract packed args')

        def e(c):
            x = '' if c < a else e(int(c/a))
            c = c % a
            return x + (chr(c + 29) if c > 35 else '0123456789abcdefghijklmnopqrstuvwxyz'[c])

        for i in range(c): d[e(i)] = k[i] or e(i)
        parsed_js_code = re.sub(r'\b(\w+)\b', lambda e: d.get(e.group(0)) or e.group(0), p)
        regex_extract = lambda rgx, txt, grp: re.search(rgx, txt).group(grp) if re.search(rgx, txt) else False
        parsed_link = regex_extract('http.*.m3u8', parsed_js_code, 0)
        if not parsed_link: raise Exception('m3u8 link extraction failed. link not found')
        return parsed_link

    def scrape(self, metadata: Metadata, episode: EpisodeSelector) -> Multi | Single:
        response = self._request(f"{self.release_url}{metadata.id}&sort=episode_asc&page=1")
        if not response.get("data"): return {}
        get_all_eps = self._request_html(f"{self.play_url}/{metadata.id}/{response['data'][0]['session']}")

        soup = self.soup(get_all_eps)
        items = soup.find("div", {"class": "clusterize-scroll"}).findAll("a")
        urls = [items[i].get("href") for i in range(len(items))]

        target_episode = None
        if metadata.type == MetadataType.MULTI:
            target_episode = urls[episode.episode-1] if episode and episode.episode else urls[0]
        elif urls:
            target_episode = urls[0]
        episode_page_url = f"{self.base_url}{target_episode}"
        episode_page_html = self._request_html(episode_page_url)

        soup = self.soup(episode_page_html)
        embed_sources = soup.find("div", {"id": "resolutionMenu"}).findAll("button", {"class": "active"}) # TODO: Add quality selection
        embed_url = embed_sources[0].get("data-src")
        embed_html = self._request_html(embed_url)
        video_url = self.parse_m3u8_link(embed_html)

        if metadata.type == MetadataType.MULTI:
            return Multi(
                url=video_url,
                title=f"{metadata.title} - Episode {episode.episode}",
                episode=episode
            )
        else:
            return Single(
                url=video_url,
                title=metadata.title
            )