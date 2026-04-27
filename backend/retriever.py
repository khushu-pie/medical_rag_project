import chromadb
import torch
import open_clip
from sentence_transformers import SentenceTransformer
from PIL import Image
import os

class MultiModalRetriever:
    def __init__(self, db_path="./chroma_db"):
        print("Initializing ChromaDB Persistent Client...")
        self.client = chromadb.PersistentClient(path=db_path)
        
        self.text_collection = self.client.get_or_create_collection(name="text_docs")
        self.image_collection = self.client.get_or_create_collection(name="image_docs")
        
        print("Loading Text Embedding Model (all-MiniLM-L6-v2)...")
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("Loading Image Embedding Model (OpenCLIP ViT-B-32)...")
        self.clip_model, _, self.clip_preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')

    def index_text(self, chunks):
        if not chunks: return
        ids = [c["id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        
        embeddings = self.text_model.encode(texts).tolist()
        
        self.text_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def index_images(self, image_records):
        if not image_records: return
        ids = []
        embeddings = []
        metadatas = []
        
        for record in image_records:
            try:
                image = Image.open(record["path"]).convert("RGB")
                image_input = self.clip_preprocess(image).unsqueeze(0)
                
                with torch.no_grad():
                    image_features = self.clip_model.encode_image(image_input)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
                
                ids.append(record["id"])
                embeddings.append(image_features[0].tolist())
                # Add path to metadata so it can be retrieved
                meta = record["metadata"].copy()
                meta["path"] = record["path"]
                metadatas.append(meta)
            except Exception as e:
                print(f"Failed to index image {record['path']}: {e}")
                
        if ids:
            self.image_collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas
            )

    def search(self, query, top_k=3):
        results = {"texts": [], "images": []}
        
        # 1. Search text collection if not empty
        if self.text_collection.count() > 0:
            text_emb = self.text_model.encode([query]).tolist()
            text_results = self.text_collection.query(
                query_embeddings=text_emb,
                n_results=min(top_k, self.text_collection.count())
            )
            
            if text_results["documents"] and len(text_results["documents"][0]) > 0:
                for i in range(len(text_results["documents"][0])):
                    results["texts"].append({
                        "text": text_results["documents"][0][i],
                        "metadata": text_results["metadatas"][0][i] if text_results["metadatas"] else {}
                    })

        # 2. Search image collection if not empty
        if self.image_collection.count() > 0:
            text_tokens = self.tokenizer([query])
            with torch.no_grad():
                clip_text_features = self.clip_model.encode_text(text_tokens)
                clip_text_features /= clip_text_features.norm(dim=-1, keepdim=True)
                
            image_results = self.image_collection.query(
                query_embeddings=clip_text_features.tolist(),
                n_results=min(top_k, self.image_collection.count())
            )
            
            if image_results["metadatas"] and len(image_results["metadatas"][0]) > 0:
                for i in range(len(image_results["metadatas"][0])):
                    results["images"].append({
                        "metadata": image_results["metadatas"][0][i]
                    })
                    
        return results

# Singleton instance
retriever = None

def get_retriever():
    global retriever
    if retriever is None:
        retriever = MultiModalRetriever()
    return retriever
