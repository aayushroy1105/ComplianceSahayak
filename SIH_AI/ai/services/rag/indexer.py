import os
import chromadb
from typing import List, Dict, Any, Tuple
from services.applicability.catalogue import LegalRuleCatalogue, LegalRule
from services.rag.embeddings import EmbeddingService
from core.logging import log_event

CHUNKING_VERSION = "v1"
COLLECTION_NAME = "legal_metrology_corpus"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_DIR = os.getenv("CHROMADB_DIR", os.path.join(PROJECT_ROOT, ".chroma_db"))

class Chunk:
    def __init__(self, text: str, rule_id: str, rule_number: str, source_document: str, source_section: str, chunk_index: int):
        self.text = text
        self.rule_id = rule_id
        self.rule_number = rule_number
        self.source_document = source_document
        self.source_section = source_section
        self.chunk_index = chunk_index

class LegalIndexer:
    def __init__(self, catalogue: LegalRuleCatalogue, embedding_service: EmbeddingService):
        self.catalogue = catalogue
        self.embedding_service = embedding_service
        self.client = chromadb.PersistentClient(path=DB_DIR)

    def _get_signature(self) -> str:
        return f"{self.catalogue.file_hash}_{self.embedding_service.get_signature()}_{CHUNKING_VERSION}"

    def check_stale(self) -> bool:
        """Returns True if the current index doesn't match the signature, or doesn't exist."""
        try:
            collection = self.client.get_collection(COLLECTION_NAME)
            metadata = collection.metadata
            if metadata and metadata.get("signature") == self._get_signature():
                return False
            return True
        except ValueError:
            return True

    def health_check(self) -> bool:
        """Lightweight deterministic check to verify the index is present and queryable."""
        try:
            if self.check_stale():
                return False
            
            collection = self.client.get_collection(COLLECTION_NAME)
            # Try a lightweight operation: count the documents
            count = collection.count()
            if count > 0:
                return True
            return False
        except Exception:
            return False

    def _chunk_rule(self, rule: LegalRule) -> List[Chunk]:
        chunks = []
        
        meta_text = f"Rule Title: {rule.title}\nCategory: {rule.category}\nApplicability: {rule.applicability}"
        chunks.append(Chunk(
            text=meta_text,
            rule_id=rule.rule_id,
            rule_number=rule.title,
            source_document="legal_metrology_rules.md",
            source_section="Metadata",
            chunk_index=0
        ))
        
        paragraphs = [p.strip() for p in rule.raw_text.split("\n\n") if p.strip()]
        current_chunk_text = ""
        current_section = "General"
        chunk_idx = 1
        
        for p in paragraphs:
            if p.startswith("### "):
                if current_chunk_text:
                    chunks.append(Chunk(
                        text=current_chunk_text,
                        rule_id=rule.rule_id,
                        rule_number=rule.title,
                        source_document="legal_metrology_rules.md",
                        source_section=current_section,
                        chunk_index=chunk_idx
                    ))
                    chunk_idx += 1
                    current_chunk_text = ""
                current_section = p.replace("### ", "").strip()
                current_chunk_text = p + "\n"
            else:
                current_chunk_text += p + "\n\n"
                if len(current_chunk_text) > 2000:
                    chunks.append(Chunk(
                        text=current_chunk_text.strip(),
                        rule_id=rule.rule_id,
                        rule_number=rule.title,
                        source_document="legal_metrology_rules.md",
                        source_section=current_section,
                        chunk_index=chunk_idx
                    ))
                    chunk_idx += 1
                    current_chunk_text = ""
                    
        if current_chunk_text.strip():
            chunks.append(Chunk(
                text=current_chunk_text.strip(),
                rule_id=rule.rule_id,
                rule_number=rule.title,
                source_document="legal_metrology_rules.md",
                source_section=current_section,
                chunk_index=chunk_idx
            ))
            
        return chunks

    def build_index(self):
        log_event("indexer_build_start", signature=self._get_signature())
        
        all_chunks = []
        for rule in self.catalogue.all():
            all_chunks.extend(self._chunk_rule(rule))
            
        if not all_chunks:
            log_event("indexer_build_empty")
            return
            
        staging_name = f"{COLLECTION_NAME}_staging"
        try:
            self.client.delete_collection(staging_name)
        except Exception:
            pass
            
        staging_collection = self.client.create_collection(
            name=staging_name,
            metadata={"signature": self._get_signature()}
        )
        
        texts = [c.text for c in all_chunks]
        ids = [f"{c.rule_id}_{c.chunk_index}" for c in all_chunks]
        metadatas = [{
            "rule_id": c.rule_id,
            "rule_number": c.rule_number,
            "source_document": c.source_document,
            "source_section": c.source_section,
            "corpus_hash": self.catalogue.file_hash,
            "chunk_index": c.chunk_index,
            "embedding_model": self.embedding_service.get_signature(),
            "chunking_version": CHUNKING_VERSION
        } for c in all_chunks]
        
        embeddings = self.embedding_service.get_embeddings(texts)
        
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            staging_collection.add(
                ids=ids[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                documents=texts[i:i+batch_size]
            )
            
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
            
        staging_collection.modify(name=COLLECTION_NAME)
        
        log_event("indexer_build_complete", chunks_indexed=len(all_chunks))

# Expose a direct entry point for rebuilding the index
if __name__ == "__main__":
    from services.applicability.catalogue import LegalRuleCatalogue
    import os
    
    cat = LegalRuleCatalogue()
    rules_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "legal_metrology_rules.md")
    cat.load(rules_path)
    
    emb = EmbeddingService()
    idx = LegalIndexer(cat, emb)
    
    print(f"Index is stale? {idx.check_stale()}")
    print("Building index...")
    idx.build_index()
    print("Build complete.")
