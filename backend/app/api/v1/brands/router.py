from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def brands_module_status():
    return {"module": "brands", "status": "ready"}
