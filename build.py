"""
Build script for JiraTask - creates a minimal exe using Nuitka.
Usage: python build.py
"""
import subprocess
import sys
import os

# Nuitka command for minimal exe
cmd = [
    sys.executable, "-m", "nuitka",
    "--onefile",
    "--enable-plugin=pyside6",
    "--output-filename=JiraTask.exe",
    "--output-dir=dist",
    "--assume-yes-for-downloads",
    "--remove-output",
    "--follow-imports",
    # Optimize for size
    "--python-flag=no_site",
    "--python-flag=no_warnings",
    "--python-flag=no_docstrings",
    # Disable unnecessary modules
    "--nofollow-import-to=tkinter",
    "--nofollow-import-to=unittest",
    "--nofollow-import-to=test",
    "--nofollow-import-to=tests",
    "--nofollow-import-to=setuptools",
    "--nofollow-import-to=pip",
    "--nofollow-import-to=wheel",
    "--nofollow-import-to=distutils",
    "--nofollow-import-to=lib2to3",
    "--nofollow-import-to=xmlrpc",
    "--nofollow-import-to=pydoc",
    "--nofollow-import-to=doctest",
    "--nofollow-import-to=asyncio",
    "--nofollow-import-to=multiprocessing",
    "--nofollow-import-to=concurrent",
    "--nofollow-import-to=html",
    "--nofollow-import-to=xml",
    "--nofollow-import-to=pydoc_data",
    "--nofollow-import-to=curses",
    "--nofollow-import-to=idlelib",
    "--nofollow-import-to=turtledemo",
    # Disable unnecessary Qt modules
    "--nofollow-import-to=PySide6.QtWebEngine",
    "--nofollow-import-to=PySide6.QtWebEngineWidgets",
    "--nofollow-import-to=PySide6.QtWebEngineCore",
    "--nofollow-import-to=PySide6.QtNetwork",
    "--nofollow-import-to=PySide6.QtSql",
    "--nofollow-import-to=PySide6.QtXml",
    "--nofollow-import-to=PySide6.QtBluetooth",
    "--nofollow-import-to=PySide6.QtNfc",
    "--nofollow-import-to=PySide6.QtPositioning",
    "--nofollow-import-to=PySide6.QtLocation",
    "--nofollow-import-to=PySide6.QtSensors",
    "--nofollow-import-to=PySide6.QtSerialPort",
    "--nofollow-import-to=PySide6.QtMultimedia",
    "--nofollow-import-to=PySide6.QtMultimediaWidgets",
    "--nofollow-import-to=PySide6.QtOpenGL",
    "--nofollow-import-to=PySide6.QtOpenGLWidgets",
    "--nofollow-import-to=PySide6.QtQml",
    "--nofollow-import-to=PySide6.QtQuick",
    "--nofollow-import-to=PySide6.QtQuickWidgets",
    "--nofollow-import-to=PySide6.QtTest",
    "--nofollow-import-to=PySide6.QtAxContainer",
    "--nofollow-import-to=PySide6.QtDesigner",
    "--nofollow-import-to=PySide6.QtHelp",
    "--nofollow-import-to=PySide6.QtPdf",
    "--nofollow-import-to=PySide6.QtPdfWidgets",
    "--nofollow-import-to=PySide6.QtPrintSupport",
    "--nofollow-import-to=PySide6.QtSpatialAudio",
    "--nofollow-import-to=PySide6.QtTextToSpeech",
    # Disable Qt plugins we don't need
    "--nofollow-import-to=PySide6.QtSvg",
    "--nofollow-import-to=PySide6.QtSvgWidgets",
    "--nofollow-import-to=PySide6.QtCharts",
    "--nofollow-import-to=PySide6.Qt3D",
    "--nofollow-import-to=PySide6.QtDataVisualization",
    # Include our data files
    "--include-data-files=config.json=config.json",
    "--windows-console-mode=disable",
    # Main entry point
    "main.py",
]

print("Building JiraTask.exe with Nuitka...")
print("This may take several minutes on first run.\n")
result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
sys.exit(result.returncode)
