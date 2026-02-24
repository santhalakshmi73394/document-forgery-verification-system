from PIL import Image, ImageChops
import numpy as np
import cv2
import os

def ela_score(image_path):

    original = Image.open(image_path).convert("RGB")

    temp_path = image_path + ".temp.jpg"
    original.save(temp_path, "JPEG", quality=90)

    compressed = Image.open(temp_path)

    diff = ImageChops.difference(original, compressed)

    diff_np = np.array(diff)

    gray = cv2.cvtColor(diff_np, cv2.COLOR_BGR2GRAY)

    # Normalize
    norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    # Threshold to detect suspicious regions
    _, thresh = cv2.threshold(norm, 40, 255, cv2.THRESH_BINARY)

    # Create red overlay
    overlay = np.zeros_like(diff_np)
    overlay[:, :, 2] = thresh  # red channel

    original_np = np.array(original)

    # Blend original + red overlay
    highlighted = cv2.addWeighted(original_np, 0.8, overlay, 0.5, 0)

    # Save highlighted image
    heatmap_path = image_path.rsplit(".", 1)[0] + "_heatmap.jpg"
    cv2.imwrite(heatmap_path, highlighted)

    os.remove(temp_path)

    score = np.mean(norm) / 255

    return score, heatmap_path