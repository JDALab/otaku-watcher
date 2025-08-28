<div align="center">

  # otaku-watcher-contrib
  <img src="https://gdjkhp.github.io/img/kagura-merge-avatar.gif" width=64>

  <sub>A mov-cli plugin for watching anime and more!</sub>

  [![](https://img.shields.io/pypi/v/otaku-watcher-contrib)](https://pypi.org/project/otaku-watcher-contrib)
  ![](https://img.shields.io/pypi/dm/otaku-watcher-contrib)
  [![](https://img.shields.io/github/created-at/GDjkhp/otaku-watcher-contrib)](https://github.com/GDjkhp/otaku-watcher-contrib)
  ![](https://img.shields.io/github/license/GDjkhp/otaku-watcher-contrib)

  <img src="https://gdjkhp.github.io/img/gintama.png">
</div>

## ⛑️ Support
| Scraper | Status | Films | TV | Mobile support |
| ------- | ------ | --- | --- | ---------------------- |
| [`animepahe`](https://animepahe.ru) | 🔵 Experimental | ✅ | ✅  | ❓ |
| [`kisskh`](https://kisskh.id) | 🔵 Experimental | ✅ | ✅  | ❓ |

## Installation
Here's how to install and add the plugin to mov-cli.

1. Install the pip package.
```sh
pip install otaku-watcher-contrib
```
2. Then add the plugin to your mov-cli config.
```sh
mov-cli -e
```
```toml
[mov-cli.plugins]
anime = "otaku-watcher-contrib"
```
## Usage
```sh
mov-cli gintama
```