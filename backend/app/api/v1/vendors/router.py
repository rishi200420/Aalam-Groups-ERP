from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def vendors_module_status():
    return {"module": "vendors", "status": "ready"}
