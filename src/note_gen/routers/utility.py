"""
Router for utility endpoints.

This router provides utility endpoints such as health checks, statistics, and other
non-core functionality.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from note_gen.controllers.utility_controller import UtilityController
from note_gen.dependencies import get_utility_controller

router = APIRouter(tags=["utilities"])

@router.get("/health")
async def health_check(
    controller: UtilityController = Depends(get_utility_controller)
):
    """
    Perform a health check.
    
    Returns:
        Dict[str, str]: The health check result
    """
    try:
        return await controller.health_check()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")

@router.get("/stats")
async def get_statistics(
    controller: UtilityController = Depends(get_utility_controller)
):
    """
    Get statistics about the database.
    
    Returns:
        Dict[str, Any]: The statistics
    """
    try:
        return await controller.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@router.get("/patterns-list")
async def list_all_patterns(
    controller: UtilityController = Depends(get_utility_controller)
):
    """
    List all patterns.
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: The patterns
    """
    try:
        return await controller.list_all_patterns()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patterns list error: {str(e)}")

@router.get("/")
async def get_api_info(
    controller: UtilityController = Depends(get_utility_controller)
):
    """
    Get API information.
    
    Returns:
        Dict[str, Any]: The API information
    """
    try:
        return await controller.get_api_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API info error: {str(e)}")
