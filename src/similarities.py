from sentence_transformers import SentenceTransformer,util
from typing import Tuple, Optional
from cv_extraction import getCV_Data
from wuzzuf_scraper import getJobsDF
import logging
import pandas as pd




class JobInfo:
    Job_Title: str
    Company: str
    Country: str
    City: str
    Area: str
    Publish_Date: str
    Job_Link: str
    Job_Type: str
    WorkPlace: str
    Salary: str
    Experience_Needed: int
    Career_Level: str
    Education_Level: str
    Job_Categories: str
    Skills: list[str]
    Job_Requirements: str
    Similarity:float

UserCV = getCV_Data()
JobsDF = getJobsDF()

model = SentenceTransformer('all-MiniLM-L6-v2')  # Using a popular, efficient model


JobsList = []

def Findsimilarities() -> list[JobInfo]:
    for index, row in JobsDF.iterrows():
        currentJob = RowtoJobInfo(row)
        semantic_score = semantic_similarity(UserCV.raw_text,currentJob.Job_Requirements)
        skill_score = skill_similarity(UserCV.skills,currentJob.Skills)
        exp_score = experience_similarity(UserCV.total_experience_years,currentJob.Experience_Needed)
        final_score = (
            0.50 * semantic_score +
            0.35 * skill_score +
            0.15 * exp_score
        ) * 100
        currentJob.Similarity = final_score
        JobsList.append(currentJob)
    return JobsList

def semantic_similarity(text1:str,text2:str)-> float:
    if not text1 or not text2:
        raise ValueError("Both text inputs must be non-empty strings")
    
    embedding_model = model

    try:
        # Encode both texts with error handling
        embeddings = embedding_model.encode(
            [text1, text2], 
            convert_to_tensor=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        # Calculate and return cosine similarity
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        return float(similarity.item())
        
    except Exception as e:
        logging.error(f"Error calculating semantic similarity: {e}")
        raise

def skill_similarity(cv_skills:list[str],job_skills:list[str]) -> float:
        """Calculate skill overlap (Jaccard similarity focused on job requirements)."""
        if not job_skills:
            return 0.0
        cv_set = set(skill.lower().strip() for skill in cv_skills)
        job_set = set(skill.lower().strip() for skill in job_skills)
    
        return len(cv_set & job_set) / len(job_set)
     
def experience_similarity(cv_years: int, jd_years: int) -> float:
        
        if jd_years == 0:
            return 1.0
        return min(cv_years / jd_years, 1.0)

def RowtoJobInfo(row:pd.Series) -> JobInfo:
    return JobInfo(
    Job_Title=row['Job Title'],
    Company=row['Company'],
    Country=row['Country'],
    City=row['City'],
    Area=row['Area'],
    Publish_Date=row['Publish Date'],
    Job_Link=row['Job Link'],
    Job_Type=row['Job Type'],
    WorkPlace=row['Work Place'],
    Salary=row['Salary'],
    Experience_Needed=int(row['Experience Needed']) if pd.notna(row['Experience Needed']) else 0,
    Career_Level=row['Career Level'],
    Education_Level=row['Education Level'],
    Job_Categories=row['Job Categories'],
    Skills=row['Skills'] if isinstance(row['Skills'], list) else [row['Skills']],
    Job_Requirements=row['Job Requirements'],
    Similarity=0.0
)