import json
from typing import Any, Dict, List, Optional, Union

from openai import OpenAI

from app.core.config import settings


class LLMService:
    """Service for interacting with Language Models (LLMs)."""
    
    def __init__(self):
        """Initialize the LLM service with appropriate API keys."""
        print(settings.OPENAI_API_KEY)
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def get_completion(self, prompt: str) -> str:
        """
        Get a simple text completion from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            str: The generated text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error getting completion: {str(e)}")
    
    async def extract_criteria_from_job_description(self, job_description: str) -> List[str]:
        """
        Extract key ranking criteria from a job description using LLM.
        
        Args:
            job_description: The text content of the job description
            
        Returns:
            List[str]: List of extracted criteria
        """
        prompt = f"""
        You are an expert HR assistant tasked with extracting key ranking criteria from job descriptions.
        
        Please analyze the following job description and extract key criteria that would be used to rank candidates.
        Focus on required skills, certifications, experience levels, and qualifications.
        
        Return the criteria as a comma-separated list within <criteria></criteria> tags.
        Each criterion should be specific and measurable.
        
        Job Description:
        {job_description}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract ranking criteria from job descriptions. Return the criteria as a comma-separated list within <criteria></criteria> tags."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more focused and consistent output
                max_tokens=1000
            )
            
            # Extract content from the response
            content = response.choices[0].message.content
            
            # Extract criteria from the XML-like tags
            start_tag = "<criteria>"
            end_tag = "</criteria>"
            start_index = content.find(start_tag) + len(start_tag)
            end_index = content.find(end_tag)
            
            if start_index != -1 and end_index != -1:
                criteria_string = content[start_index:end_index].strip()
                return [criterion.strip() for criterion in criteria_string.split(",")]
            else:
                raise ValueError("Criteria not found in the expected format")
            
        except Exception as e:
            raise Exception(f"Error extracting criteria from job description: {str(e)}")
    async def score_resume_against_criteria(self, resume_text: str, criteria: List[str]) -> Dict[str, int]:
        """
        Score a resume against the provided criteria using LLM.
        
        Args:
            resume_text: The text content of the resume
            criteria: List of criteria to score against
            
        Returns:
            Dict[str, int]: Dictionary mapping each criterion to a score (0-5)
        """
        # Format criteria for the prompt
        criteria_text = "\n".join([f"- {criterion}" for criterion in criteria])
        
        prompt = f"""
        You are an expert HR assistant tasked with scoring resumes against specific criteria.
        
        Please analyze the following resume and score it against each criterion on a scale of 0-5,
        where 0 means "not mentioned or not relevant" and 5 means "exceeds expectations".
        
        Criteria:
        {criteria_text}
        
        Resume:
        {resume_text}
        
        For each criterion, provide a score (0-5) and a brief justification.
        Return the results in JSON format with the criterion as the key and the score as the value.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You score resumes against criteria. Return only a JSON object mapping each criterion to a score from 0-5."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more consistent scoring
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Ensure we have scores for all criteria
            scores = {}
            for criterion in criteria:
                # Find the matching criterion in the response
                # This handles slight variations in formatting
                matching_key = next((k for k in data.keys() if criterion.lower() in k.lower()), None)
                
                if matching_key:
                    # Get the score, ensuring it's an integer from 0-5
                    raw_score = data[matching_key]
                    if isinstance(raw_score, dict) and "score" in raw_score:
                        # Handle if the LLM returns objects with score property
                        score = min(5, max(0, int(raw_score["score"])))
                    else:
                        # Handle if the LLM returns direct score values
                        score = min(5, max(0, int(raw_score)))
                    scores[criterion] = score
                else:
                    # Default to 0 if no match found
                    scores[criterion] = 0
                    
            return scores
            
        except Exception as e:
            raise Exception(f"Error scoring resume against criteria: {str(e)}")

llm_service = LLMService()