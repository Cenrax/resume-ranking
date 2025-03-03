import os
from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile

from app.core.config import settings


class FileHandler:
    """Utility for handling file uploads and validation."""
    
    @staticmethod
    def validate_file_type(file: UploadFile) -> None:
        """
        Validate that the uploaded file has an allowed content type.
        
        Args:
            file: The uploaded file to validate
            
        Raises:
            HTTPException: If the file type is not supported
        """
        if file.content_type not in settings.SUPPORTED_FILE_TYPES:
            allowed_extensions = ", ".join([".pdf", ".docx"])
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {allowed_extensions}"
            )
    
    @staticmethod
    def validate_file_size(file: UploadFile) -> None:
        """
        Validate that the uploaded file does not exceed the maximum file size.
        
        Args:
            file: The uploaded file to validate
            
        Raises:
            HTTPException: If the file is too large
        """
        # This is an approximation, as we can't easily get the file size without reading it
        # In a production environment, you might want to use a different approach
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # Reset file pointer
        
        if file_size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size allowed: {max_size_mb}MB"
            )
    
    @staticmethod
    def validate_files(files: List[UploadFile]) -> None:
        """
        Validate a list of uploaded files.
        
        Args:
            files: List of uploaded files to validate
            
        Raises:
            HTTPException: If any validation fails
        """
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
            
        for file in files:
            FileHandler.validate_file_type(file)
            FileHandler.validate_file_size(file)
    
    @staticmethod
    def get_file_path(filename: str) -> Path:
        """
        Get the path for a file in the upload directory.
        
        Args:
            filename: Name of the file
            
        Returns:
            Path: Path object for the file
        """
        return Path(settings.UPLOAD_DIR) / filename

file_handler = FileHandler()