#!/bin/sh
#
# Run this in the virtualenv context.
# Unsure settings.json is located at the EXE folder place
# -------------------------------------------------------
#

./.venv/bin/pyinstaller dashboard.py --onefile --windowed --icon icon.png --add-data "settings.json:." --add-data "icon.png:."
