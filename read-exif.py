#!/usr/bin/env python3
"""ExifPeek: read EXIF data from images and optionally build a contact sheet.

Examples:
    python read-exif.py photo.jpg
    python read-exif.py ./photos
    python read-exif.py ./photos -r
    python read-exif.py ./photos --contact-sheet
    python read-exif.py ./photos --contact-sheet --fields camera,iso,aperture,shutter -o sheet.jpg

Requires Pillow 9.4 or newer:
    pip install Pillow
"""

import argparse
import math
import sys
from pathlib import Path

from PIL import ExifTags, Image, ImageDraw, ImageFont, ImageOps

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".webp"}

# Fields shown under each thumbnail when --fields is not given.
DEFAULT_FIELDS = [
    "Model",
    "DateTimeOriginal",
    "FNumber",
    "ExposureTime",
    "ISOSpeedRatings",
    "FocalLength",
]

# Short names accepted by --fields, mapped to the real EXIF tag names.
ALIASES = {
    "camera": ("Model",),
    "make": ("Make",),
    "lens": ("LensModel",),
    "date": ("DateTimeOriginal", "DateTime"),
    "iso": ("ISOSpeedRatings", "PhotographicSensitivity"),
    "aperture": ("FNumber",),
    "shutter": ("ExposureTime",),
    "focal": ("FocalLength",),
}

# Labels printed on the contact sheet. Other tags use their own name.
LABELS = {
    "Model": "Camera",
    "DateTimeOriginal": "Date",
    "DateTime": "Date",
    "FNumber": "Aperture",
    "ExposureTime": "Shutter",
    "ISOSpeedRatings": "ISO",
    "PhotographicSensitivity": "ISO",
    "FocalLength": "Focal",
    "LensModel": "Lens",
}

# These tags only point to sub-IFDs, so they are not worth printing.
POINTER_TAGS = {0x8769, 0x8825}


# ---------------------------------------------------------------- reading ---

def format_value(value):
    """Make raw EXIF values readable."""
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace").strip("\x00").strip()
        return text if text.isprintable() else f"<{len(value)} bytes>"
    return value


def read_exif(img):
    """Return {section name: {tag name: value}} for an open image."""
    exif = img.getexif()
    sections = {}
    if not exif:
        return sections

    sections["Main"] = {
        ExifTags.TAGS.get(tag, f"Unknown (0x{tag:04x})"): value
        for tag, value in exif.items()
        if tag not in POINTER_TAGS
    }

    for title, ifd_id, names in (
        ("Exif", ExifTags.IFD.Exif, ExifTags.TAGS),
        ("GPS", ExifTags.IFD.GPSInfo, ExifTags.GPSTAGS),
    ):
        try:
            ifd = exif.get_ifd(ifd_id)
        except Exception:
            ifd = {}
        if ifd:
            sections[title] = {
                names.get(tag, f"Unknown (0x{tag:04x})"): value
                for tag, value in ifd.items()
            }
    return sections


def print_sections(sections):
    if not sections:
        print("No EXIF data found.")
        return
    for title, tags in sections.items():
        if not tags:
            continue
        print(f"\n=== {title} ===")
        for name, value in tags.items():
            print(f"{name:<28} {format_value(value)}")


