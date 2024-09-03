from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Iterable

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

    from bs4 import Tag

from thefuzz import fuzz

from mov_cli import Cache, Scraper
from mov_cli.utils import EpisodeSelector, what_platform
from mov_cli import Single, Multi, Metadata, MetadataType

__all__ = ("TokyoInsider",)

BASE_URL = "https://www.tokyoinsider.com"

class TokyoInsider(Scraper):
    def __init__(
        self,
        config: Config,
        http_client: HTTPClient,
        options: Optional[ScraperOptionsT] = None
    ) -> None:
        super().__init__(config, http_client, options)

        self.__anime_list: Optional[List[Tuple[str, str]]] = None

    def search(self, query: str, limit: Optional[int] = None) -> Iterable[Metadata]:
        limit = limit or 35
        anime_list = self.__get_anime_list()

        search_results: List[Tuple[int, Metadata]] = []

        index = 0

        for (name, url) in anime_list:

            if index == limit:
                break

            name_match = fuzz.partial_ratio(name.lower(), query.lower())

            if name_match > 70:
                metadata = Metadata(
                    id = url,
                    title = name,
                    type = MetadataType.MULTI # TODO: Handle anime films and stuff.
                )

                search_results.append(
                    (name_match, metadata)
                )

                index += 1

        search_results.sort(key = lambda x: x[0], reverse = True)
        return [x[1] for x in search_results]

    def scrape(self, metadata: Metadata, episode: EpisodeSelector) -> Optional[Multi | Single]:
        return super().scrape(metadata, episode)

    def __get_anime_list(self) -> List[Tuple[str, str]]:

        if self.__anime_list is not None:
            return self.__anime_list

        cache = Cache(what_platform())
        anime_list_cached = cache.get_cache("tokyo_insider_anime_list")

        if anime_list_cached is not None:
            return anime_list_cached

        list_of_anime_entries: List[Tuple[str, str]] = []

        response = self.http_client.request("GET", url = BASE_URL + "/anime/list")
        soup = self.soup(response.text)

        all_anime_entry_div_tags: List[Tag] = soup.find_all("div", {"class": "c_h2"}) + soup.find_all("div", {"class": "c_h2b"})

        for anime_entry_div_tag in all_anime_entry_div_tags:
            anime_entry_a_tag = anime_entry_div_tag.find("a")

            if anime_entry_a_tag is None:
                continue

            list_of_anime_entries.append(
                (anime_entry_a_tag.text, anime_entry_a_tag["href"])
            )

        self.__anime_list = cache.set_cache(
            id = "tokyo_insider_anime_list", 
            value = list_of_anime_entries, 
            seconds_until_expired = 86400 # 24 hours
        )

        return list_of_anime_entries