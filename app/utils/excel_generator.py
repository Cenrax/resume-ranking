import os
from datetime import datetime
from typing import Dict, List

import pandas as pd

from app.core.config import settings


class ExcelGenerator:
    """Service for generating Excel/CSV reports."""
    
    @staticmethod
    def generate_report(data: List[Dict], criteria: List[str]) -> str:
        """
        Generate an Excel/CSV report from resume scoring data.
        
        Args:
            data: List of dictionaries containing scoring data
            criteria: List of criteria used for scoring
            
        Returns:
            str: Path to the generated file
        """
        # Create a DataFrame from the data
        df = pd.DataFrame(data)
        
        # Ensure proper column order
        columns = ["Candidate Name"] + criteria + ["Total Score"]
        df = df[columns]
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_ranking_{timestamp}"
        
        # Create directory for reports if it doesn't exist
        reports_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate both Excel and CSV files
        excel_path = os.path.join(reports_dir, f"{filename}.xlsx")
        csv_path = os.path.join(reports_dir, f"{filename}.csv")
        
        # Write to Excel with formatting
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Resume Rankings")
            
            # Access the workbook and the worksheet
            workbook = writer.book
            worksheet = writer.sheets["Resume Rankings"]
            
            # Apply some basic formatting
            for col_num, column in enumerate(df.columns):
                # Set column width
                worksheet.column_dimensions[chr(65 + col_num)].width = 20
                
        # Write to CSV as well
        df.to_csv(csv_path, index=False)
        
        # Return the Excel file path
        return excel_path

excel_generator = ExcelGenerator()