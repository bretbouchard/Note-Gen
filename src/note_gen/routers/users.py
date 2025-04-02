from fastapi import APIRouter, HTTPException, Depends, Body, Path, Query
from typing import Dict, Any, List, Optional

from note_gen.controllers.user_controller import UserController
from note_gen.presenters.user_presenter import UserPresenter
from note_gen.dependencies import get_user_controller
from note_gen.models.user import User

router = APIRouter(tags=["users"])

@router.get("/")
async def get_users(
    controller: UserController = Depends(get_user_controller)
):
    """Get all users."""
    try:
        users = await controller.get_all_users()
        return {"users": UserPresenter.present_many(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user(
    controller: UserController = Depends(get_user_controller)
):
    """Get the current user."""
    try:
        user = await controller.get_current_user()
        return UserPresenter.present(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user(
    user_id: str = Path(..., description="The ID of the user to get"),
    controller: UserController = Depends(get_user_controller)
):
    """Get a user by ID."""
    try:
        user = await controller.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserPresenter.present(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_user(
    user_data: Dict[str, Any] = Body(...),
    controller: UserController = Depends(get_user_controller)
):
    """Create a new user."""
    try:
        user = await controller.create_user(user_data)
        return UserPresenter.present(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}")
async def update_user(
    user_id: str = Path(..., description="The ID of the user to update"),
    user_data: Dict[str, Any] = Body(...),
    controller: UserController = Depends(get_user_controller)
):
    """Update a user."""
    try:
        user = await controller.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserPresenter.present(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: str = Path(..., description="The ID of the user to delete"),
    controller: UserController = Depends(get_user_controller)
):
    """Delete a user."""
    try:
        success = await controller.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/by-username/{username}")
async def get_user_by_username(
    username: str = Path(..., description="The username of the user to get"),
    controller: UserController = Depends(get_user_controller)
):
    """Get a user by username."""
    try:
        user = await controller.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserPresenter.present(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))