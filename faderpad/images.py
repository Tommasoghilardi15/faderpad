"""Small helpers for the images Wave Link and Windows hand us."""
import base64
import os


def sniff_image_type(data):
    """Return the MIME type of an image from its first bytes, or None."""
    if not data:
        return None
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data[:2] == b"\xff\xd8":
        return "image/jpeg"
    if data[:4] == b"\x00\x00\x01\x00":
        return "image/x-icon"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    head = data[:300].lstrip().lower()
    if head.startswith(b"<svg") or head.startswith(b"<?xml"):
        return "image/svg+xml"
    return None


def image_data_uri(image):
    """Turn a Wave Link image (base64 data or a file path) into a data: URI.

    Returns None when the image is missing or not recognisable; the web app then
    draws its own icon instead.
    """
    if image is None or not getattr(image, "img_data", None):
        return None
    raw = image.img_data.strip()
    if raw.startswith("data:image"):
        return raw
    data = None
    try:
        if len(raw) < 500 and os.path.isfile(raw):
            with open(raw, "rb") as f:
                data = f.read()
    except (OSError, ValueError):
        pass
    if data is None:
        try:
            data = base64.b64decode(raw + "=" * (-len(raw) % 4))
        except Exception:
            return None
    mime = sniff_image_type(data)
    if mime is None:
        return None
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"
