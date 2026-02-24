from pdf2image import convert_from_path
import os

def convert_pdf_to_image(pdf_path):

    poppler_path = r"C:\poppler\Library\bin"  # <-- Adjust if needed

    pages = convert_from_path(
        pdf_path,
        poppler_path=poppler_path
    )

    image_path = pdf_path.replace(".pdf", ".jpg")

    pages[0].save(image_path, "JPEG")

    return image_path