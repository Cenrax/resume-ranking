from typing import List

from fastapi import UploadFile

from app.services.document_processor import document_processor
from app.services.llm_service import llm_service


class CriteriaExtractor:
    """Service for extracting ranking criteria from job descriptions."""
    
    @staticmethod
    async def extract_criteria_from_job_description(file: UploadFile) -> List[str]:
        """
        Extract key ranking criteria from a job description file.
        
        Args:
            file: UploadFile object containing the job description
            
        Returns:
            List[str]: List of extracted criteria
        """
        # Extract text from the job description file
        job_description_text = await document_processor.extract_text_from_file(file)

        print(job_description_text)
        
        # Use LLM to extract criteria from the text
        criteria = await llm_service.extract_criteria_from_job_description(job_description_text)
        
        return criteria

criteria_extractor = CriteriaExtractor()