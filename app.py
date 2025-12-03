from _future_ import annotations

import base64
import io
import json
import os
import textwrap
from zipfile import ZipFile

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from PIL import Image
from google import genai

load_dotenv()

API_KEY = os.getenv("GENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Set GENAI_API_KEY or GEMINI_API_KEY before starting the server.")

TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.0-flash")
IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

client = genai.Client(api_key=API_KEY)

POSTER_STYLES = [
    "Soft pastel studio gradients with diffused light",
    "High-energy neon scene with motion trails",
    "Premium editorial dark backdrop with rim lighting",
]

app = Flask(_name_)


def load_image_from_upload(upload):
    if not upload:
        return None
    data = upload.read()
    if not data:
        return None
    return Image.open(io.BytesIO(data)).convert("RGB")


def ensure_images(logo_upload, product_upload):
    logo_img = load_image_from_upload(logo_upload)
    product_img = load_image_from_upload(product_upload)
    if not logo_img or not product_img:
        raise ValueError("Both brand logo and product image are required")
    return logo_img, product_img


def generate_copy_from_images(product_img, logo_img):
    prompt = textwrap.dedent(
        """
        You are the H-003 Auto-Creative Engine.
        You receive two reference images: the hero product and the brand logo.
        Infer the product category, mood, and value props strictly from the visuals.
        Return JSON with:
        {
            "title": "6 word headline",
            "caption": "Punchy caption under 40 words"
        }
        No markdown, no commentary.
        """
    ).strip()

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=[prompt, product_img, logo_img],
    )

    raw = response.text or ""
    if not raw and getattr(response, "candidates", None):
        raw = response.candidates[0].content.parts[0].text

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = _fallback_parse_copy(raw)

    return {
        "title": parsed.get("title", "Untitled concept"),
        "caption": parsed.get("caption", "Gemini could not infer a caption."),
    }


def _fallback_parse_copy(raw_text):
    title = "Untitled"
    caption = raw_text.strip()
    for line in raw_text.splitlines():
        upper = line.strip()
        if upper.lower().startswith("title") or upper.lower().startswith("headline"):
            title = upper.split(":", 1)[-1].strip() or title
        if upper.lower().startswith("caption"):
            caption = upper.split(":", 1)[-1].strip() or caption
    return {"title": title, "caption": caption}


def generate_posters(product_img, logo_img, count):
    posters = []
    for idx in range(count):
        style = POSTER_STYLES[idx % len(POSTER_STYLES)]
        prompt = textwrap.dedent(
            f"""
            You are an art director composing a finished advertising poster.
            - Use the provided PRODUCT IMAGE as the hero subject without heavy distortion.
            - Place the provided LOGO IMAGE clearly in a top or bottom corner.
            - Build supporting typography, lighting, and background inspired by: {style}.
            - Keep everything photorealistic and ready for print.
            Return only the rendered image.
            """
        ).strip()

        try:
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=[prompt, product_img, logo_img],
            )
            data_url = extract_image_data_url(response)
            if data_url:
                posters.append({"style": style, "image_data_url": data_url})
        except Exception as exc:  # pragma: no cover - network call
            print(f"Error generating poster {idx + 1}: {exc}")

    return posters


def extract_image_data_url(response):
    parts = getattr(response, "parts", None) or getattr(response, "candidates", None)
    if not parts:
        return None

    part_list = parts
    if hasattr(parts[0], "content"):
        part_list = parts[0].content.parts

    for part in part_list:
        inline = getattr(part, "inline_data", None)
        if inline and inline.data:
            mime = inline.mime_type or "image/png"
            return f"data:{mime};base64,{inline.data}"
    return None


def pack_zip(copy_block, posters):
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as zipf:
        zipf.writestr(
            "copy.txt",
            textwrap.dedent(
                f"""
                TITLE: {copy_block.get('title')}
                CAPTION: {copy_block.get('caption')}
                """
            ).strip(),
        )

        for idx, poster in enumerate(posters, start=1):
            data_url = poster.get("image_data_url")
            if not data_url or "," not in data_url:
                continue
            _, payload = data_url.split(",", 1)
            zipf.writestr(f"poster_{idx}.png", base64.b64decode(payload))

    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/generate")
def generate_campaign():
    try:
        variation_count = int(request.form.get("variationCount", 1))
    except ValueError:
        variation_count = 1
    variation_count = max(1, min(variation_count, 3))

    try:
        logo_img, product_img = ensure_images(
            request.files.get("brandLogo"),
            request.files.get("productImage"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    copy_block = generate_copy_from_images(product_img, logo_img)
    posters = generate_posters(product_img, logo_img, variation_count)

    if not posters:
        return jsonify({"error": "Gemini could not render any posters. Try again."}), 502

    zip_b64 = pack_zip(copy_block, posters)
    return jsonify({
        "copy": copy_block,
        "posters": posters,
        "zip_base64": zip_b64,
    })


if _name_ == "_main_":
    app.run(debug=True)
