from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_database
from backend.models import SettingsBase, SettingsInDB, UserInDB
from backend.routers.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/", response_model=SettingsInDB)
async def get_settings(
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    settings = await db["settings"].find_one({"user_id": current_user.id})
    if not settings:
        # Should have been created at registration, but just in case
        new_settings = SettingsInDB(user_id=current_user.id)
        await db["settings"].insert_one(new_settings.model_dump(by_alias=True, exclude={"id"}))
        return new_settings
    return SettingsInDB(**settings)

@router.put("/update", response_model=SettingsInDB)
async def update_settings(
    settings_update: SettingsBase,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    update_data = settings_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db["settings"].find_one_and_update(
        {"user_id": current_user.id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Settings not found")
        
    return SettingsInDB(**result)

@router.post("/preset")
async def apply_preset(
    preset_name: str,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    presets = {
        "safe": {"dip_threshold": 5.0, "rise_threshold": 5.0, "cooldown_minutes": 30},
        "standard": {"dip_threshold": 2.5, "rise_threshold": 2.5, "cooldown_minutes": 15},
        "scalping": {"dip_threshold": 1.0, "rise_threshold": 1.0, "cooldown_minutes": 5},
        "extreme": {"dip_threshold": 0.5, "rise_threshold": 0.5, "cooldown_minutes": 1}
    }
    
    if preset_name not in presets:
        raise HTTPException(status_code=400, detail="Invalid preset name")
        
    update_data = presets[preset_name]
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db["settings"].find_one_and_update(
        {"user_id": current_user.id},
        {"$set": update_data},
        return_document=True
    )
    return SettingsInDB(**result)

@router.post("/test-notification")
async def test_notification(
    channel: str,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    # In a real app, this would trigger the notification service
    # For now, we just return success
    return {"status": "success", "message": f"Test notification sent to {channel}"}

@router.post("/reset")
async def reset_settings(
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_database)
):
    default_settings = SettingsBase() # Uses defaults from model
    update_data = default_settings.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db["settings"].find_one_and_update(
        {"user_id": current_user.id},
        {"$set": update_data},
        return_document=True
    )
    return SettingsInDB(**result)
