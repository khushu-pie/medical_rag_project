import fitz  # PyMuPDF
import os
import uuid
import google.generativeai as genai
from PIL import Image

def extract_text_with_gemini(image_path):
    """Uses Gemini to perform OCR and extract handwritten/printed text from an image."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not set. Skipping OCR.")
            return ""
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        img = Image.open(image_path)
        prompt = "Please extract all the text from this image exactly as it is written. If it is a medical prescription, make sure to transcribe the medicine names, dosages, and instructions accurately. Do not add any conversational text, just return the transcribed text."
        
        response = model.generate_content([prompt, img])
        return response.text.strip()
    except Exception as e:
        print(f"OCR Error for {image_path}: {e}")
        return ""

def process_pdf(file_path, original_filename, image_dir="uploads/images"):
    """Extracts text and images from a PDF file."""
    os.makedirs(image_dir, exist_ok=True)
    text_chunks = []
    image_records = []

    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract Text
            text = page.get_text("text")
            if text.strip():
                text_chunks.append({
                    "id": f"txt_{uuid.uuid4().hex}",
                    "text": text.strip(),
                    "metadata": {"source": original_filename, "page": page_num + 1, "type": "text"}
                })

            # Extract Images
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                image_filename = f"img_{uuid.uuid4().hex}.{image_ext}"
                image_path = os.path.join(image_dir, image_filename)
                
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                    
                image_records.append({
                    "id": f"img_{uuid.uuid4().hex}",
                    "path": image_path,
                    "metadata": {"source": original_filename, "page": page_num + 1, "type": "image"}
                })
        doc.close()
    except Exception as e:
        print(f"Error processing PDF {original_filename}: {e}")

    return text_chunks, image_records

def process_image(file_path, original_filename):
    """Processes a direct image upload and extracts text using OCR."""
    image_records = [{
        "id": f"img_{uuid.uuid4().hex}",
        "path": file_path,
        "metadata": {"source": original_filename, "type": "image"}
    }]
    
    text_chunks = []
    print(f"Extracting text from image {original_filename}...")
    extracted_text = extract_text_with_gemini(file_path)
    
    if extracted_text:
        print(f"Successfully extracted text from {original_filename}")
        text_chunks.append({
            "id": f"txt_{uuid.uuid4().hex}",
            "text": f"[Image Transcription of {original_filename}]:\n{extracted_text}",
            "metadata": {"source": original_filename, "type": "text_from_image"}
        })
        
    return text_chunks, image_records
