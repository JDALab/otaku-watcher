<div align="center">

  # otaku-watcher
  <sub>A mov-cli plugin for watching anime.</sub>

  [![Pypi Version](https://img.shields.io/pypi/v/otaku-watcher?style=flat)](https://pypi.org/project/otaku-watcher)

  <img src="https://github.com/JDALab/otaku-watcher/assets/123201787/2df8d707-b472-48b3-aaa1-f6d5154c686d">

</div>

> [!CAUTION]
> We are on the lookout for maintainers and if we don't find any soon this project may become unmaintained! Please consider or nominate a friend. Thank you.

## ⛑️ Support
| Scraper | Status | Films | TV | Supports <br> Android & iOS | Notes |
| ------- | ------ | --- | --- | ---------------------- | :------: |
| [`anitaku`](https://anitaku.bz) | 🔴 Not working | ✅ | ✅  | ❌ | okay quality (720p) |
| [`tokyo`](https://www.tokyoinsider.com) | 🔵 Experimental | ✅ | ✅ | ✅ | **New scraper**, good quality (1080p) **for older anime** but a lot of the time absolutely trash quality for newer shows and not all streams have english dub. Give it a try for older anime though like anime before 2018. |
| [`hianime`](https://hianime.to) | 🔵 Experimental | ✅ | ✅  | ❓ | 🐐 (multi-subs and eng dubs) |
| [`animepahe`](https://animepahe.ru) | 🔵 Experimental | ✅ | ✅  | ❓ | 🐐 (hard-coded subs and eng dubs) |

## Installation
Here's how to install and add the plugin to mov-cli.

1. Install the pip package.
```sh
pip install otaku-watcher
```
2. Then add the plugin to your mov-cli config.
```sh
mov-cli -e
```
```toml
[mov-cli.plugins]
anime = "otaku-watcher"
```
3. Set `DDG2` cookie for animepahe scraper or it will not work. (optional)
```sh
mov-cli -e .env
```
```
DDG2 = "__ddg2_=<ddg2 cookie>"
```
## Usage
```sh
mov-cli -s anime lycoris recoil
```
