import fitz
from PIL import Image
import pytesseract
import io

# Tell Python where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_pdf_text(pdf_path):
    document = fitz.open(pdf_path)

    complete_text = ""

    for page_number, page in enumerate(document, start=1):

        # First try normal PDF text extraction
        text = page.get_text()

        if text.strip():
            print(f"Page {page_number}: Text extracted")
            complete_text += text + "\n"

        else:
            # If no text exists, use OCR
            print(f"Page {page_number}: OCR processing...")

            pix = page.get_pixmap(dpi=200)

            image_bytes = pix.tobytes("png")

            image = Image.open(io.BytesIO(image_bytes))

            ocr_text = pytesseract.image_to_string(image)

            complete_text += ocr_text + "\n"

    document.close()

    return complete_text


if __name__ == "__main__":

    pdf_path = "scanned_sample.pdf"

    text = extract_pdf_text(pdf_path)

    print("\n========== EXTRACTED TEXT ==========\n")
    print(text)