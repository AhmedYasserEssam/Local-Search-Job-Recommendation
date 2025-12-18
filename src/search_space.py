import random
from typing import List, Dict

from job import Job
from cv_extraction import CVData
from similarities import calculate_similarity


class JobSearchSpace:
    def __init__(self, jobs: List[Job], cv_data: CVData):
        self.jobs = jobs
        self.cv_data = cv_data
        self._scores: Dict[int, float] = {}
        self._precompute_scores()
    
    def _precompute_scores(self) -> None:
        for job in self.jobs:
            self._scores[id(job)] = calculate_similarity(self.cv_data, job)
    
    def get_score(self, job: Job) -> float:
        return self._scores.get(id(job), 0.0)
    
    def get_random_job(self) -> Job:
        return random.choice(self.jobs)
    
    def get_neighbors(self, current: Job, k: int = 5) -> List[Job]:
        current_skills = set(s.lower() for s in current.skills)
        current_categories = set(c.lower() for c in current.categories)
        
        neighbor_scores = []
        
        for job in self.jobs:
            if id(job) == id(current):
                continue
            
            job_skills = set(s.lower() for s in job.skills)
            job_categories = set(c.lower() for c in job.categories)
            
            skill_overlap = len(current_skills & job_skills)
            category_overlap = len(current_categories & job_categories)
            
            neighbor_score = skill_overlap * 2 + category_overlap
            neighbor_scores.append((job, neighbor_score))
        
        neighbor_scores.sort(key=lambda x: x[1], reverse=True)
        return [job for job, _ in neighbor_scores[:k]]
    
    def get_top_jobs(self, k: int = 3) -> List[Job]:
        sorted_jobs = sorted(self.jobs, key=lambda j: self.get_score(j), reverse=True)
        return sorted_jobs[:k]
    
    def size(self) -> int:
        return len(self.jobs)
