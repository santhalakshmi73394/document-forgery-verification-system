from PIL import Image
from PIL.ExifTags import TAGS

def analyze_metadata(image_path):

    suspicious_software = [
        "photoshop",
        "gimp",
        "canva",
        "pixlr",
        "snapseed"
    ]

    try:
        image = Image.open(image_path)
        exif_data = image._getexif()

        if not exif_data:
            return False, "No EXIF metadata found"

        metadata = {}

        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            metadata[tag_name] = str(value)

        software_used = metadata.get("Software", "").lower()

        for tool in suspicious_software:
            if tool in software_used:
                return True, f"Edited using {software_used}"

        return False, "No suspicious software detected"

    except Exception:
        return False, "Metadata extraction failed"