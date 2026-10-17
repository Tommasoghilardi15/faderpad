"""Start Faderpad: python -m faderpad [--port 5757] [--pin 1234] [--no-browser]"""
import argparse
import json
import logging
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path

from werkzeug.serving import make_server

from . import __version__
from . import setup
from .server import create_app

DEFAULT_PORT = 5757
CONFIG_NAME = "faderpad.json"
LOG_NAME = "faderpad.log"


def base_dir():
    """Folder of the .exe when frozen, otherwise the current folder."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def load_config():
    """Optional faderpad.json next to the program: {"port": 5757, "pin": "1234", "open_browser": true}."""
    path = base_dir() / CONFIG_NAME
    if not path.is_file():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError) as e:
        print(f"Ignoring {path.name}: {e}")
        return {}


def lan_addresses():
    """Local network addresses of this PC, most likely one first."""
    found = []
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))  # no packet is sent; this only picks a route
        found.append(probe.getsockname()[0])
    except OSError:
        pass
    finally:
        probe.close()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            address = info[4][0]
            if address not in found:
                found.append(address)
    except OSError:
        pass
    return [a for a in found if not a.startswith(("127.", "169.254."))] or ["127.0.0.1"]


def setup_log():
    """The .exe has no console, so print() would crash: send all output to faderpad.log instead."""
    if not getattr(sys, "frozen", False):
        return
    try:
        log = open(base_dir() / LOG_NAME, "w", encoding="utf-8", buffering=1)
    except OSError:
        log = open(os.devnull, "w")
    sys.stdout = sys.stderr = log


def alert(text):
    """Tell the user something when there is no console to print to."""
    print(text)
    if getattr(sys, "frozen", False) and sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, text, "Faderpad", 0x10)


def show_window(url):
    """Open Faderpad's own window and wait until it is closed. Returns False if that isn't possible."""
    try:
        import webview
        webview.create_window("Faderpad", url, width=1100, height=700, min_size=(480, 420))
        webview.start()
        return True
    except Exception as e:  # e.g. Edge WebView2 missing: fall back to the browser
        print(f"Could not open the app window ({type(e).__name__}: {e}), using the browser instead.")
        return False


def main(argv=None):
    setup_log()
    try:
        sys.stdout.reconfigure(line_buffering=True)  # show messages right away, even when redirected
    except Exception:
        pass
    config = load_config()
    parser = argparse.ArgumentParser(
        prog="faderpad",
        description="Control Elgato Wave Link from a tablet or phone on the same network.",
    )
    parser.add_argument("--port", type=int, default=config.get("port", DEFAULT_PORT),
                        help=f"port to listen on (default {DEFAULT_PORT})")
    parser.add_argument("--host", default=config.get("host", "0.0.0.0"),
                        help="address to listen on (default: all network interfaces)")
    parser.add_argument("--pin", default=config.get("pin"),
                        help="ask other devices for this PIN before they can control anything")
    parser.add_argument("--no-browser", action="store_true",
                        default=not config.get("open_browser", True),
                        help="don't open the Faderpad window on this PC (the server just runs)")
    parser.add_argument("--version", action="version", version=f"Faderpad {__version__}")
    args = parser.parse_args(argv)
    pin = str(args.pin) if args.pin not in (None, "") else None

    if args.host in ("0.0.0.0", "::"):
        urls = [f"http://{ip}:{args.port}" for ip in lan_addresses()]
    else:
        urls = [f"http://{args.host}:{args.port}"]

    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app = create_app(pin=pin, urls=urls)
    try:
        server = make_server(args.host, args.port, app, threaded=True)
    except OSError:
        alert(f"Port {args.port} is already in use. Is Faderpad already running?\n"
              "Close the other copy, or start Faderpad on another port with --port.")
        return 1

    print(f"Faderpad {__version__}")
    print()
    print("Open this address on your tablet or phone (same Wi-Fi as this PC):")
    for url in urls:
        print(f"  {url}")
    print()
    print(f"PIN: {'on' if pin else 'off'}")
    print("Close the Faderpad window to stop it.")

    setup.refresh_autostart()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        opened = False
        if not args.no_browser:
            # Closing the window closes Faderpad: serve_forever runs in a daemon thread and dies with us.
            first_page = "welcome" if setup.supported() and not setup.is_done() else ""
            opened = show_window(f"http://127.0.0.1:{args.port}/{first_page}")
            if not opened:
                webbrowser.open(f"http://127.0.0.1:{args.port}/")
        if not opened:
            threading.Event().wait()  # no window: keep serving until Ctrl+C
    except KeyboardInterrupt:
        pass
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
