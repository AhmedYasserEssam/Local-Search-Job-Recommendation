from sentence_transformers import SentenceTransformer, util
from typing import Any


model = SentenceTransformer('all-MiniLM-L6-v2')


def calculate_similarity(cv_data: Any, job: Any) -> float:
    semantic_score = semantic_similarity(cv_data.raw_text, job.Job_Requirements)
    skill_score = skill_similarity(cv_data.skills, job.Skills)
    exp_score = experience_similarity(cv_data.total_experience_years, job.Experience_Needed)
    
    final_score = (
        0.50 * semantic_score +
        0.35 * skill_score +
        0.15 * exp_score
    ) * 100
    
    return final_score


def semantic_similarity(text1: str, text2: str) -> float:
    embeddings = model.encode(
        [text1, text2], 
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    return float(similarity.item())

def skill_similarity(cv_skills: List[str], job_skills: List[str]) -> float:
    if not job_skills:
        return 0.0
    cv_set = set(skill.lower().strip() for skill in cv_skills)
    job_set = set(skill.lower().strip() for skill in job_skills)

    return len(cv_set & job_set) / len(job_set)
     
def experience_similarity(cv_years: float, jd_years: int) -> float:
    if jd_years == 0:
        return 1.0
    return min(cv_years / jd_years, 1.0)
