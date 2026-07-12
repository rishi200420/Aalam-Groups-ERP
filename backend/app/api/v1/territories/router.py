from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def territories_module_status():
    return {"module": "territories", "status": "ready"}
