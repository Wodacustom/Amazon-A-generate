"""语义搜索接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.search import SearchQuery, SearchResponse
from app.services.vectorstore import VectorStore

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search(query: str, limit: int = 5, db: AsyncSession = Depends(get_db)) -> dict:
    """基于 pgvector 检索产品和智能体记忆。"""
    payload = SearchQuery(query=query, limit=limit)
    documents = await VectorStore().search(db, payload.query, payload.limit)
    return {
        "items": [
            {
                "id": str(document.id),
                "source_type": document.source_type,
                "source_id": document.source_id,
                "content": document.content,
                "metadata": document.document_metadata,
                "score": None,
            }
            for document in documents
        ]
    }
