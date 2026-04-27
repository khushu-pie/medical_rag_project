import google.generativeai as genai
import os

def generate_response(query, context):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable is not set."
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""You are a helpful AI assistant answering medical-related queries based ONLY on the provided context.
    
    CONTEXT:
    """
    
    if context.get("texts"):
        prompt += "\n--- TEXT CONTEXT ---\n"
        for i, t in enumerate(context["texts"]):
            prompt += f"[Source: {t['metadata'].get('source', 'unknown')}, Page: {t['metadata'].get('page', 'N/A')}]: {t['text']}\n\n"
            
    if context.get("images"):
        prompt += "\n--- IMAGE CONTEXT ---\n"
        for i, img in enumerate(context["images"]):
            prompt += f"[Image related to query found in {img['metadata'].get('source', 'unknown')} at Page {img['metadata'].get('page', 'N/A')}]\n"
            
    prompt += f"""
    ---
    USER QUERY: {query}
    
    INSTRUCTIONS:
    1. Answer the user's query clearly and concisely based ONLY on the provided context.
    2. If the context does not contain the answer, state that you cannot find the answer in the uploaded documents.
    3. You must ALWAYS include this exact medical disclaimer at the very end of your response, on a new line: "This is not a substitute for professional medical advice"
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I encountered an error while generating a response. Please try again later.\n\nThis is not a substitute for professional medical advice"
