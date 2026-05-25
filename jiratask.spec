# -*- mode: python ; coding: utf-8 -*-
import os
import PySide6

pyside6_dir = os.path.dirname(PySide6.__file__)

excludes = [
    'tkinter', 'unittest', 'test', 'tests', 'setuptools', 'pip', 'wheel',
    'distutils', 'lib2to3', 'xmlrpc', 'pydoc', 'doctest', 'asyncio',
    'multiprocessing', 'concurrent', 'html', 'xml', 'pydoc_data',
    'curses', 'idlelib', 'turtledemo', 'IPython', 'notebook', 'numpy',
    'pandas', 'matplotlib', 'scipy', 'PIL', 'cv2', 'sqlalchemy',
    'PySide6.QtWebEngine', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineCore',
    'PySide6.QtNetwork', 'PySide6.QtSql', 'PySide6.QtXml', 'PySide6.QtBluetooth',
    'PySide6.QtNfc', 'PySide6.QtPositioning', 'PySide6.QtLocation',
    'PySide6.QtSensors', 'PySide6.QtSerialPort', 'PySide6.QtMultimedia',
    'PySide6.QtMultimediaWidgets', 'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets',
    'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuickWidgets',
    'PySide6.QtTest', 'PySide6.QtAxContainer', 'PySide6.QtDesigner',
    'PySide6.QtHelp', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
    'PySide6.QtPrintSupport', 'PySide6.QtSpatialAudio', 'PySide6.QtTextToSpeech',
    'PySide6.QtSvg', 'PySide6.QtSvgWidgets', 'PySide6.QtCharts',
    'PySide6.Qt3D', 'PySide6.QtDataVisualization',
    'PyQt5', 'PyQt6', 'PySide2',
    'jira', 'oauthlib', 'requests',
    'defusedxml', 'pytz', 'pkg_resources',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,
)

# Remove unnecessary Qt binaries/plugins
def _filter_binaries(binaries):
    skip_patterns = [
        'Qt6WebEngine', 'Qt6Network', 'Qt6Sql', 'Qt6Xml', 'Qt6Bluetooth',
        'Qt6Nfc', 'Qt6Positioning', 'Qt6Location', 'Qt6Sensors',
        'Qt6SerialPort', 'Qt6Multimedia', 'Qt6OpenGL', 'Qt6Qml', 'Qt6Quick',
        'Qt6Test', 'Qt6AxContainer', 'Qt6Designer', 'Qt6Help', 'Qt6Pdf',
        'Qt6PrintSupport', 'Qt6SpatialAudio', 'Qt6TextToSpeech',
        'Qt6Svg', 'Qt6Charts', 'Qt63D', 'Qt6DataVisualization',
        'qt6/webengine', 'qt6/network', 'qt6/sql', 'qt6/xml',
    ]
    filtered = []
    for name, path, type_ in binaries:
        skip = False
        name_lower = name.lower()
        for pat in skip_patterns:
            if pat.lower() in name_lower or pat.lower() in path.lower():
                skip = True
                break
        if not skip:
            filtered.append((name, path, type_))
    return filtered

def _filter_datas(datas):
    skip_patterns = [
        'Qt6WebEngine', 'qt6/webengine', 'Qt6Network', 'Qt6Sql',
        'translations/qtwebengine', 'translations/qtmultimedia',
        'translations/qtlocation', 'translations/qtbluetooth',
    ]
    filtered = []
    for name, path, type_ in datas:
        skip = False
        for pat in skip_patterns:
            if pat.lower() in name.lower() or pat.lower() in path.lower():
                skip = True
                break
        if not skip:
            filtered.append((name, path, type_))
    return filtered

a.binaries = _filter_binaries(a.binaries)
a.datas = _filter_datas(a.datas)

a.binaries = [b for b in a.binaries if 'opengl32sw' not in b[0].lower()]
a.binaries = [b for b in a.binaries if 'qt6virtualkeyboard' not in b[0].lower()]
a.binaries = [b for b in a.binaries if 'qgif' not in b[0].lower() and 'qico' not in b[0].lower() and 'qsvg' not in b[0].lower() and 'qtga' not in b[0].lower() and 'qtiff' not in b[0].lower() and 'qwbmp' not in b[0].lower()]
a.binaries = [b for b in a.binaries if 'qdirect2d' not in b[0].lower()]
a.datas = [d for d in a.datas if 'translations' not in d[0].lower() and 'translations' not in d[1].lower()]
a.binaries = [b for b in a.binaries if 'qwebp' not in b[0].lower() and 'qjpeg' not in b[0].lower() and 'qpdf' not in b[0].lower()]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='JiraTask',
    debug=False,
    bootloader_ignore_signals=True,
    strip=False,
    upx=True,
    upx_dir=r'C:\Users\YUAN~1.ZHO\AppData\Local\Temp\kilo',
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
