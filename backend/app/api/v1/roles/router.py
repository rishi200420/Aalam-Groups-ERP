from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def roles_module_status():
    return {"module": "roles", "status": "ready"}
