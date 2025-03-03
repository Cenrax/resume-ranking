from typing import List, Optional

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class ExtractCriteriaRequest(BaseModel):
    """Model for extract criteria request (for docs only, actual endpoint uses form data)."""
    file: UploadFile = Field(..., description="Job description file (PDF or DOCX)")

    class Config:
        schema_extra = {
            "example": {
                "file": "uploaded_job_description.pdf"
            }
        }


class ScoreResumesRequest(BaseModel):
    """Model for score resumes request (for docs only, actual endpoint uses form data)."""
    criteria: List[str] = Field(..., 
                             description="List of criteria to score resumes against")
    files: List[UploadFile] = Field(..., 
                                  description="List of resume files to evaluate (PDF or DOCX)")

    class Config:
        schema_extra = {
            "example": {
                "criteria": [
                    "Must have certification XYZ",
                    "5+ years of experience in Python development",
                    "Strong background in Machine Learning"
                ],
                "files": [
                    "uploaded_resume_1.pdf",
                    "uploaded_resume_2.docx",
                    "uploaded_resume_3.pdf"
                ]
            }
        }


# For actual form data handling with FastAPI
def score_resumes_form(
    criteria: List[str] = Form(..., description="List of criteria to score resumes against"),
    files: List[UploadFile] = File(..., description="List of resume files to evaluate (PDF or DOCX)")
):
    return {"criteria": criteria, "files": files}