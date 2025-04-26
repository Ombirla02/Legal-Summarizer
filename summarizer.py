import fitz  
from transformers import pipeline
import torch
device = -1 
print(f"Using device: {'GPU' if device == 0 else 'CPU'}")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error opening or reading PDF with fitz: {e}")
        
        return None 
    return text


def summarize_text(text, max_chunk_length=1024): 
    if not text:
        return "Input text is empty or could not be read."
    words = text.split()
    max_words_per_chunk = 600
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_words_per_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk: 
        chunks.append(" ".join(current_chunk))

    if not chunks:
        return "Input text processed into zero chunks."
    full_summary = ""
    try:
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i+1}/{len(chunks)}...")
            
            
            chunk_summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
            full_summary += chunk_summary[0]['summary_text'] + "\n\n" 
    except Exception as e:
        print(f"Error during summarization: {e}")
        return f"Error during summarization: {e}" 

    return full_summary.strip() 

