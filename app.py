from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import faiss
import numpy as np

app = Flask(__name__)
app.static_folder = 'static'

# Initialize models
embedder = SentenceTransformer('all-MiniLM-L6-v2')
qa_pipeline = pipeline('question-answering', model='deepset/roberta-base-squad2')

# Storage variables
chunks = []
index = None

def scrape_and_process(urls):
    global chunks, index
    chunks = []
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = ' '.join(soup.get_text().split())
            # Split text into 500-character chunks
            chunks.extend([text[i:i+500] for i in range(0, len(text), 500)])
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
    
    if chunks:
        # Create FAISS index
        embeddings = embedder.encode(chunks)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings.astype('float32'))
    
    return len(chunks)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ingest', methods=['POST'])
def ingest_urls():
    data = request.get_json()
    num_chunks = scrape_and_process(data['urls'])
    return jsonify({
        'message': f'Processed {num_chunks} text chunks from {len(data["urls"])} URLs'
    })

@app.route('/ask', methods=['POST'])
def answer_question():
    data = request.get_json()
    question = data['question']
    
    # Convert question to embedding
    question_embed = embedder.encode([question])
    
    # Search FAISS index
    _, indices = index.search(question_embed.astype('float32'), k=3)
    
    # Get relevant chunks
    relevant_chunks = [chunks[i] for i in indices[0]]
    
    # Get answers from all relevant chunks
    answers = []
    for chunk in relevant_chunks:
        result = qa_pipeline(question=question, context=chunk)
        if result['score'] > 0.1:  # Confidence threshold
            answers.append((result['answer'], result['score']))
    
    return jsonify({
        'answer': max(answers, key=lambda x: x[1])[0] if answers else 'No answer found'
    })

if __name__ == '__main__':
    app.run(debug=True)