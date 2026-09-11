from typing import List, Optional
from schemas.rag import RetrievalResult, RetrievedChunk, RetrievalMode
from services.rag.embeddings import EmbeddingService
from services.rag.indexer import LegalIndexer, COLLECTION_NAME
from schemas.applicability import ApplicabilityResult
from core.logging import log_event

class Retriever:
    def __init__(self, indexer: LegalIndexer, embedding_service: EmbeddingService):
        self.indexer = indexer
        self.embedding_service = embedding_service
        self.collection = None
        
    def _get_collection(self):
        if self.collection is None:
            try:
                self.collection = self.indexer.client.get_collection(COLLECTION_NAME)
            except Exception:
                self.collection = None
        return self.collection

    def retrieve(self, query: str, applicability_result: ApplicabilityResult, k: int = 5) -> RetrievalResult:
        collection = self._get_collection()
        
        if collection is None or self.indexer.check_stale():
            log_event("retriever_stale_or_missing_index")
            return RetrievalResult(
                query=query,
                retrieval_mode=RetrievalMode.REVIEW_ONLY,
                chunks=[],
                corpus_hash=self.indexer.catalogue.file_hash if self.indexer.catalogue else "unknown",
                error="VECTOR_STORE_ERROR"
            )
            
        retrieval_mode = RetrievalMode.AUTOMATIC
        filter_dict = None
        
        if applicability_result.status == "INSUFFICIENT_CONTEXT":
            retrieval_mode = RetrievalMode.REVIEW_ONLY
        else:
            allowed_ids = applicability_result.applicable_rule_ids + applicability_result.candidate_rule_ids
            if not allowed_ids:
                return RetrievalResult(
                    query=query,
                    retrieval_mode=retrieval_mode,
                    chunks=[],
                    corpus_hash=self.indexer.catalogue.file_hash
                )
            if len(allowed_ids) == 1:
                filter_dict = {"rule_id": allowed_ids[0]}
            else:
                filter_dict = {"rule_id": {"$in": allowed_ids}}
                
        try:
            query_embedding = self.embedding_service.get_embeddings([query])[0]
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filter_dict
            )
            
            chunks = []
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    meta = results["metadatas"][0][i]
                    score = results["distances"][0][i] 
                    chunks.append(RetrievedChunk(
                        rule_id=meta["rule_id"],
                        text=results["documents"][0][i],
                        score=score,
                        source_document=meta["source_document"],
                        source_section=meta["source_section"],
                        corpus_hash=meta["corpus_hash"],
                        chunk_index=meta["chunk_index"]
                    ))
                    
            return RetrievalResult(
                query=query,
                retrieval_mode=retrieval_mode,
                chunks=chunks,
                corpus_hash=self.indexer.catalogue.file_hash
            )
        except Exception as e:
            log_event("retriever_exception", error=str(e))
            return RetrievalResult(
                query=query,
                retrieval_mode=RetrievalMode.REVIEW_ONLY,
                chunks=[],
                corpus_hash=self.indexer.catalogue.file_hash if self.indexer.catalogue else "unknown",
                error="VECTOR_STORE_ERROR"
            )
