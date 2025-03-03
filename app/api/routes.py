import json
import os
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask
from starlette.status import HTTP_201_CREATED

from app.core.config import settings
from app.schemas.requests import score_resumes_form
from app.schemas.responses import (ErrorResponse, ExtractCriteriaResponse,
                                  ScoreResumesResponse)
from app.services.criteria_extractor import criteria_extractor
from app.services.resume_scorer import resume_scorer
from app.utils.file_handler import file_handler

router = APIRouter()


@router.post(
    "/extract-criteria",
    response_model=ExtractCriteriaResponse,
    status_code=HTTP_201_CREATED,
    summary="Extract ranking criteria from job description",
    description="Extract key ranking criteria from a job description file (PDF or DOCX).",
    responses={
        201: {"description": "Criteria successfully extracted"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    tags=["Ranking Criteria"]
)
async def extract_criteria(
    file: UploadFile = File(..., description="Job description file (PDF or DOCX)"),
):
    """
    Extract key ranking criteria from a job description file.
    
    - **file**: Job description file (PDF or DOCX)
    
    Returns a list of extracted criteria.
    """
    try:
        # Validate file
        file_handler.validate_file_type(file)
        file_handler.validate_file_size(file)
        
        # Extract criteria from job description
        criteria = await criteria_extractor.extract_criteria_from_job_description(file)
        
        return ExtractCriteriaResponse(criteria=criteria)
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except Exception as e:
        # Log the error in a production environment
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract criteria: {str(e)}"
        )


@router.post(
    "/score-resumes",
    response_model=ScoreResumesResponse,
    status_code=HTTP_201_CREATED,
    summary="Score resumes against criteria",
    description="Score multiple resumes against provided criteria and generate an Excel/CSV report.",
    responses={
        201: {"description": "Resumes successfully scored"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    tags=["Resume Scoring"]
)
async def score_resumes(
    criteria: List[str] = Form(..., description="List of criteria to score resumes against"),
    files: List[UploadFile] = File(..., description="Resume files to evaluate (PDF or DOCX)"),
):
    """
    Score multiple resumes against provided criteria.
    
    - **criteria**: List of criteria to score resumes against
    - **files**: List of resume files to evaluate (PDF or DOCX)
    
    Returns a URL to download the generated Excel/CSV report.
    """
    try:
        # Validate files
        file_handler.validate_files(files)
        
        # Score resumes against criteria
        output_path = await resume_scorer.score_resumes(criteria, files)
        
        # Get filename for URL
        filename = os.path.basename(output_path)
        file_url = f"{settings.API_PREFIX}/download/{filename}"
        
        return ScoreResumesResponse(file_url=file_url)
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except Exception as e:
        # Log the error in a production environment
        raise HTTPException(
            status_code=500,
            detail=f"Failed to score resumes: {str(e)}"
        )


@router.get(
    "/download/{filename}",
    summary="Download generated report",
    description="Download a generated Excel/CSV report.",
    response_class=FileResponse,
    responses={
        200: {"description": "File downloaded successfully"},
        404: {"model": ErrorResponse, "description": "File not found"}
    },
    tags=["Downloads"]
)
async def download_file(filename: str):
    """
    Download a generated Excel/CSV report.
    
    - **filename**: Name of the file to download
    
    Returns the file for download.
    """
    try:
        # Build file path
        file_path = os.path.join(settings.UPLOAD_DIR, "reports", filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
            
        # Return file for download
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" 
                      if filename.endswith(".xlsx") else "text/csv"
        )
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except Exception as e:
        # Log the error in a production environment
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )