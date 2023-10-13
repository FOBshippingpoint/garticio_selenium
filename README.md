# Gartic.io Selenium Printer

![GitHub contributors](https://img.shields.io/github/contributors/FOBshippingpoint/garticio_selenium?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/FOBshippingpoint/garticio_selenium?color=blue&style=for-the-badge)

[中文說明](https://github.com/FOBshippingpoint/garticio_selenium/blob/main/README_zh-TW.md)

<!-- ![Jupyter](https://img.shields.io/badge/Made%20with-Jupyter%20Notebook-F37626?logo=Jupyter&style=for-the-badge) -->

<!-- ![garticio\_selenium](https://socialify.git.ci/FOBshippingpoint/garticio_selenium/image?description=1&descriptionEditable=A%20Jupyter%20Notebook%20gartic.io%20drawing%20assistant.&font=Source%20Code%20Pro&language=1&logo=https%3A%2F%2Fgartic.io%2Fstatic%2Fdownload%2Fcharacter.png&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Dark) -->

![screenshot1](https://i.imgur.com/Ets3Iwa.png)
![screenshot2](https://i.imgur.com/8YC48H4.png)
![gif](./demo.gif)

A gartic.io drawing assistant desktop app.

## Usage

Download [latest program](https://github.com/FOBshippingpoint/garticio_selenium/releases/latest).

When it is your turn, the program will open a Google image search page with the specified keyword. You can then select the image you want to draw, and the program will start drawing it (more accurately, printing it).


## Prerequisite

[poetry](https://python-poetry.org/)

## Develop

```sh
git clone https://github.com/FOBshippingpoint/garticio_selenium.git garticio_selenium
cd garticio_selenium
poetry init
poetry install
poetry run python garticio_selenium/app.py
```

## Build

```sh
poetry run python build.py
```

## Authors

- [@FOBshippingpoint](https://www.github.com/FOBshippingpoint)
- [@Felian 1999](https://github.com/Felian1999)
- [@Elmer Chou](https://github.com/elmerchou)

## License

[MIT](https://choosealicense.com/licenses/mit/)
