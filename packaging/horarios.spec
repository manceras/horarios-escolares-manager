"""PyInstaller build of the desktop application.

Build from the repository root, with the web client already built:

    pnpm --dir frontend build
    uv run --project backend pyinstaller packaging/horarios.spec --noconfirm

One-directory rather than one-file: a one-file build unpacks ~200 MB to a
temporary folder on every launch, which costs seconds of startup and is the
shape antivirus heuristics dislike most. The Inno Setup script wraps the
directory into the single file the school actually downloads.
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).parent
BACKEND = ROOT / "backend"

# OR-Tools ships native libraries and data files that no static analysis finds.
ortools_datas, ortools_binaries, ortools_hiddenimports = collect_all("ortools")

datas = [
    # Alembic loads env.py and every version script by path at runtime, so they
    # travel as data files rather than as imported modules.
    (str(BACKEND / "alembic"), "alembic"),
    # The built single-page client, served by the API itself.
    (str(ROOT / "frontend" / "dist"), "web"),
    *ortools_datas,
]

hiddenimports = [
    # uvicorn picks its event loop and protocol implementations by name.
    *collect_submodules("uvicorn"),
    "app.models",
    *ortools_hiddenimports,
]

analysis = Analysis(
    [str(BACKEND / "app" / "desktop" / "__main__.py")],
    pathex=[str(BACKEND)],
    binaries=ortools_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    excludes=["tkinter", "matplotlib", "pytest", "mypy", "PIL"],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="Horarios",
    debug=False,
    strip=False,
    upx=False,  # UPX-packed executables are a well-known antivirus trigger.
    console=False,
    icon=str(ROOT / "packaging" / "horarios.ico"),
)

COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="Horarios",
)
