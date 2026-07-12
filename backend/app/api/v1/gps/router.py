from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def gps_module_status():
    return {"module": "gps", "status": "ready"}
