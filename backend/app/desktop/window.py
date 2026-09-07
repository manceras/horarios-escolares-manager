"""The application window.

Windows 10 and 11 ship the Edge WebView2 runtime, so pywebview can give the
program a real window with its own icon and taskbar entry rather than a browser
tab. When that runtime is missing -- an old, unpatched Windows 10 -- falling
back to the default browser is far better than an error the user cannot act on.
"""

import logging
import webbrowser

logger = logging.getLogger(__name__)

WINDOW_TITLE = "Horarios"
INITIAL_WIDTH = 1280
INITIAL_HEIGHT = 860
MINIMUM_SIZE = (1024, 640)


def open_window(url: str) -> None:
    """Show the application. Blocks until the user closes it.

    Falls back to the default browser, which does not block, so the caller must
    keep the process alive itself in that case -- see ``run_until_closed``.
    """
    try:
        import webview
    except ImportError:
        logger.warning("pywebview is not installed; opening the default browser")
        webbrowser.open(url)
        return

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
        # A missing WebView2 runtime surfaces here as a native error. The user
        # wants their timetable, not a diagnosis.
        logger.exception("Could not open a native window; opening the default browser")
        webbrowser.open(url)
        _block_forever()


def _block_forever() -> None:
    """Keep the process (and therefore the server) alive for the browser tab."""
    import threading

    threading.Event().wait()
