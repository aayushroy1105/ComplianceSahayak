import os

DEFAULT_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

class EmbeddingService:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.model = None

    def initialize(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        self.initialize()
        embeddings = self.model.encode(texts, show_progress_bar=False)
        if isinstance(embeddings, list):
            return embeddings
        return embeddings.tolist()
        
    def get_signature(self) -> str:
        return self.model_name
