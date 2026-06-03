from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path
from typing import Optional

try:
    import cv2
    _CV2 = True
except ImportError:
    _CV2 = False

try:
    import mss
    import mss.tools
    _MSS = True
except ImportError:
    _MSS = False

try:
    import PIL.Image
    _PIL = True
except ImportError:
    _PIL = False

import numpy as np
from google import genai
from google.genai import types as gtypes


# ─── Paths & Config ───────────────────────────────────────────────────────────

def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


_BASE        = _base_dir()
_CONFIG_PATH = _BASE / "config" / "api_keys.json"

_VISION_MODEL = "gemini-2.5-flash"   # text-in, text-out — fast and multimodal

_IMG_MAX_W = 1280
_IMG_MAX_H = 720
_JPEG_Q    = 75


def _load_config() -> dict:
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _get_api_key() -> str:
    key = _load_config().get("gemini_api_key", "")
    if not key:
        raise RuntimeError("gemini_api_key not found in config.")
    return key


def _get_os() -> str:
    return _load_config().get("os_system", "windows").lower()


# ─── Image Capture & Compression ──────────────────────────────────────────────

def _compress(img_bytes: bytes, source_format: str = "PNG") -> tuple[bytes, str]:
    if not _PIL:
        return img_bytes, f"image/{source_format.lower()}"
    try:
        img = PIL.Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img.thumbnail((_IMG_MAX_W, _IMG_MAX_H), PIL.Image.BILINEAR)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=_JPEG_Q, optimize=False)
        return buf.getvalue(), "image/jpeg"
    except Exception as e:
        print(f"[Vision] ⚠️  Image compress failed: {e}")
        return img_bytes, f"image/{source_format.lower()}"


def _capture_screen() -> tuple[bytes, str]:
    if not _MSS:
        raise RuntimeError("mss is not installed. Run: pip install mss")
    with mss.mss() as sct:
        monitors = sct.monitors
        target   = monitors[1] if len(monitors) > 1 else monitors[0]
        shot     = sct.grab(target)
        png      = mss.tools.to_png(shot.rgb, shot.size)
    return _compress(png, "PNG")


def _cv2_backend() -> int:
    if not _CV2:
        return 0
    os_name = _get_os()
    if os_name == "windows":
        return cv2.CAP_DSHOW
    if os_name == "mac":
        return cv2.CAP_AVFOUNDATION
    return cv2.CAP_ANY


def _probe_camera(index: int, backend: int, warmup: int = 5) -> bool:
    if not _CV2:
        return False
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        cap.release()
        return False
    for _ in range(warmup):
        cap.read()
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return False
    return bool(np.mean(frame) > 8)


def _detect_camera_index() -> int:
    backend = _cv2_backend()
    print("[Vision] 🔍 Auto-detecting camera...")
    for idx in range(6):
        if _probe_camera(idx, backend):
            print(f"[Vision] ✅ Camera found at index {idx}")
            cfg = _load_config()
            cfg["camera_index"] = idx
            _CONFIG_PATH.write_text(json.dumps(cfg, indent=4), encoding="utf-8")
            return idx
        print(f"[Vision] ⚠️  Camera index {idx}: no usable frame")
    print("[Vision] ⚠️  No camera found — defaulting to index 0")
    return 0


def _get_camera_index() -> int:
    cfg = _load_config()
    if "camera_index" in cfg:
        return int(cfg["camera_index"])
    return _detect_camera_index()


def _capture_camera() -> tuple[bytes, str]:
    if not _CV2:
        raise RuntimeError("OpenCV (cv2) is not installed. Run: pip install opencv-python")
    index   = _get_camera_index()
    backend = _cv2_backend()
    cap     = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        raise RuntimeError(f"Camera index {index} could not be opened.")
    for _ in range(10):
        cap.read()
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        raise RuntimeError("Camera returned no frame.")
    if _PIL:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(rgb)
        img.thumbnail((_IMG_MAX_W, _IMG_MAX_H), PIL.Image.BILINEAR)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=_JPEG_Q)
        return buf.getvalue(), "image/jpeg"
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, _JPEG_Q])
    return buf.tobytes(), "image/jpeg"


# ─── Core Vision Function ─────────────────────────────────────────────────────

_VISION_SYSTEM = (
    "You are JARVIS, Tony Stark's AI assistant. "
    "You have been given an image to analyze. "
    "Describe what you see clearly and concisely, answering the user's specific question. "
    "Be precise and intelligent — like an advanced AI with perfect visual perception. "
    "Maximum 3 sentences unless the question genuinely requires more detail."
)


def screen_process(
    parameters:     dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """
    Captures the screen or camera, analyzes it via the standard Gemini multimodal
    API, and returns the text description. The main Jarvis voice speaks the result.
    No separate audio session — single unified voice.
    """
    params    = parameters or {}
    user_text = (params.get("text") or params.get("user_text") or "What do you see on this screen?").strip()
    angle     = params.get("angle", "screen").lower().strip()

    print(f"[Vision] ▶ angle={angle!r}  question='{user_text[:80]}'")

    # 1. Capture image
    try:
        if angle == "camera":
            image_bytes, mime_type = _capture_camera()
            print(f"[Vision] 📷 Camera: {len(image_bytes):,} bytes")
        else:
            image_bytes, mime_type = _capture_screen()
            print(f"[Vision] 🖥️  Screen: {len(image_bytes):,} bytes")
    except Exception as e:
        print(f"[Vision] ❌ Capture error: {e}")
        return f"I was unable to capture the {'camera' if angle == 'camera' else 'screen'}, sir: {e}"

    # 2. Analyze with standard Gemini multimodal API (text response)
    try:
        client = genai.Client(api_key=_get_api_key())
        b64    = base64.b64encode(image_bytes).decode("ascii")

        response_obj = client.models.generate_content(
            model=_VISION_MODEL,
            contents=[
                gtypes.Content(
                    role="user",
                    parts=[
                        gtypes.Part(
                            inline_data=gtypes.Blob(
                                mime_type=mime_type,
                                data=b64,
                            )
                        ),
                        gtypes.Part(text=user_text),
                    ],
                )
            ],
            config=gtypes.GenerateContentConfig(
                system_instruction=_VISION_SYSTEM,
                temperature=0.4,
            ),
        )

        # Extract text from response
        text = ""
        for part in response_obj.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                text += part.text

        text = text.strip()
        if not text:
            return "I analyzed the screen but received an empty response, sir."

        print(f"[Vision] ✅ Analysis: {text[:120]}")
        return text

    except Exception as e:
        print(f"[Vision] ❌ Analysis error: {e}")
        return f"I encountered an error analyzing the {'camera' if angle == 'camera' else 'screen'}, sir: {e}"


# ─── Backward Compatibility ───────────────────────────────────────────────────

def warmup_session(player=None) -> None:
    """No-op: kept for backward compatibility. No separate session needed."""
    pass


if __name__ == "__main__":
    print("[TEST] screen_processor.py")
    print("=" * 52)
    mode = input("angle — screen / camera (default: screen): ").strip().lower() or "screen"
    q    = input("Question (Enter = default): ").strip() or "What do you see? Be brief."
    result = screen_process({"angle": mode, "text": q})
    print(f"\nResult:\n{result}")