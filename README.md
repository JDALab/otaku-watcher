<div align="center">

  # otaku-watcher
  <sub>A mov-cli plugin for watching anime.</sub>

  <img src="https://github.com/mov-cli/mov-cli-gogotaku/assets/132799819/1436339c-f2c3-4c37-b9ae-0da6b83faf8d">

</div>

> [!CAUTION]
> We are on the lookout for maintainers and if we don't find any soon this project may become unmaintained! Please consider or nominate a friend. Thank you.

## Installation
Here's how to install and add the plugin to mov-cli.

> [!WARNING]
> Before installing this plugin make sure ``mov-cli-anime`` is not installed to lower the risks of a conflict.
> ``pip uninstall mov-cli-anime``

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

## Usage
```sh
mov-cli -s anime lycoris recoil
```
