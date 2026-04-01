# Deployment Guide

## Local Development

```bash
cd ~/Projects/Sozo-Protocol-Generator

# Install dependencies
pip install streamlit python-docx pydantic pydantic-settings typer pyyaml matplotlib pillow svgwrite httpx

# Run the app
PYTHONPATH=src streamlit run app.py

# Run tests
PYTHONPATH=src python -m pytest tests/ -v -m "not slow"

# Generate all documents (CLI)
PYTHONPATH=src python generate_all.py --with-qa --with-manifests
```

## Environment Requirements

- Python 3.8+ (tested on 3.8.8)
- All dependencies in `requirements.txt`
- Optional: `biopython>=1.81` for live PubMed queries (system works without it)
- Optional: Anthropic API key for AI-powered chat intent parsing

## Docker

```bash
docker build -t sozo-generator .
docker run -p 8080:8080 sozo-generator
```

## Fly.io

```bash
fly deploy
```

Configuration in `fly.toml`:
- Region: `lhr` (London)
- Port: 8080
- Auto-scaling: min 0, max 1

## Pages

| Page | Purpose |
|---|---|
| **Chat** | Natural language document generation, merging, QA |
| **Generate from Template** | Upload DOCX template, generate for all conditions |
| **Generate Documents** | Standard document generation per condition |
| **Review Queue** | Approve/reject/flag, section review, reports, exports |
| **Conditions Overview** | View all 15 conditions with clinical details |
| **QA Report** | Completeness and conformity checks |
| **Evidence Ingest** | PubMed evidence fetching with caching |

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'Bio'` | Install `biopython` or ignore — system works without it |
| `InvalidVersion: '4.0.0-unsupported'` | Remove broken pyodbc: `pip uninstall pyodbc` |
| Streamlit won't start | Check `PYTHONPATH=src` is set |
| No documents generated | Check `outputs/documents/` directory exists |
| Review queue empty | Reviews are stored in `reviews/` — create via Chat or API |

## Authentication

Set password in `.streamlit/secrets.toml`:
```toml
[auth]
password = "your-password"
```

Or skip authentication in local dev (no secrets = no gate).

## AI Chat (Optional)

Add Anthropic API key in sidebar "AI Settings" or in `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Without an API key, the chat uses rule-based intent parsing (works for all standard commands).
