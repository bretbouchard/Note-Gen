"""
Router for import/export endpoints.

This router provides endpoints for importing and exporting data from the application.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import Response
from typing import Optional

from note_gen.controllers.import_export_controller import ImportExportController
from note_gen.dependencies import get_import_export_controller

router = APIRouter(tags=["import-export"])

@router.get("/export/chord-progressions")
async def export_chord_progressions(
    format: str = Query("json", description="Export format (json or csv)"),
    controller: ImportExportController = Depends(get_import_export_controller)
):
    """
    Export all chord progressions.
    
    Args:
        format: The export format (json or csv)
        
    Returns:
        The exported data
    """
    try:
        data = await controller.export_chord_progressions(format)
        
        # Set appropriate content type and filename
        content_type = "application/json" if format.lower() == "json" else "text/csv"
        filename = f"chord_progressions.{format.lower()}"
        
        return Response(
            content=data,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/export/note-patterns")
async def export_note_patterns(
    format: str = Query("json", description="Export format (json or csv)"),
    controller: ImportExportController = Depends(get_import_export_controller)
):
    """
    Export all note patterns.
    
    Args:
        format: The export format (json or csv)
        
    Returns:
        The exported data
    """
    try:
        data = await controller.export_note_patterns(format)
        
        # Set appropriate content type and filename
        content_type = "application/json" if format.lower() == "json" else "text/csv"
        filename = f"note_patterns.{format.lower()}"
        
        return Response(
            content=data,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/export/rhythm-patterns")
async def export_rhythm_patterns(
    format: str = Query("json", description="Export format (json or csv)"),
    controller: ImportExportController = Depends(get_import_export_controller)
):
    """
    Export all rhythm patterns.
    
    Args:
        format: The export format (json or csv)
        
    Returns:
        The exported data
    """
    try:
        data = await controller.export_rhythm_patterns(format)
        
        # Set appropriate content type and filename
        content_type = "application/json" if format.lower() == "json" else "text/csv"
        filename = f"rhythm_patterns.{format.lower()}"
        
        return Response(
            content=data,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/export/sequences")
async def export_sequences(
    format: str = Query("json", description="Export format (json or csv)"),
    controller: ImportExportController = Depends(get_import_export_controller)
):
    """
    Export all sequences.
    
    Args:
        format: The export format (json or csv)
        
    Returns:
        The exported data
    """
    try:
        data = await controller.export_sequences(format)
        
        # Set appropriate content type and filename
        content_type = "application/json" if format.lower() == "json" else "text/csv"
        filename = f"sequences.{format.lower()}"
        
        return Response(
            content=data,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.post("/import/chord-progressions")
async def import_chord_progressions(
    file: UploadFile = File(...),
    controller: ImportExportController = Depends(get_import_export_controller)
):
    """
    Import chord progressions from a file.
    
    Args:
        file: The file to import from
        
    Returns:
        The number of imported items
    """
    try:
        count = await controller.import_chord_progressions(file)
        return {"imported_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")

@router.post("/import/note-patterns")
async def import_note_patterns(
    file: UploadFile = File(...),
    controller: ImportExportController = Depends(get_import_export_controller)
):
    """
    Import note patterns from a file.
    
    Args:
        file: The file to import from
        
    Returns:
        The number of imported items
    """
    try:
        count = await controller.import_note_patterns(file)
        return {"imported_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")

@router.post("/import/rhythm-patterns")
async def import_rhythm_patterns(
    file: UploadFile = File(...),
    controller: ImportExportController = Depends(get_import_export_controller)
):
    """
    Import rhythm patterns from a file.
    
    Args:
        file: The file to import from
        
    Returns:
        The number of imported items
    """
    try:
        count = await controller.import_rhythm_patterns(file)
        return {"imported_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")

@router.post("/import/sequences")
async def import_sequences(
    file: UploadFile = File(...),
    controller: ImportExportController = Depends(get_import_export_controller)
):
    """
    Import sequences from a file.
    
    Args:
        file: The file to import from
        
    Returns:
        The number of imported items
    """
    try:
        count = await controller.import_sequences(file)
        return {"imported_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")
