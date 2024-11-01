# Convert-and-Replace-to-JPEG-XL
This script identifies suitable images for JPEG XL conversion, preserving original metadata. 
It adds the original filename as a title tag to the image's EXIF data.

# Usage
```
python <complete path to this main.py> <complete path to a directory containing images>
```

# Important!
This script will delete the old image files after conversion. It will also overwrite previous exif title tags.

# Requirements
- Python 3.X
- PATH installation of exiftool version from 10.07.2024 (🌍 Website to exiftool https://exiftool.org)
- PATH installation of JPEG XL Reference Implementation v0.11.0 (🌍 Website to JPEG XL: https://github.com/libjxl/libjxl)