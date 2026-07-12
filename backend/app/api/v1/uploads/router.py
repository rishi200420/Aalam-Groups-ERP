from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def uploads_module_status():
    return {"module": "uploads", "status": "ready"}
