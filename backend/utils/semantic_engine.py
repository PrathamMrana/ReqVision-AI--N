"""
backend/utils/semantic_engine.py

Semantic Embedding Engine for ReqVision AI Phase 3.

Loads sentence-transformers/all-MiniLM-L6-v2 once (lazy singleton).
Provides real dense vector embeddings and cosine similarity.

RULES:
- Model loaded once, reused for all comparisons in a session.
- Embeddings cached by normalized text hash (LRU).
- Returns None (not 0.0) when model is unavailable.
- Never fabricates scores.
- V1 /api/compare never touches this module.
"""

import re
import hashlib
import logging
import numpy as np
from functools import lru_cache

logger = logging.getLogger("ReqVision-SemanticEngine")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
HF_MODEL_ID = "all-MiniLM-L6-v2"

# Negation / polarity words that must NOT be stripped during preprocessing
_PRESERVE_WORDS = {
    "not", "never", "no", "only", "except", "unless", "without",
    "prohibited", "forbidden", "prevent", "disallow", "deny",
    "required", "mandatory", "must", "shall", "optional",
    "instead", "replace", "before", "after", "until"
}


class SemanticEngine:
    """
    Singleton semantic embedding engine.
    Loads all-MiniLM-L6-v2 once and caches embeddings by text hash.
    """

    _instance = None
    _model = None
    _available = False
    _embedding_cache: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _initialize(self):
        if self._initialized:
            return
        self._initialized = True
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"[SemanticEngine] Loading model: {HF_MODEL_ID}")
            try:
                self.__class__._model = SentenceTransformer(HF_MODEL_ID)
            except Exception:
                self.__class__._model = SentenceTransformer(MODEL_NAME)
            self.__class__._available = True
            logger.info(f"[SemanticEngine] Model loaded successfully: {MODEL_NAME}")
        except ImportError:
            logger.warning("[SemanticEngine] sentence-transformers not installed. Falling back to lexical mode.")
            self.__class__._available = False
        except Exception as e:
            logger.warning(f"[SemanticEngine] Model load failed: {e}. Falling back to lexical mode.")
            self.__class__._available = False

    def is_available(self) -> bool:
        self._initialize()
        return self.__class__._available

    @property
    def model_name(self) -> str:
        return MODEL_NAME

    def normalize_for_embedding(self, text: str) -> str:
        """
        Normalize text for embedding.
        Preserves: negation words, numbers, percentages, units.
        Removes: excess whitespace, non-alphanumeric noise (but keeps words).
        Does NOT aggressively stem or remove meaningful words.
        """
        if not text:
            return ""
        # Lowercase
        t = text.lower().strip()
        # Collapse multiple whitespace
        t = re.sub(r'\s+', ' ', t)
        # Remove control characters but keep alphanumeric, punctuation, spaces
        t = re.sub(r'[^\w\s\.\,\!\?\-\%\(\)\/]', ' ', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    def _text_hash(self, text: str) -> str:
        normalized = self.normalize_for_embedding(text)
        return hashlib.md5(normalized.encode("utf-8", errors="replace")).hexdigest()

    def compute_embedding(self, text: str):
        """
        Returns normalized embedding vector for text, or None if unavailable.
        Caches by normalized text hash.
        """
        self._initialize()
        if not self._available or not text or not text.strip():
            return None

        cache_key = self._text_hash(text)
        if cache_key in self.__class__._embedding_cache:
            return self.__class__._embedding_cache[cache_key]

        try:
            normalized = self.normalize_for_embedding(text)
            emb = self.__class__._model.encode([normalized], normalize_embeddings=True)[0]
            self.__class__._embedding_cache[cache_key] = emb
            return emb
        except Exception as e:
            logger.warning(f"[SemanticEngine] Embedding error: {e}")
            return None

    def batch_embed(self, texts: list):
        """
        Batch embed a list of texts. Returns list of embeddings (or None entries).
        Uses cache for already-computed texts.
        """
        self._initialize()
        if not self._available:
            return [None] * len(texts)

        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []

        for i, text in enumerate(texts):
            cache_key = self._text_hash(text)
            if cache_key in self.__class__._embedding_cache:
                results[i] = self.__class__._embedding_cache[cache_key]
            else:
                uncached_indices.append(i)
                uncached_texts.append(self.normalize_for_embedding(text))

        if uncached_texts:
            try:
                embeddings = self.__class__._model.encode(
                    uncached_texts, normalize_embeddings=True, batch_size=32
                )
                for idx, emb in zip(uncached_indices, embeddings):
                    cache_key = self._text_hash(texts[idx])
                    self.__class__._embedding_cache[cache_key] = emb
                    results[idx] = emb
            except Exception as e:
                logger.warning(f"[SemanticEngine] Batch embed error: {e}")

        return results

    def compute_semantic_similarity(self, text_a: str, text_b: str):
        """
        Returns cosine similarity in [0, 1] between two texts.
        Returns None if model is unavailable or either text is empty.
        NEVER returns a fabricated score.
        """
        self._initialize()
        if not self._available:
            return None
        if not text_a or not text_a.strip() or not text_b or not text_b.strip():
            return None

        emb_a = self.compute_embedding(text_a)
        emb_b = self.compute_embedding(text_b)

        if emb_a is None or emb_b is None:
            return None

        # Since embeddings are L2-normalized, dot product = cosine similarity
        sim = float(np.dot(emb_a, emb_b))
        # Clamp to [0, 1] (cosine can theoretically be slightly negative for unrelated text)
        return max(0.0, min(1.0, sim))

    def cache_stats(self) -> dict:
        return {"cached_embeddings": len(self.__class__._embedding_cache), "model_available": self._available}
