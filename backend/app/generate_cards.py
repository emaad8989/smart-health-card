"""Smart Health Card - two-QR card generator (synthetic data only).

Front: identity + blue DOCTOR QR (patient ID only).
Back : red EMERGENCY band + large emergency QR (signed link) + contact.
Card : 85.6 x 54 mm at 300 DPI = 1011 x 638 px.
"""
import os
import sys

import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_M

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.seed import SAMPLE_PATIENTS          # noqa: E402
from app.emergency_link import make_signature  # noqa: E402

SITE = "https://smart-health-card-bltg.onrender.com"
W, H = 1011, 638
BLUE = (21, 101, 192)
RED = (198, 40, 40)
DARK = (30, 30, 30)
GREY = (90, 90, 90)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cards")
os.makedirs(OUT, exist_ok=True)


def font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    for path in (os.path.join("C:\\Windows\\Fonts", name), name):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_qr(data, target, level):
    """Black-on-white QR scaled to a whole number of pixels per module."""
    qr = qrcode.QRCode(error_correction=level, border=0)
    qr.add_data(data)
    qr.make(fit=True)
    n = len(qr.get_matrix())
    box = max(1, target // n)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((n * box, n * box), Image.NEAREST)
    pad = box * 4  # quiet zone
    tile = Image.new("RGB", (img.width + 2 * pad, img.height + 2 * pad), "white")
    tile.paste(img, (pad, pad))
    return tile


def front(p):
    card = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, W, 90], fill=BLUE)
    d.text((30, 18), "SMART HEALTH CARD", font=font(46, True), fill="white")

    d.text((30, 130), p["full_name"], font=font(44, True), fill=DARK)
    d.text((30, 200), "ID: " + p["patient_id"], font=font(36, True), fill=BLUE)
    d.text((30, 255), "DOB: " + str(p["date_of_birth"]), font=font(30), fill=GREY)
    d.text((30, 300), "Gender: " + str(p["gender"]), font=font(30), fill=GREY)

    d.rounded_rectangle([30, 400, 290, 520], radius=18, outline=RED, width=6)
    d.text((50, 410), "BLOOD", font=font(26, True), fill=RED)
    d.text((50, 445), str(p["blood_group"]), font=font(64, True), fill=RED)

    qr = make_qr(p["patient_id"], 290, ERROR_CORRECT_H)
    x = W - qr.width - 30
    card.paste(qr, (x, 120))
    d.text((x + 10, 120 + qr.height + 5), "DOCTOR SCAN", font=font(30, True), fill=BLUE)
    d.text((x + 10, 120 + qr.height + 42), "Use the hospital scanner", font=font(22), fill=GREY)
    return card


def back(p):
    card = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, W, 100], fill=RED)
    d.text((30, 20), "EMERGENCY", font=font(60, True), fill="white")

    sig = make_signature(p["patient_id"])
    url = f"{SITE}/emergency.html?id={p['patient_id']}&sig={sig}"
    qr = make_qr(url, 340, ERROR_CORRECT_M)
    card.paste(qr, (20, 120))

    x = 20 + qr.width + 30
    d.text((x, 130), "In an emergency,", font=font(34, True), fill=DARK)
    d.text((x, 175), "scan with your", font=font(34, True), fill=DARK)
    d.text((x, 220), "phone camera", font=font(34, True), fill=DARK)
    d.text((x, 285), "Shows blood group,", font=font(26), fill=GREY)
    d.text((x, 320), "allergies & contact.", font=font(26), fill=GREY)
    d.text((x, 360), "No login needed.", font=font(26), fill=GREY)

    d.line([30, 540, W - 30, 540], fill=RED, width=3)
    contact = f"{p.get('emergency_contact_name', '')}   {p.get('emergency_contact_phone', '')}"
    d.text((30, 555), "Emergency contact: " + contact.strip(), font=font(26, True), fill=DARK)
    d.text((30, 595), p["full_name"] + "  |  " + p["patient_id"], font=font(22), fill=GREY)
    return card


for p in SAMPLE_PATIENTS:
    f, b = front(p), back(p)
    f.save(os.path.join(OUT, f"{p['patient_id']}_front.png"), dpi=(300, 300))
    b.save(os.path.join(OUT, f"{p['patient_id']}_back.png"), dpi=(300, 300))
    f.save(os.path.join(OUT, f"{p['patient_id']}_card.pdf"), save_all=True,
           append_images=[b], resolution=300)
    print("Done:", p["patient_id"])

print("Cards saved in:", OUT)