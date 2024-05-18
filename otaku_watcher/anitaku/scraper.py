from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Dict, Generator, Any

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient
    from mov_cli.scraper import ScraperOptionsT

import re

from mov_cli import utils
from mov_cli.scraper import Scraper
from mov_cli import Single, Multi, Metadata, MetadataType
from mov_cli import ExtraMetadata

__all__ = ("AnitakuScraper",)

class AnitakuScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient, options: Optional[ScraperOptionsT] = None) -> None:
        self.base_url = "https://anitaku.so"
        super().__init__(config, http_client, options)

    def search(self, query: str, limit: int = 20) -> List[Metadata]:
        query = query.replace(' ', '-')
        results = self.__results(query, limit)
        return results

    def scrape(self, metadata: Metadata, episode: utils.EpisodeSelector) -> Multi | Single:
        req = self.http_client.get(self.base_url + f"/{metadata.id}-episode-{episode.episode}", redirect = True)
        soup = self.soup(req)

        streamwish = soup.find("li", {"class": "streamwish"})
        dood = soup.find("li", {"class": "doodstream"})

        if streamwish:
            url = self.__streamwish(streamwish.find("a")["data-video"])
        elif dood:
            url = self.__dood(dood.find("a")["data-video"])

        if metadata.type == MetadataType.MOVIE:
            return Single(
                url,
                title = metadata.title,
                referrer = self.base_url,
                year = metadata.year,
                subtitles = None
            )

        return Multi(
            url,
            title = metadata.title,
            referrer = self.base_url,
            episode = episode,
            subtitles = None
        )

    def scrape_episodes(self, metadata: Metadata) -> Dict[int, int]:
        page = self.http_client.get(f"{self.base_url}/category/{metadata.id}")
        _soup = self.soup(page)

        episode_page = _soup.find("ul", {"id": "episode_page"})
        li = episode_page.findAll("li")
        last = int(li[-1].find("a")["ep_end"])
        return {1: last} # TODO: Return multiple seasons.

    def __results(self, query: str, limit: int) -> Generator[Metadata, Any, None]:
        pagination = 1
        result_count = 0

        while True:
            req = self.http_client.get(f"{self.base_url}/search.html?keyword={query}&page={pagination}")
            soup = self.soup(req)
            items = soup.find("ul", {"class": "items"}).findAll("li")

            if len(items) == 0:
                break

            for item in items:
                id = item.find("a")["href"].split("/")[-1]
                title = item.find("a")["title"]
                year_text = re.findall(r"(\d{4})", item.find("p", {"class": "released"}).text)

                if year_text: # Animes without a year are not released
                    year = year_text[0]
                else:
                    continue

                page = self.http_client.get(self.base_url + f"/category/{id}")
                _soup = self.soup(page)

                episode_page = _soup.find("ul", {"id": "episode_page"})
                li = episode_page.findAll("li")
                last = li[-1].find("a")["ep_end"]

                if last == "1":
                    type = MetadataType.MOVIE
                else:
                    type = MetadataType.SERIES

                info_body = _soup.find("div", {"class": "anime_info_body_bg"})

                _p = info_body.findAll("p")

                genres = _p[3].findAll("a")

                yield Metadata(
                    id = id,
                    title = title,
                    type = type,
                    year = year,

                    extra_func = lambda: ExtraMetadata(
                        description = [str.strip(x) for x in _p[2].strings if str.strip(x) != ''][1].replace(r"\r\n", "\r\n"),
                        image_url = item.find("img")["src"],
                        alternate_titles = [],
                        cast = None,
                        genres = [i.text.split(" ")[-1] for i in genres]
                    )
                )

                result_count += 1

                if result_count >= limit:
                    return None

            pagination += 1

    def __dood(self, url):
        video_id = url.split("/")[-1]
        webpage_html = self.http_client.get(
            f"https://dood.to/e/{video_id}", redirect = True
        )
        webpage_html = webpage_html.text

        try:
            pass_md5 = re.search(r"/pass_md5/[^']*", webpage_html).group()
        except Exception as e:
            self.logger.error(e)
            return None

        urlh = f"https://dood.to{pass_md5}"
        res = self.http_client.get(urlh, headers = {"referer": "https://dood.to"}).text
        md5 = pass_md5.split("/")
        true_url = res + "MovCli3oPi?token=" + md5[-1]

        return true_url

    def __streamwish(self, url):
        req = self.http_client.get(url).text
        file = re.findall(r'file:"(.*?)"', req)[0]

        return file