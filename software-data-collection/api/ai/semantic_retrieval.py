from sklearn.neighbors import NearestNeighbors


class SemanticSimilarityCalculator:
    def __init__(self, embeddings_chunks, n_neighbors=5):
        self.embeddings = []
        self.chunks = []
        for d in embeddings_chunks:
            self.embeddings.append(d["embedding"])
            self.chunks.append(d["chunk"])

        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)

    def retrieve_top_chunks(self, question_embedding):
        neighbors = self.nn.kneighbors(question_embedding, return_distance=False)[0]
        return [self.chunks[i] for i in neighbors]
