from rank_bm25 import BM25Okapi
import jieba
import numpy as np
import logging

class BM25IndexManager:
    def __init__(self):
        self.bm25_index = None
        self.doc_mapping = {}
        self.tokenized_corpus = []
        self.raw_corpus = []
    def build_index(self, documents, doc_ids):
        self.raw_corpus = documents
        self.doc_mapping = {i: doc_id for i, doc_id in enumerate(doc_ids)}
        self.tokenized_corpus = [list(jieba.cut(doc)) for doc in documents]
        self.bm25_index = BM25Okapi(self.tokenized_corpus)
        return True
    def search(self, query, top_k=5):
        if not self.bm25_index:
            return []
        tokenized_query = list(jieba.cut(query))
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        top_indices = np.argsort(bm25_scores)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if bm25_scores[idx] > 0:
                results.append({
                    'id': self.doc_mapping[idx],
                    'score': float(bm25_scores[idx]),
                    'content': self.raw_corpus[idx]
                })
        return results
    def clear(self):
        self.bm25_index = None
        self.doc_mapping = {}
        self.tokenized_corpus = []
        self.raw_corpus = []

BM25_MANAGER = BM25IndexManager() 