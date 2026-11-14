#!/usr/bin/env python3
"""Read and print EXIF data from a JPEG file.

Usage:
    python read_exif.py photo.jpg

Requires Pillow:
    pip install Pillow
"""

import sys

from PIL import ExifTags, Image


def format_value(value):
    """Make raw EXIF values readable."""
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace").strip("\x00").strip()
        return text if text.isprintable() else f"<{len(value)} bytes>"
    return value


def print_ifd(title, ifd, tag_names):
    """Print one block of EXIF tags."""
    if not ifd:
        return
    print(f"\n=== {title} ===")
    for tag_id, value in ifd.items():
        name = tag_names.get(tag_id, f"Unknown (0x{tag_id:04x})")
        print(f"{name:<28} {format_value(value)}")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <image.jpg>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        with Image.open(path) as img:
            exif = img.getexif()
    except FileNotFoundError:
        sys.exit(f"File not found: {path}")
    except Exception as e:
        sys.exit(f"Could not open image: {e}")

    if not exif:
        print("No EXIF data found.")
        return

    # Main image tags (camera make/model, orientation, date, etc.)
    print_ifd("Main", dict(exif), ExifTags.TAGS)

    # Exif sub-IFD (exposure, ISO, lens, focal length, etc.)
    print_ifd("Exif", exif.get_ifd(ExifTags.IFD.Exif), ExifTags.TAGS)

    # GPS sub-IFD (latitude, longitude, altitude, etc.)
    print_ifd("GPS", exif.get_ifd(ExifTags.IFD.GPSInfo), ExifTags.GPSTAGS)


if __name__ == "__main__":
    main()
