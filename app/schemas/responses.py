from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ExtractCriteriaResponse(BaseModel):
    """Response model for extract criteria endpoint."""
    criteria: List[str] = Field(..., 
                             description="List of extracted criteria from job description")

    class Config:
        schema_extra = {
            "example": {
                "criteria": [
                    "Must have certification XYZ",
                    "5+ years of experience in Python development",
                    "Strong background in Machine Learning"
                ]
            }
        }


class ResumeScoreResponse(BaseModel):
    """Response model for resume score."""
    candidate_name: str = Field(..., 
                             description="Name of the candidate")
    scores: Dict[str, int] = Field(..., 
                                description="Scores for each criterion (0-5)")
    total_score: int = Field(..., 
                          description="Total score across all criteria")

    class Config:
        schema_extra = {
            "example": {
                "candidate_name": "John Doe",
                "scores": {
                    "Must have certification XYZ": 5,
                    "5+ years of experience in Python development": 4,
                    "Strong background in Machine Learning": 4
                },
                "total_score": 13
            }
        }


class ScoreResumesResponse(BaseModel):
    """Response model for score resumes endpoint."""
    file_url: str = Field(..., 
                       description="URL to download the generated Excel/CSV report")

    class Config:
        schema_extra = {
            "example": {
                "file_url": "/api/v1/download/resume_ranking_20240303_123456.xlsx"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., 
                     description="Error message")

    class Config:
        schema_extra = {
            "example": {
                "detail": "Failed to process request due to invalid file format"
            }
        }