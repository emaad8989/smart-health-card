from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.database import SessionLocal
from app.generate_qr import make_qr_image
from app.models import Patient

# Cards are saved in "card_designs" at the top of the project.
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "card_designs"

DPI = 300


def mm(value: float) -> int:
    """Convert millimetres to pixels at 300 DPI."""
    return round(value / 25.4 * DPI)


CARD_W, CARD_H = mm(85.6), mm(54)   # standard ID-card size (CR80)
BLEED = mm(0)                        # change to mm(3) if the print shop asks for bleed

# Colours
TEAL = (0, 121, 107)
DARK = (30, 30, 30)
GREY = (110, 110, 110)
LIGHT = (240, 245, 244)

REGULAR_FONTS = ["C:/Windows/Fonts/arial.ttf"]
BOLD_FONTS = ["C:/Windows/Fonts/arialbd.ttf"]


def load_font(size: int, bold: bool = False):
    for path in (BOLD_FONTS if bold else REGULAR_FONTS):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def fit_font(draw, text, max_width, start_size, bold=True):
    """Shrink the font until the text fits inside max_width."""
    size = start_size
    font = load_font(size, bold)
    while draw.textlength(text, font=font) > max_width and size > 20:
        size -= 2
        font = load_font(size, bold)
    return font


def make_card(patient: Patient) -> Image.Image:
    canvas_w, canvas_h = CARD_W + 2 * BLEED, CARD_H + 2 * BLEED
    ox, oy = BLEED, BLEED  # where the real card starts inside the canvas

    card = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(card)

    # Header band (runs to the canvas edge so bleed is covered)
    draw.rectangle([0, 0, canvas_w, oy + 110], fill=TEAL)
    draw.text((ox + 50, oy + 28), "SMART HEALTH CARD", font=load_font(50, True), fill="white")

    # Footer band
    draw.rectangle([0, oy + CARD_H - 60, canvas_w, canvas_h], fill=LIGHT)
    draw.text(
        (ox + 50, oy + CARD_H - 45),
        "DEMO CARD - synthetic data only",
        font=load_font(24),
        fill=GREY,
    )

    # Left side: text details
    left = ox + 50
    text_width = 540
    label_font = load_font(24)

    draw.text((left, oy + 135), "NAME", font=label_font, fill=GREY)
    name_font = fit_font(draw, patient.full_name, text_width, 54)
    draw.text((left, oy + 165), patient.full_name, font=name_font, fill=DARK)

    draw.text((left, oy + 260), "PATIENT ID", font=label_font, fill=GREY)
    draw.text((left, oy + 290), patient.patient_id, font=load_font(68, True), fill=TEAL)

    draw.text((left, oy + 395), "BLOOD GROUP", font=label_font, fill=GREY)
    draw.text((left, oy + 425), patient.blood_group, font=load_font(52, True), fill=DARK)

    # Right side: QR code
    qr_size = 330
    qr_x = ox + CARD_W - qr_size - 50
    qr_y = oy + 130
    qr_image = make_qr_image(patient.patient_id).get_image().convert("RGB")
    qr_image = qr_image.resize((qr_size, qr_size), Image.NEAREST)
    card.paste(qr_image, (qr_x, qr_y))

    caption = "Scan to open record"
    caption_font = load_font(24)
    caption_width = draw.textlength(caption, font=caption_font)
    draw.text(
        (qr_x + (qr_size - caption_width) / 2, qr_y + qr_size + 10),
        caption,
        font=caption_font,
        fill=GREY,
    )

    return card


def generate_cards():
    OUTPUT_DIR.mkdir(exist_ok=True)

    db = SessionLocal()
    try:
        patients = db.query(Patient).order_by(Patient.patient_id).all()
        for patient in patients:
            card = make_card(patient)
            card.save(OUTPUT_DIR / f"{patient.patient_id}_card.png", dpi=(DPI, DPI))
            card.save(OUTPUT_DIR / f"{patient.patient_id}_card.pdf", "PDF", resolution=DPI)
            print(f"Created card for {patient.patient_id} - {patient.full_name}")
    finally:
        db.close()

    print(f"\nDone. {len(patients)} cards (PNG and PDF) saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_cards()