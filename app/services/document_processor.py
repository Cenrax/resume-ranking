import os
from typing import Dict, List, Tuple, Union

import docx
import fitz  # PyMuPDF
from fastapi import UploadFile

from app.core.config import settings


class DocumentProcessor:
    """Service for processing PDF and DOCX documents."""
    
    @staticmethod
    async def extract_text_from_file(file: UploadFile) -> str:
        """
        Extract text content from uploaded PDF or DOCX file.
        
        Args:
            file: UploadFile object containing the document
            
        Returns:
            str: Extracted text content
            
        Raises:
            ValueError: If file format is not supported
        """
        # Save the uploaded file temporarily
        temp_file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
            
        try:
            # Extract text based on file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext == ".pdf":
                text = DocumentProcessor._extract_text_from_pdf(temp_file_path)
            elif file_ext in [".docx", ".doc"]:
                text = DocumentProcessor._extract_text_from_docx(temp_file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
            return text
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    @staticmethod
    def _extract_text_from_pdf(file_path: str) -> str:
        """Extract text from a PDF file."""
        text = ""
        try:
            # Open the PDF file
            with fitz.open(file_path) as pdf:
                # Extract text from each page
                for page in pdf:
                    text += page.get_text()
            return text
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def _extract_text_from_docx(file_path: str) -> str:
        """Extract text from a DOCX file."""
        try:
            # Open the DOCX file
            doc = docx.Document(file_path)
            # Extract text from paragraphs
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text)
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {str(e)}")
            
    @staticmethod
    async def get_candidate_name_from_resume(resume_text: str) -> str:
        """
        Extract candidate name from resume text using GPT-4.
        
        Args:
            resume_text: The extracted text from a resume
            
        Returns:
            str: The candidate's name or a placeholder if not found
        """
        from app.services.llm_service import llm_service

        prompt = f"""
        Extract the candidate's full name from the following resume text.
        Return only the name, without any additional text or explanation.
        If you can't find a name, return "Unnamed Candidate".

        Resume text:
        {resume_text[:500]}  # Send first 500 characters to keep prompt short
        """

        try:
            name = await llm_service.get_completion(prompt)
            return name.strip() or "Unnamed Candidate"
        except Exception as e:
            print(f"Error extracting name: {str(e)}")
            return "Unnamed Candidate"

document_processor = DocumentProcessor()