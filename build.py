import subprocess

# the first run would failed (cannot open)
subprocess.run(
    [
        "pyinstaller",
        "--add-data",
        "uBlock-Origin.crx;.",
        "--add-data",
        "settings.toml;.",
        "--noconsole",
        "-p",
        "garticio_selenium",
        "garticio_selenium/app.py",
    ]
)

# add this line in app.spec COLLECT
# Tree('locale', prefix='locale', typecode='EXTENSION'),
# and run pyinstaller app.spec
