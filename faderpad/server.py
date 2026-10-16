"""HTTP server: serves the web app and the JSON API it talks to."""
import hashlib
import hmac
import io
import json
import time
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

from . import __version__
from .background import Background
from .media import MediaController
from .wavelink import WaveLink

WEB_DIR = Path(__file__).resolve().parent / "web"
PIN_COOKIE = "faderpad_auth"
OPEN_PATHS = {"/api/info", "/api/auth"}          # reachable without the PIN
LOCAL_ADDRESSES = {"127.0.0.1", "::1"}           # the PC itself never needs the PIN
LEVELS_INTERVAL = 0.066                          # ~15 meter updates per second


def _error(code, status, detail=None):
    body = {"error": code}
    if detail:
        body["detail"] = detail
    return jsonify(body), status


def create_app(pin=None, urls=()):
    app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path="/static")
    background = Background()
    wavelink = WaveLink(background)
    media = MediaController(background)
    token = hashlib.sha256(f"faderpad:{pin}".encode()).hexdigest() if pin else None

    def authorized():
        if not pin or request.remote_addr in LOCAL_ADDRESSES:
            return True
        return hmac.compare_digest(request.cookies.get(PIN_COOKIE, ""), token)

    @app.before_request
    def require_pin():
        if request.path.startswith("/api/") and request.path not in OPEN_PATHS and not authorized():
            return _error("pin_required", 401)
        return None

    # ---------- pages ----------

    @app.get("/")
    def index():
        return send_from_directory(WEB_DIR, "index.html")

    @app.get("/connect")
    def connect():
        return send_from_directory(WEB_DIR, "connect.html")

    @app.get("/apple-touch-icon.png")
    def touch_icon():
        return send_from_directory(WEB_DIR, "icon.png")

    @app.get("/qr.svg")
    def qr_code():
        import qrcode
        import qrcode.image.svg

        target = urls[0] if urls else request.host_url
        image = qrcode.make(target, image_factory=qrcode.image.svg.SvgPathImage, border=2)
        buffer = io.BytesIO()
        image.save(buffer)
        return Response(buffer.getvalue(), mimetype="image/svg+xml")

    # ---------- access ----------

    @app.get("/api/info")
    def info():
        return jsonify(version=__version__, pin_required=bool(pin), authorized=authorized(), urls=list(urls))

    @app.post("/api/auth")
    def auth():
        if not pin:
            return jsonify(ok=True)
        given = str((request.get_json(silent=True) or {}).get("pin", ""))
        if not hmac.compare_digest(given.encode(), pin.encode()):
            time.sleep(0.6)  # slows down guessing
            return _error("wrong_pin", 401)
        response = jsonify(ok=True)
        response.set_cookie(PIN_COOKIE, token, max_age=60 * 60 * 24 * 365, httponly=True, samesite="Strict")
        return response

    # ---------- Wave Link ----------

    @app.get("/api/state")
    def state():
        result = {"media": media.state()}
        try:
            result["wavelink"] = wavelink.state()
        except Exception as e:
            result["wavelink"] = None
            result["error"] = "wavelink_unavailable"
            result["detail"] = f"{type(e).__name__}: {e}"
        return jsonify(result)

    @app.post("/api/set")
    def set_value():
        change = request.get_json(silent=True)
        if not isinstance(change, dict):
            return _error("bad_request", 400)
        try:
            wavelink.apply(change)
        except (KeyError, ValueError, TypeError) as e:
            return _error("bad_request", 400, f"{type(e).__name__}: {e}")
        except Exception as e:
            return _error("wavelink_unavailable", 502, f"{type(e).__name__}: {e}")
        return jsonify(ok=True)

    @app.get("/api/icons")
    def icons():
        try:
            return jsonify(wavelink.icons())
        except Exception as e:
            return _error("wavelink_unavailable", 502, f"{type(e).__name__}: {e}")

    @app.get("/api/levels")
    def levels():
        """Live level meters as Server-Sent Events."""
        def stream():
            last, last_sent = None, 0.0
            while True:
                now = time.monotonic()
                text = json.dumps(wavelink.meters(), separators=(",", ":"))
                if text != last or now - last_sent > 2:
                    last, last_sent = text, now
                    yield f"data: {text}\n\n"
                time.sleep(LEVELS_INTERVAL)

        return Response(stream(), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    # ---------- media ----------

    @app.post("/api/media")
    def media_command():
        body = request.get_json(silent=True) or {}
        try:
            return jsonify(ok=True, via=media.command(body.get("action"), body.get("session")))
        except ValueError as e:
            return _error("bad_request", 400, str(e))
        except Exception as e:
            return _error("media_unavailable", 502, f"{type(e).__name__}: {e}")

    @app.get("/api/media/cover")
    def media_cover():
        data, mime = media.cover(request.args.get("k", ""))
        if not data:
            return _error("not_found", 404)
        return Response(data, mimetype=mime or "image/png", headers={"Cache-Control": "max-age=86400"})

    # ---------- troubleshooting ----------

    @app.get("/api/debug")
    def debug():
        result = {"version": __version__, "media": media.debug()}
        try:
            result["wavelink"] = wavelink.state()
        except Exception as e:
            result["wavelink_error"] = f"{type(e).__name__}: {e}"
        return jsonify(result)

    return app
