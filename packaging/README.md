# Packaging

The school downloads one file: `Horarios-Setup-x.y.z.exe`. This directory is how
it gets built.

| File | What it does |
|---|---|
| `horarios.spec` | PyInstaller build: Python, the API, the solver, the migrations and the built web client into `dist/Horarios/` |
| `horarios.iss` | Inno Setup: wraps that directory into the single installer, with shortcuts and an uninstall entry |
| `horarios.ico` | The icon, generated from `horarios.png` |

## Building

Normally you do not: pushing a `v*` tag runs
[`.github/workflows/release.yml`](../.github/workflows/release.yml) on a Windows
runner, which builds both and attaches them to the release with a `.sha256`.
**PyInstaller cannot cross-compile**, so a Windows machine or runner is the only
way to produce the `.exe`.

By hand, on Windows, from the repository root:

```sh
uv sync --project backend --extra desktop --group build
pnpm --dir frontend install && pnpm --dir frontend build
uv run --project backend pyinstaller packaging/horarios.spec --noconfirm --clean --distpath dist --workpath build
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DAppVersion=0.1.0 packaging\horarios.iss
```

`make installer` does everything up to the last line on any platform, which is
enough to check the spec still works — the Linux build runs, it just cannot be
shipped to a school.

## Things that are the way they are on purpose

- **One-directory, not one-file.** A one-file build unpacks ~200 MB to a temp
  folder on every launch. That is seconds of startup and the behaviour antivirus
  heuristics are most suspicious of.
- **No UPX.** Compressed executables are a long-standing false-positive trigger.
- **Per-user install into `%LOCALAPPDATA%`.** Program Files needs administrator
  rights that a school laptop's account usually lacks, and a UAC prompt is one
  more place for a teacher to stop.
- **The uninstaller does not delete `%LOCALAPPDATA%\Horarios`.** Removing the
  program must never remove the school's timetables.

## The SmartScreen warning

The installer is not code-signed, so Windows shows *"Windows protected your PC"*
on first run and hides the button behind **More info → Run anyway**. Nothing in
the build can avoid this; only an OV or EV code-signing certificate can, at a few
hundred euros a year. The `.sha256` published beside each installer is what
verifies a download in the meantime.