def find_images(path, recursive):
    """Return (root folder, sorted list of image paths) for a file or folder."""
    if path.is_file():
        return path.parent, [path]
    pattern = path.rglob("*") if recursive else path.glob("*")
    images = sorted(
        p for p in pattern
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    return path, images


# ----------------------------------------------------------- contact sheet ---

def lookup_field(sections, field):
    """Find a field by tag name or alias, case-insensitively.

    Returns (tag name, value) or None.
    """
    flat = {}
    for tags in sections.values():
        for name, value in tags.items():
            flat.setdefault(name.lower(), (name, value))

    key = field.strip().lower().replace(" ", "")
    candidates = ALIASES.get(key, (field.strip(),))
    for candidate in candidates:
        hit = flat.get(candidate.lower())
        if hit:
            return hit
    return None


def format_for_sheet(name, value):
    """Format common tags the way photographers expect to see them."""
    try:
        if name == "ExposureTime":
            seconds = float(value)
            if 0 < seconds < 1:
                return f"1/{round(1 / seconds)}s"
            return f"{seconds:g}s"
        if name == "FNumber":
            return f"f/{float(value):g}"
        if name == "FocalLength":
            return f"{float(value):g}mm"
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return str(format_value(value))


def load_font(size):
    for name in ("DejaVuSans.ttf", "Arial.ttf", "arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # older Pillow: fixed-size default font
        return ImageFont.load_default()


def fit_text(draw, text, font, max_width):
    """Trim text with '...' so it fits within max_width pixels."""
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]
    return text + "..."


def build_sheet(records, fields, columns, thumb_size, font_size):
    """Draw one contact sheet image from a list of records."""
    font = load_font(font_size)
    pad = 12
    line_h = font_size + 4
    cell_w = thumb_size + pad * 2
    cell_h = thumb_size + pad * 2 + line_h * (1 + len(fields))
    columns = max(1, min(columns, len(records)))
    rows = math.ceil(len(records) / columns)

    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)

    for i, rec in enumerate(records):
        x0 = (i % columns) * cell_w + pad
        y0 = (i // columns) * cell_h + pad
        text_w = thumb_size

        thumb = rec["thumb"]
        if thumb is not None:
            tx = x0 + (thumb_size - thumb.width) // 2
            ty = y0 + (thumb_size - thumb.height) // 2
            sheet.paste(thumb, (tx, ty))
        else:
            draw.rectangle(
                [x0, y0, x0 + thumb_size, y0 + thumb_size], outline="gray"
            )
            draw.text((x0 + 8, y0 + 8), "Unreadable", fill="gray", font=font)

        y = y0 + thumb_size + 6
        name = fit_text(draw, rec["name"], font, text_w)
        draw.text((x0, y), name, fill="black", font=font)
        y += line_h

        lines = []
        for field in fields:
            hit = lookup_field(rec["sections"], field)
            if hit:
                tag, value = hit
                label = LABELS.get(tag, tag)
                lines.append(f"{label}: {format_for_sheet(tag, value)}")
        if not lines:
            lines = ["No EXIF data" if not rec["sections"] else "(no matching fields)"]

        for line in lines:
            draw.text((x0, y), fit_text(draw, line, font, text_w),
                      fill="dimgray", font=font)
            y += line_h

    return sheet


def sheet_paths(output, pages):
    """One path for a single page, numbered paths (name_001.jpg) otherwise."""
    if pages == 1:
        return [output]
    return [
        output.with_name(f"{output.stem}_{n:03d}{output.suffix}")
        for n in range(1, pages + 1)
    ]


# -------------------------------------------------------------------- main ---

def parse_args():
    p = argparse.ArgumentParser(
        description="Read EXIF data from an image or a folder of images, "
                    "and optionally create a contact sheet."
    )
    p.add_argument("path", type=Path, help="image file or folder of images")
    p.add_argument("-r", "--recursive", action="store_true",
                   help="include images in subfolders")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="do not print EXIF data to the terminal")

    sheet = p.add_argument_group("contact sheet")
    sheet.add_argument("--contact-sheet", action="store_true",
                       help="create a contact sheet of thumbnails")
    sheet.add_argument("-o", "--output", type=Path,
                       default=Path("contact_sheet.jpg"),
                       help="contact sheet file (default: contact_sheet.jpg)")
    sheet.add_argument("--fields", default=",".join(DEFAULT_FIELDS),
                       help="comma-separated EXIF fields to print under each "
                            "thumbnail, e.g. camera,iso,aperture,shutter "
                            "(default: %(default)s)")
    sheet.add_argument("--columns", type=int, default=5,
                       help="thumbnails per row (default: 5)")
    sheet.add_argument("--thumb-size", type=int, default=240,
                       help="thumbnail size in pixels (default: 240)")
    sheet.add_argument("--per-sheet", type=int, default=30,
                       help="max images per sheet; extra sheets are numbered "
                            "(default: 30)")
    return p.parse_args()


def main():
    args = parse_args()

    if not args.path.exists():
        sys.exit(f"Path not found: {args.path}")

    root, images = find_images(args.path, args.recursive)
    if not images:
        sys.exit(f"No image files found in {args.path}")

    fields = [f.strip() for f in args.fields.split(",") if f.strip()]
    show_headers = args.path.is_dir()
    records = []

    for path in images:
        label = str(path.relative_to(root)) if show_headers else path.name
        if show_headers and not args.quiet:
            print(f"\n##### {label}")

        try:
            with Image.open(path) as img:
                sections = read_exif(img)
                thumb = None
                if args.contact_sheet:
                    shown = ImageOps.exif_transpose(img).convert("RGB")
                    shown.thumbnail((args.thumb_size, args.thumb_size))
                    thumb = shown
        except Exception as e:
            print(f"Could not read {label}: {e}", file=sys.stderr)
            if args.contact_sheet:
                records.append({"name": label, "sections": {}, "thumb": None})
            continue

        if not args.quiet:
            print_sections(sections)
        records.append({"name": label, "sections": sections, "thumb": thumb})

    if not args.contact_sheet:
        return

    if not records:
        sys.exit("Nothing to put on a contact sheet.")

    for field in fields:
        if not any(lookup_field(r["sections"], field) for r in records):
            print(f"Warning: field '{field}' was not found in any image.",
                  file=sys.stderr)

    per_sheet = max(1, args.per_sheet)
    chunks = [records[i:i + per_sheet] for i in range(0, len(records), per_sheet)]
    paths = sheet_paths(args.output, len(chunks))

    for chunk, out in zip(chunks, paths):
        sheet = build_sheet(chunk, fields, args.columns, args.thumb_size, 14)
        try:
            sheet.save(out)
        except (OSError, ValueError) as e:
            sys.exit(f"Could not save contact sheet {out}: {e}")
        print(f"\nContact sheet saved: {out} ({len(chunk)} images)")


if __name__ == "__main__":
    main()
