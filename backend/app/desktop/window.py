"""The application window.

Three ways to show the app, tried in order, because no single one works
everywhere:

1. **pywebview.** On Windows 10 and 11 the Edge WebView2 runtime is already
   there, so this gives a real window with its own icon and taskbar entry.
2. **A Chromium-family browser in app mode.** `--app=<url>` opens a window with
   no tabs, no address bar and no bookmarks -- close enough to a native window
   that a teacher will not notice, and it needs nothing bundled. This is the
   normal path on Linux, where shipping WebKitGTK inside the bundle is fragile
   across distributions.
3. **The default browser.** A tab is worse than a window, and still far better
   than an error the user cannot act on.
"""

import logging
import shutil
import subprocess
import threading
import webbrowser

logger = logging.getLogger(__name__)

WINDOW_TITLE = "Horarios"
INITIAL_WIDTH = 1280
INITIAL_HEIGHT = 860
MINIMUM_SIZE = (1024, 640)

# Chromium derivatives that accept --app. Ordered by how likely a school
# machine is to have one.
APP_MODE_BROWSERS = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    "brave-browser",
    "vivaldi",
)


def open_window(url: str) -> None:
    """Show the application. Returns only when the user closes it."""
    if _open_native_window(url):
        return
    if _open_app_mode_browser(url):
        return

    logger.warning("No app-mode browser found; opening the default browser")
    webbrowser.open(url)
    _block_forever()


def _open_native_window(url: str) -> bool:
    """A real window through pywebview. Returns False if it is not usable here."""
    try:
        import webview
    except ImportError:
        logger.info("pywebview is not installed")
        return False

    webview.create_window(
        WINDOW_TITLE,
        url,
        width=INITIAL_WIDTH,
        height=INITIAL_HEIGHT,
        min_size=MINIMUM_SIZE,
        text_select=True,
    )
    try:
        webview.start()
    except Exception:
        # A missing WebView2 runtime, or a Linux box with no GTK bindings,
        # surfaces here as a native error. The user wants their timetable,
        # not a diagnosis.
        logger.info("No native window available, falling back", exc_info=True)
        return False
    return True


def _open_app_mode_browser(url: str) -> bool:
    """A chromeless browser window. Blocks until it is closed."""
    for name in APP_MODE_BROWSERS:
        executable = shutil.which(name)
        if executable is None:
            continue
        logger.info("Opening %s in app mode", name)
        try:
            subprocess.run(
                [executable, f"--app={url}", f"--window-size={INITIAL_WIDTH},{INITIAL_HEIGHT}"],
                check=False,
            )
        except OSError:
            logger.info("Could not launch %s", name, exc_info=True)
            continue
        return True
    return False


def _block_forever() -> None:
    """Keep the process (and therefore the server) alive for the browser tab."""
    threading.Event().wait()
