# Gartic.io Selenium Printer
![GitHub contributors](https://img.shields.io/github/contributors/FOBshippingpoint/garticio_selenium?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/FOBshippingpoint/garticio_selenium?color=blue&style=for-the-badge)
![Jupyter](https://img.shields.io/badge/Made%20with-Jupyter%20Notebook-F37626?logo=Jupyter&style=for-the-badge)

![garticio_selenium](https://socialify.git.ci/FOBshippingpoint/garticio_selenium/image?description=1&descriptionEditable=A%20Jupyter%20Notebook%20gartic.io%20drawing%20assistant.&font=Source%20Code%20Pro&language=1&logo=https%3A%2F%2Fgartic.io%2Fstatic%2Fdownload%2Fcharacter.png&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Dark)

A Jupyter Notebook gartic.io drawing assistant.

## Usage

Initialize project

```sh
git clone https://github.com/FOBshippingpoint/garticio_selenium.git garticio_selenium
cd garticio_selenium
python -m venv venv --prompt="garticio_selenium" # Create virtual environment
venv\Scripts\Activate.ps1 # Activate virtual environment
pip install -r requirements.txt # Install requirements
```

Open main.ipynb

1. run first cell: initialize functions
2. run second cell: open webdriver
3. start playing gartic.io
4. when you are drawer, run third cell: search images of answer
5. click the image you want to draw
6. run fourth cell: save target image
7. run fifth cell and change your window to the browser in three seconds: start drawing

## Authors

- [@FOBshippingpoint](https://www.github.com/FOBshippingpoint)
- [@Felian 1999](https://github.com/Felian1999)
- [@Elmer Chou](https://github.com/elmerchou)

## License

[MIT](https://choosealicense.com/licenses/mit/)
