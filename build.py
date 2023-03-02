import subprocess

subprocess.run(
    ["pyinstaller", "--add-data", "uBlock-Origin.crx;.", "--noconsole", "-p", "garticio_selenium", "garticio_selenium/app.py"]
)
