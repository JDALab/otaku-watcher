from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Optional, Dict

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

import json
from urllib.parse import quote_plus

from mov_cli.utils import EpisodeSelector
from mov_cli import Scraper, Multi, Single, Metadata, MetadataType

__all__ = ("HiAnimeScraper",)

class HiAnimeScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient, options: Optional[ScraperOptionsT] = None) -> None:
        self.base_url = "https://aniwatch-api-7ehn.onrender.com/api/v2/hianime"
        self.search_url = f"{self.base_url}/search"
        self.anime_url = f"{self.base_url}/anime"
        self.episode_url = f"{self.base_url}/episode/sources"
        super().__init__(config, http_client, options)

    def _request(self, url: str, params: Optional[Dict] = None) -> Dict:
        response = self.http_client.get(url, params=params)
        return json.loads(response.text)

    def search(self, query: str, limit: int = None) -> Iterable[Metadata]:
        response = self._request(f"{self.search_url}?q={quote_plus(query)}")
        animes = response["data"]["animes"]
        if limit is not None: animes = animes[:limit]
        for anime in animes:
            yield Metadata(
                id=anime["id"],
                title=anime["name"],
                type=MetadataType.MULTI if anime["episodes"]["sub"] > 1 else MetadataType.SINGLE,
            )

    def scrape_episodes(self, metadata: Metadata) -> Dict[int | None, int]:
        anime_details = self._request(f"{self.anime_url}/{metadata.id}/episodes")
        episodes = anime_details["data"]["episodes"]
        episode_map = {}
        episode_map[1] = len(episodes) # [season] = episodes
        if not episode_map: return {None: 1}
        return episode_map

    def scrape(self, metadata: Metadata, episode: EpisodeSelector) -> Multi | Single:
        anime_details = self._request(f"{self.anime_url}/{metadata.id}/episodes")
        episodes = anime_details["data"]["episodes"]

        # Find the requested episode
        target_episode = None
        if metadata.type == MetadataType.MULTI:
            episode_num = episode.episode if episode and episode.episode else 1
            for ep in episodes:
                if ep["number"] == episode_num:
                    target_episode = ep
                    break
        else:
            # For a single, just grab the first episode
            if episodes:
                target_episode = episodes[0]

        sources_response = self._request(f"{self.episode_url}?animeEpisodeId={target_episode['episodeId']}")
        video_url = sources_response["data"]["sources"][0]["url"]

        subtitles = []
        if "tracks" in sources_response["data"]:
            for track in sources_response["data"]["tracks"]:
                if track["kind"] == "captions":
                    subtitles.append(track["file"])

        if metadata.type == MetadataType.MULTI:
            return Multi(
                url=video_url,
                title=f"{metadata.title} - Episode {target_episode['number']}",
                episode=episode,
                subtitles=subtitles
            )
        else:
            return Single(
                url=video_url,
                title=metadata.title,
                subtitles=subtitles
            )