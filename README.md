# ExifPeek

Reads EXIF metadata (camera details, exposure settings, and GPS data) from a single image or a whole folder of images, prints it to the terminal, and can build a contact sheet of thumbnails labeled with the EXIF fields you choose.

## Features

- Reads one image or every image in a folder, with optional recursion into subfolders
- Prints main image tags (camera make, model, date), Exif tags (exposure, aperture, ISO, focal length, lens), and GPS tags
- Creates a contact sheet of thumbnails with a filename and the EXIF fields of your choice under each one
- Splits large folders across numbered contact sheets
- Skips unreadable files with a warning instead of stopping
- Supports JPEG, TIFF, PNG, and WebP files

## Requirements

- Python 3.7 or newer
- [Pillow](https://pypi.org/project/Pillow/) 9.4 or newer

## Installation

1. Download `read-exif.py` to a folder of your choice.
2. Install Pillow:

   ```
   pip install Pillow
   ```

   If `pip` isn't recognized, use `python -m pip install Pillow` or `pip3 install Pillow`.

## Usage

```
python read-exif.py <path> [options]
```

`<path>` is an image file or a folder. On macOS and Linux, you may need `python3` instead of `python`. Put quotes around any path that contains spaces.

### Read a single image

```
python read-exif.py photo.jpg
```

### Read every image in a folder

```
python read-exif.py ./photos
```

Add `-r` to include subfolders:

```
python read-exif.py ./photos -r
```

Each file's output is preceded by a `##### filename` header. To save the output to a text file:

```
python read-exif.py ./photos > exif.txt
```

### Create a contact sheet

```
python read-exif.py ./photos --contact-sheet
```

This saves `contact_sheet.jpg` in the current folder. Each thumbnail is labeled with its filename and these fields: camera, date, aperture, shutter speed, ISO, and focal length.

Choose your own fields with `--fields`, and the output file with `-o`:

```
python read-exif.py ./photos --contact-sheet --fields camera,lens,iso -o my_sheet.jpg
```

Add `-q` to skip the terminal output and only create the sheet:

```
python read-exif.py ./photos --contact-sheet -q
```

### Options

| Option | Description |
| --- | --- |
| `-r`, `--recursive` | Include images in subfolders |
| `-q`, `--quiet` | Do not print EXIF data to the terminal |
| `--contact-sheet` | Create a contact sheet of thumbnails |
| `-o`, `--output FILE` | Contact sheet file name (default: `contact_sheet.jpg`). Use `.png` for PNG output |
| `--fields LIST` | Comma-separated EXIF fields to print under each thumbnail |
| `--columns N` | Thumbnails per row (default: 5) |
| `--thumb-size N` | Thumbnail size in pixels (default: 240) |
| `--per-sheet N` | Maximum images per sheet (default: 30). Extra sheets are numbered, for example `contact_sheet_001.jpg` |

### Choosing fields

`--fields` accepts these short names:

| Short name | EXIF tag |
| --- | --- |
| `camera` | Model |
| `make` | Make |
| `lens` | LensModel |
| `date` | DateTimeOriginal |
| `iso` | ISOSpeedRatings |
| `aperture` | FNumber |
| `shutter` | ExposureTime |
| `focal` | FocalLength |

You can also use any EXIF tag name, such as `Software` or `WhiteBalance`. Names are not case-sensitive. A tag that isn't found in any image produces a warning, and images without a value for a field simply leave that line out.

## Example output

```
##### photo1.jpg

=== Main ===
Model                        Canon EOS 80D
Make                         Canon

=== Exif ===
DateTimeOriginal             2026:05:14 18:32:07
ExposureTime                 0.004
FNumber                      5.6
ISOSpeedRatings              200
FocalLength                  85.0
```

The values above are only an illustration. The tags you see depend on the camera and on what each photo's metadata contains.

## Notes

- Many photos have no EXIF data, especially images that were edited, screenshotted, or stripped by messaging apps and social media sites. These appear on the contact sheet with "No EXIF data".
- Thumbnails are rotated to match each photo's orientation tag.
- GPS coordinates are printed as raw degree/minute/second values, with the N/S and E/W reference stored in separate tags.
- HEIC files aren't supported without extra plugins.

## Troubleshooting

| Problem | Likely cause and fix |
| --- | --- |
| `can't open file ... [Errno 2] No such file or directory` | Python can't find `read-exif.py`. Run the command from the script's folder, or give its full path. |
| `Path not found: ...` | The image or folder path is wrong. Check the spelling and give the full path if needed. |
| `No image files found in ...` | The folder has no supported images. Try `-r` if they are in subfolders. |
| `ModuleNotFoundError: No module named 'PIL'` | Pillow isn't installed. Run `pip install Pillow`. |
| `AttributeError: ... has no attribute 'IFD'` | Your Pillow version is too old. Run `pip install --upgrade Pillow`. |
| `Warning: field 'x' was not found in any image` | The field name is misspelled or none of the images contain that tag. |

## License

Add your preferred license here (for example, MIT).
