"""Documentation routes for serving markdown files."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/docs", tags=["documentation"])

# Map doc names to file paths
DOC_FILES = {
    "readme": "README.md",
    "prd": "prd.md",
    "architecture": "ARCHITECTURE.md",
    "diagrams": "diagrams.md",
    "tech-decisions": "TECH_DECISIONS.md",
}

# Project root directory (where the markdown files are)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@router.get("/{doc_name}")
async def get_documentation(doc_name: str) -> dict:
    """Get a documentation file by name.

    Args:
        doc_name: One of 'readme', 'prd', 'architecture', 'diagrams', 'tech-decisions'

    Returns:
        The markdown content of the requested document
    """
    if doc_name not in DOC_FILES:
        raise HTTPException(
            status_code=404,
            detail=f"Document '{doc_name}' not found. Available: {list(DOC_FILES.keys())}",
        )

    file_path = PROJECT_ROOT / DOC_FILES[doc_name]

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Document file '{DOC_FILES[doc_name]}' not found on disk",
        )

    content = file_path.read_text(encoding="utf-8")

    return {
        "name": doc_name,
        "filename": DOC_FILES[doc_name],
        "content": content,
    }


@router.get("/")
async def list_documentation() -> dict:
    """List all available documentation files."""
    available = []
    for name, filename in DOC_FILES.items():
        file_path = PROJECT_ROOT / filename
        available.append({
            "name": name,
            "filename": filename,
            "exists": file_path.exists(),
        })

    return {"documents": available}
