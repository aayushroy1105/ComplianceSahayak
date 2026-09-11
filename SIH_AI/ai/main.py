import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import router
from api.errors import AIAPIException, ai_api_exception_handler
from core.config import settings
from services.applicability.catalogue import LegalRuleCatalogue

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.catalogue = LegalRuleCatalogue()
    rules_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "legal_metrology_rules.md")
    try:
        app.state.catalogue.load(rules_path)
    except FileNotFoundError:
        print(f"Warning: Legal rules file not found at {rules_path}")

    from clients.ocr_client import OCRClient
    from services.extraction.extractor import DeclarationExtractor
    from services.classification.product_classifier import ProductClassifier
    from services.classification.context_classifier import ContextClassifier
    from services.applicability.engine import ApplicabilityEngine
    from services.rag.embeddings import EmbeddingService
    from services.rag.indexer import LegalIndexer
    from services.rag.retriever import Retriever
    from services.rules.engine import RuleEngine
    from services.llm.generator import LLMGenerator

    app.state.ocr_client = OCRClient()
    app.state.extractor = DeclarationExtractor()
    app.state.product_classifier = ProductClassifier()
    app.state.context_classifier = ContextClassifier()
    app.state.applicability_engine = ApplicabilityEngine(app.state.catalogue)
    
    app.state.embedding_service = EmbeddingService()
    # Note: the embedding service might need await initialize() if we were doing remote embeddings, 
    # but currently it defaults to SentenceTransformers locally or mock. 
    # For Phase 10 we stick to existing behavior.
    
    app.state.indexer = LegalIndexer(app.state.catalogue, app.state.embedding_service)
    # We do not build index on request, but on startup if it's stale. 
    # However, Phase 10 specifically states: "Do not rebuild the RAG index during request processing."
    # If it's stale at startup, we could build it, but maybe just let Retriever handle empty.
    
    app.state.retriever = Retriever(app.state.indexer, app.state.embedding_service)
    app.state.rule_engine = RuleEngine()
    app.state.llm_generator = LLMGenerator()

    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Service for Legal Metrology Packaged Commodity Compliance System",
    lifespan=lifespan
)

app.add_exception_handler(AIAPIException, ai_api_exception_handler)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
