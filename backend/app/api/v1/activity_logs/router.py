from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def activity_logs_module_status():
    return {"module": "activity_logs", "status": "ready"}
