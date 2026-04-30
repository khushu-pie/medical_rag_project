from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
from ingestion import process_pdf, process_image
from retriever import get_retriever
from llm import generate_response
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Medical RAG API")

# Allow all origins for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/docs", exist_ok=True)
os.makedirs("uploads/images", exist_ok=True)

@app.on_event("startup")
async def startup_event():
    # Initialize retriever on startup to preload heavy ML models
    print("Pre-loading models...")
    get_retriever()
    print("Models loaded successfully.")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_ext = file.filename.split('.')[-1].lower()
        file_path = f"uploads/docs/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        retriever = get_retriever()
            
        if file_ext == 'pdf':
            text_chunks, image_records = process_pdf(file_path, file.filename, "uploads/images")
            retriever.index_text(text_chunks)
            retriever.index_images(image_records)
            return {"message": f"Successfully processed and indexed PDF: {file.filename}"}
            
        elif file_ext in ['jpg', 'jpeg', 'png']:
            img_path = f"uploads/images/{file.filename}"
            # move from docs to images
            shutil.move(file_path, img_path)
            text_chunks, image_records = process_image(img_path, file.filename)
            retriever.index_text(text_chunks)
            retriever.index_images(image_records)
            return {"message": f"Successfully processed and indexed Image: {file.filename}"}
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, JPG, or PNG.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post("/query")
async def query_system(query: str = Form(...)):
    try:
        retriever = get_retriever()
        context = retriever.search(query, top_k=3)
        response = generate_response(query, context)
        return {"answer": response, "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/clear")
async def clear_data():
    try:
        retriever = get_retriever()
        retriever.clear()
        
        # Clear files in uploads directories
        for folder in ["uploads/docs", "uploads/images"]:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")
                        
        return {"message": "All documents and data have been cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

@app.get("/")
async def root():
    return {"status": "Backend is running"}
