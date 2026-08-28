from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_similarity_matrix(baseline_docs, updated_docs):
    """
    Given a list of cleaned baseline and updated sentences,
    calculates the cosine similarity matrix.
    Uses TfidfVectorizer with advanced NLP parameters.
    """
    if not baseline_docs or not updated_docs:
        return np.array([])

    # Advanced TF-IDF as requested
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        lowercase=True,
        min_df=1
    )
    
    # Fit on both sets to ensure vocabulary covers both
    all_docs = baseline_docs + updated_docs
    vectorizer.fit(all_docs)
    
    # Transform separately
    baseline_tfidf = vectorizer.transform(baseline_docs)
    updated_tfidf = vectorizer.transform(updated_docs)
    
    # Compute similarity matrix (shape: len(baseline) x len(updated))
    sim_matrix = cosine_similarity(baseline_tfidf, updated_tfidf)
    
    return sim_matrix
