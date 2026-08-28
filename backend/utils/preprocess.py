import re
import string
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure resources are available
try:
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
except LookupError:
    # Fallback if not downloaded (though app.py handles it)
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

def get_sentences(text):
    """Parse text into list of dicts: [{'id': 'REQ-001', 'text': '...'}]"""
    if not text or not text.strip():
        return []
    
    # Try to split by explicit tags like REQ-001, FR-01, NFR-100
    if re.search(r'\b[A-Z]{2,4}-\d+', text):
        chunks = re.split(r'(?=\b[A-Z]{2,4}-\d+)', text)
        reqs = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                match = re.match(r'^([A-Z]{2,4}-\d+)[^\w]*(.*)', chunk, re.DOTALL)
                if match:
                    req_id = match.group(1)
                    req_text = match.group(2).strip()
                    req_text = re.split(r'\n\s*(?:\d+\.\s+)?[A-Z][A-Z0-9\s\-]{5,}(?:\n|$)', req_text)[0]
                    req_text = req_text.replace('\n', ' ').strip()
                    reqs.append({"id": req_id, "text": req_text})
        return reqs
        
    chunks = re.split(r'\n\s*\n', text.strip())
    reqs = []
    for chunk in chunks:
        if chunk.strip():
            reqs.append({"id": None, "text": chunk.strip().replace('\n', ' ')})
    return reqs

def clean_text(text):
    """
    Lowercases, removes punctuation (but preserves numbers like 99.9% and 500), removes stopwords, and lemmatizes the text.
    """
    text = text.lower()
    
    # Custom punctuation removal that preserves numbers like 99.9 and percentages
    # Replace anything that is not alphanumeric, dot, or percent with space
    text = re.sub(r'[^\w\s\.%]', ' ', text)
    
    words = word_tokenize(text)
    cleaned_words = [
        lemmatizer.lemmatize(w) for w in words if w not in stop_words
    ]
    return " ".join(cleaned_words)
