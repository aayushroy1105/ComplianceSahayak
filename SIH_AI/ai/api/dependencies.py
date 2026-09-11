from fastapi import Request

def get_ocr_client(request: Request):
    return request.app.state.ocr_client

def get_extractor(request: Request):
    return request.app.state.extractor

def get_product_classifier(request: Request):
    return request.app.state.product_classifier

def get_context_classifier(request: Request):
    return request.app.state.context_classifier

def get_applicability_engine(request: Request):
    return request.app.state.applicability_engine

def get_retriever(request: Request):
    return request.app.state.retriever

def get_rule_engine(request: Request):
    return request.app.state.rule_engine

def get_llm_generator(request: Request):
    return request.app.state.llm_generator
