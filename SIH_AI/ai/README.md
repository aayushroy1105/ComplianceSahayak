# AI Service

This is the AI service for the Legal Metrology Packaged Commodity Compliance System prototype.

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (e.g. in `.env`):
   ```
   MOCK_AI=true
   DEBUG_PIPELINE=false
   LEGAL_RULES_PATH=../legal_metrology_rules.md
   ```

## Running the Service

```bash
uvicorn main:app --reload
```
The service will be available at `http://127.0.0.1:8000`.

## Endpoints

- `GET /health`: Health check endpoint.
- `POST /ai/analyze`: Package analysis endpoint.

## MOCK_AI Behavior

When `MOCK_AI=true` is set, the `/ai/analyze` endpoint returns a deterministic, static JSON response demonstrating the structured AI contract without executing OCR, RAG, or the Rule Engine. This is to verify system boundaries and integration points. If `MOCK_AI` is false, it will currently return an `AI_PIPELINE_ERROR` (Not Implemented).

## Testing

Run tests with `pytest`:
```bash
pytest tests/
```
