def extract_text(image_path):

    import pytesseract
    import cv2
    import os

    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if not os.path.isfile(TESSERACT_PATH):
        print("❌ Tesseract not found at:", TESSERACT_PATH)
        return ""

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    print("🔍 OCR Running On:", image_path)

    try:
        image = cv2.imread(image_path)

        if image is None:
            print("❌ Image could not be loaded:", image_path)
            return ""

        # Save debug image to confirm it's correct
        cv2.imwrite("debug_ocr_input.jpg", image)

        # Resize only (NO threshold, NO blur)
        image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        config = r'--oem 3 --psm 4 -l eng'

        text = pytesseract.image_to_string(image, config=config)

        print("📝 OCR Output:", text[:200])  # print first 200 chars

        return text.strip()

    except Exception as e:
        print("❌ OCR Error:", str(e))
        return ""