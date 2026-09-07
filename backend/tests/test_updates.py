"""Update checking: version comparison, failure modes and checksum verification."""

import json
from pathlib import Path
from typing import Any

import pytest
from app import __version__
from app.desktop import updates


@pytest.mark.parametrize(
    ("candidate", "installed", "expected"),
    [
        ("v1.2.0", "1.1.9", True),
        ("1.2.0", "v1.2.0", False),
        ("v1.1.0", "1.2.0", False),
        ("v1.10.0", "1.9.0", True),  # not a string comparison
        ("v2.0.0-beta.1", "1.9.9", True),
    ],
)
def test_version_comparison(candidate: str, installed: str, expected: bool) -> None:
    assert updates.is_newer(candidate, installed) is expected


@pytest.mark.parametrize("tag", ["", "latest", "nightly", "v1.2"])
def test_an_unparseable_tag_never_offers_an_update(tag: str) -> None:
    """A malformed tag must not nag a school on every startup."""
    assert updates.is_newer(tag, "1.0.0") is False


def test_an_unreachable_github_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """No network means keep working, not a dialog nobody can act on."""

    def explode(*_args: Any, **_kwargs: Any) -> Any:
        raise OSError("no network")

    monkeypatch.setattr(updates.urllib.request, "urlopen", explode)

    status = updates.check_for_update()

    assert status.update_available is False
    assert status.current_version == __version__


def _release(tag: str, assets: list[dict[str, str]]) -> bytes:
    return json.dumps({"tag_name": tag, "assets": assets}).encode()


def test_finds_the_windows_installer_among_the_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = _release(
        "v99.0.0",
        [
            {"name": "horarios-source.zip", "browser_download_url": "https://x/source.zip"},
            {"name": "Horarios-Setup-99.0.0.exe", "browser_download_url": "https://x/setup.exe"},
        ],
    )
    monkeypatch.setattr(updates, "_read_release", lambda _url: json.loads(payload))

    status = updates.check_for_update()

    assert status.update_available is True
    assert status.download_url == "https://x/setup.exe"


def test_a_release_without_an_installer_offers_no_download(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _release("v99.0.0", [{"name": "notes.txt", "browser_download_url": "https://x/n"}])
    monkeypatch.setattr(updates, "_read_release", lambda _url: json.loads(payload))

    status = updates.check_for_update()

    assert status.update_available is True
    assert status.download_url is None


def test_a_mismatched_checksum_rejects_the_download(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A truncated or tampered installer must never be run."""

    def fake_download(url: str, destination: Path, timeout: float = 0.0) -> Path:
        destination.write_bytes(b"wrong checksum" if url.endswith(".sha256") else b"payload")
        return destination

    monkeypatch.setattr(updates, "_download", fake_download)

    with pytest.raises(ValueError, match="checksum"):
        updates.download_installer("https://x/Horarios-Setup.exe", tmp_path)

    assert not (tmp_path / "Horarios-Setup.exe").exists()


def test_a_matching_checksum_keeps_the_installer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"installer bytes"
    digest = updates.hashlib.sha256(payload).hexdigest()

    def fake_download(url: str, destination: Path, timeout: float = 0.0) -> Path:
        content = f"{digest}  Horarios-Setup.exe\n".encode() if url.endswith(".sha256") else payload
        destination.write_bytes(content)
        return destination

    monkeypatch.setattr(updates, "_download", fake_download)

    installer = updates.download_installer("https://x/Horarios-Setup.exe", tmp_path)

    assert installer.read_bytes() == payload
