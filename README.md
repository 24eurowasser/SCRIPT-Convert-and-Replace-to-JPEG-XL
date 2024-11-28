# Convert-and-Replace-to-JPEG-XL 🦭
This script identifies suitable images for JPEG XL conversion, preserving original metadata. 
It adds the original filename as a title tag to the image's EXIF data.

# Important! 🫵👁️👄👁️
This script will **delete** the old image files after conversion. It will also **overwrite** previous exif title tags.

# Usage
```
python <complete path to this main.py> <complete path to a directory containing images>
```

# JPEG XL Settings
These settings are used for conversion:
```
--distance 0 --effort 10 --lossless_jpeg 1 --allow_jpeg_reconstruction 0
```

# Requirements
- Python 3.X
- PATH installation of exiftool version from 10.07.2024 (🌍 Website to exiftool https://exiftool.org)
- PATH installation of JPEG XL Reference Implementation v0.11.0 (🌍 Website to JPEG XL: https://github.com/libjxl/libjxl)
- PATH installation of ImageMagick 7.1.1-39 (🌍 Website to ImageMagick: https://imagemagick.org)

# License
You are free to use and modify this script. However, please do not:
- Use this code for commercial purposes.
- Copy or modify this code without giving credit.
