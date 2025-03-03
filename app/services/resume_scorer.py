import os
from typing import Dict, List, Tuple

import pandas as pd
from fastapi import UploadFile

from app.services.document_processor import document_processor
from app.services.llm_service import llm_service
from app.utils.excel_generator import excel_generator


class ResumeScorer:
    """Service for scoring resumes against criteria."""
    
    @staticmethod
    async def score_resumes(criteria: List[str], files: List[UploadFile]) -> str:
        """
        Score multiple resumes against provided criteria.
        
        Args:
            criteria: List of criteria to score against
            files: List of resume files to evaluate
            
        Returns:
            str: Path to the generated Excel/CSV file
        """
        # Process each resume and collect scores
        results = []
        
        for resume_file in files:
            # Extract text from resume
            resume_text = await document_processor.extract_text_from_file(resume_file)
            
            # Try to extract candidate name
            candidate_name = await document_processor.get_candidate_name_from_resume(resume_text)
            
            # Score the resume against criteria
            scores = await llm_service.score_resume_against_criteria(resume_text, criteria)
            
            # Calculate total score
            total_score = sum(scores.values())
            
            # Add to results
            result = {
                "Candidate Name": candidate_name,
                **scores,
                "Total Score": total_score
            }
            
            results.append(result)
        
        # Sort results by total score (descending)
        sorted_results = sorted(results, key=lambda x: x["Total Score"], reverse=True)
        
        # Generate Excel/CSV report
        output_path = excel_generator.generate_report(sorted_results, criteria)
        
        return output_path

resume_scorer = ResumeScorer()