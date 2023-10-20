import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(settings.SIMILARITY_MODEL_PATH)

    def get_text_embedding(self, texts, batch=1000):
        embeddings = []
        for i in range(0, len(texts), batch):
            text_batch = texts[i : (i + batch)]
            emb_batch = self.model.encode(text_batch)
            embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings