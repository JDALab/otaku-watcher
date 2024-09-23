from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Iterable, Dict, Literal

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

    from bs4 import Tag

from thefuzz import fuzz
from datetime import datetime

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
        limit = limit or 125 # recommended limit
        anime_list = self.__get_anime_list()

        search_results: List[Tuple[int, Metadata]] = []

        index = 0

        for (name, url) in anime_list:

            if index == limit:
                break

            name_match = fuzz.partial_token_sort_ratio(name.lower(), query.lower())

            if name_match > 90:
                metadata = Metadata(
                    id = url,
                    title = name,
                    type = MetadataType.MULTI if "(TV)" in name else MetadataType.SINGLE
                )

                search_results.append(
                    (name_match, metadata)
                )

                index += 1

        search_results.sort(key = lambda x: x[0], reverse = True)
        return [x[1] for x in search_results]

    def scrape(self, metadata: Metadata, episode: EpisodeSelector) -> Optional[Multi | Single]:
        if metadata.type == MetadataType.SINGLE:
            page = self.http_client.request(
                "GET",
                f"{BASE_URL}{metadata.id}/movie/1"
            )

        else:
            page = self.http_client.request(
                "GET",
                f"{BASE_URL}{metadata.id}/episode/{episode.episode}"
            )

        soup = self.soup(page)

        all_download_divs: List[Tag] = soup.find("div", {"id": "inner_page"}).find_all("div", recursive=False)[1:]

        available_downloads: List[Tuple[datetime, str]] = []

        for download_div in all_download_divs:
            if "finfo" not in str(download_div):
                continue

            streaming_url_a_tag = download_div.find_all("a")[-1]
            finfo = download_div.find("div", {"class": "finfo"})

            finfo_bold_tags: List[Tag] = finfo.find_all("b")

            date_added_string = finfo_bold_tags[-1].text

            available_downloads.append(
                (
                    datetime.strptime(date_added_string, "%m/%d/%y"), # american date format, ewww what's that brother... ewwww
                    streaming_url_a_tag["href"]
                )
            )

        available_downloads.sort(key = lambda x: x[0].timestamp(), reverse = True)

        if metadata.type == MetadataType.MULTI:
            return Multi(
                available_downloads[0][1],
                metadata.title,
                episode
            )

        return Single(
            available_downloads[0][1],
            metadata.title
        )

    def scrape_episodes(self, metadata: Metadata) -> Dict[int, int] | Dict[None, Literal[1]]:
        anime_page = self.http_client.request(
            "GET",
            BASE_URL + metadata.id
        )

        soup = self.soup(anime_page)

        return {1: len(soup.find_all("a", {"class": "download-link"}))}

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
        