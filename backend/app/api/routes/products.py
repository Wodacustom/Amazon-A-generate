"""产品接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead
from app.services.vectorstore import VectorStore

router = APIRouter()


@router.post("", response_model=ProductRead, status_code=201)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)) -> Product:
    """创建产品，并同步写入一条 pgvector 检索文档。"""
    product = Product(**payload.model_dump())
    db.add(product)
    await db.flush()
    await VectorStore().add_document(
        db,
        source_type="product",
        source_id=str(product.id),
        content=_product_text(payload),
        metadata={"platform": payload.platform, "country": payload.country, "language": payload.language},
    )
    await db.commit()
    await db.refresh(product)
    return product


def _product_text(product: ProductCreate) -> str:
    """把产品字段拼成向量化文本。"""
    return " ".join(
        [
            product.name,
            product.description or "",
            " ".join(product.selling_points),
            str(product.specs),
        ]
    )
