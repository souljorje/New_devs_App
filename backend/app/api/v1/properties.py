from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from app.core.auth import authenticate_request
from app.core.database_pool import DatabasePool

router = APIRouter()


@router.get("/properties")
async def list_properties(
    current_user=Depends(authenticate_request),
):
    try:
        db_pool = DatabasePool()
        await db_pool.initialize()

        session = await db_pool.get_session()
        async with session:
            items_result = await session.execute(
                text(
                    """
                    SELECT id, tenant_id, name, timezone, created_at
                    FROM properties
                    WHERE tenant_id = :tenant_id
                    ORDER BY name, id
                    """
                ),
                {"tenant_id": current_user.tenant_id},
            )
            items = [dict(row._mapping) for row in items_result.fetchall()]
    except Exception as e:
        print(f"Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch properties")

    return {"items": items, "total": len(items)}
