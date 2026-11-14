# ExifPeek

Reads a JPEG file's EXIF metadata (camera details, exposure settings, and GPS data) and prints it to the terminal.

## Features

- Prints main image tags such as camera make, model, date, and orientation
- Prints Exif tags such as exposure time, aperture, ISO, focal length, and lens
- Prints GPS tags such as latitude, longitude, and altitude, when present
- Shows readable tag names instead of numeric IDs
- Reports a clear message when a file has no EXIF data or can't be opened

## Requirements

- Python 3.7 or newer
- [Pillow](https://pypi.org/project/Pillow/) 9.4 or newer

## Installation

1. Download `read_exif.py` to a folder of your choice.
2. Install Pillow:

   ```
   pip install Pillow
   ```

   If `pip` isn't recognized, use `python -m pip install Pillow` or `pip3 install Pillow`.

## Usage

```
python read_exif.py <image.jpg>
```

On macOS and Linux, you may need to use `python3` instead of `python`.

If the script and the image are in different folders, give the full path to each:

```
python "C:\Users\YourName\Downloads\read_exif.py" "C:\Users\YourName\Pictures\photo.jpg"
```

Put quotes around any path that contains spaces.

To save the output to a text file:

```
python read_exif.py photo.jpg > exif.txt
```

## Example output

```
=== Main ===
Make                         Canon
Model                        Canon EOS 80D
Orientation                  1
DateTime                     2026:05:14 18:32:07

=== Exif ===
ExposureTime                 0.004
FNumber                      5.6
ISOSpeedRatings              200
FocalLength                  85.0

=== GPS ===
GPSLatitudeRef               N
GPSLatitude                  (47.0, 51.0, 12.3)
GPSLongitudeRef              W
GPSLongitude                 (122.0, 10.0, 45.6)
```

The values above are only an illustration. The tags you see depend on the camera and on what the photo's metadata contains.

## Notes

- Many photos have no EXIF data, especially images that were edited, screenshotted, or stripped by messaging apps and social media sites.
- GPS coordinates are printed as raw degree/minute/second values, with the N/S and E/W reference stored in separate tags.
- Only the first image in the file is read.

## Troubleshooting

| Problem | Likely cause and fix |
| --- | --- |
| `can't open file ... [Errno 2] No such file or directory` | Python can't find `read_exif.py`. Run the command from the script's folder, or give its full path. |
| `File not found: photo.jpg` | The image path is wrong. Check the filename and give the full path if needed. |
| `ModuleNotFoundError: No module named 'PIL'` | Pillow isn't installed. Run `pip install Pillow`. |
| `AttributeError: ... has no attribute 'IFD'` | Your Pillow version is too old. Run `pip install --upgrade Pillow`. |
| `No EXIF data found.` | The image has no EXIF metadata. |

