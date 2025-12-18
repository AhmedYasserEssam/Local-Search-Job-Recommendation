import random
import math
from typing import List, Dict, Set

from job import Job
from search_space import JobSearchSpace


def hill_climbing(space: JobSearchSpace, max_no_improve: int = 10) -> List[Job]:
    current = space.get_random_job()
    current_score = space.get_score(current)
    
    visited: Dict[int, float] = {id(current): current_score}
    no_improve_count = 0
    
    while no_improve_count < max_no_improve:
        neighbors = space.get_neighbors(current, k=5)
        
        if not neighbors:
            break
        
        best_neighbor = None
        best_neighbor_score = current_score
        
        for neighbor in neighbors:
            score = space.get_score(neighbor)
            visited[id(neighbor)] = score
            
            if score > best_neighbor_score:
                best_neighbor = neighbor
                best_neighbor_score = score
        
        if best_neighbor is not None and best_neighbor_score > current_score:
            current = best_neighbor
            current_score = best_neighbor_score
            no_improve_count = 0
        else:
            no_improve_count += 1
    
    visited_jobs = [(job, visited[id(job)]) for job in space.jobs if id(job) in visited]
    visited_jobs.sort(key=lambda x: x[1], reverse=True)
    return [job for job, _ in visited_jobs[:3]]


def simulated_annealing(
    space: JobSearchSpace,
    initial_temp: float = 100.0,
    cooling_rate: float = 0.95,
    min_temp: float = 0.01
) -> List[Job]:
    current = space.get_random_job()
    current_score = space.get_score(current)
    
    best = current
    best_score = current_score
    
    visited: Dict[int, float] = {id(current): current_score}
    temp = initial_temp
    
    while temp > min_temp:
        neighbors = space.get_neighbors(current, k=5)
        
        if not neighbors:
            break
        
        neighbor = random.choice(neighbors)
        neighbor_score = space.get_score(neighbor)
        visited[id(neighbor)] = neighbor_score
        
        delta = neighbor_score - current_score
        
        if delta > 0 or random.random() < math.exp(delta / temp):
            current = neighbor
            current_score = neighbor_score
            
            if current_score > best_score:
                best = current
                best_score = current_score
        
        temp *= cooling_rate
    
    visited_jobs = [(job, visited[id(job)]) for job in space.jobs if id(job) in visited]
    visited_jobs.sort(key=lambda x: x[1], reverse=True)
    return [job for job, _ in visited_jobs[:3]]


def local_beam_search(
    space: JobSearchSpace,
    k: int = 5,
    max_iter: int = 50
) -> List[Job]:
    beam: List[Job] = random.sample(space.jobs, min(k, space.size()))
    
    for _ in range(max_iter):
        all_candidates: List[Job] = []
        seen_ids: Set[int] = set()
        
        for job in beam:
            neighbors = space.get_neighbors(job, k=3)
            for neighbor in neighbors:
                if id(neighbor) not in seen_ids:
                    all_candidates.append(neighbor)
                    seen_ids.add(id(neighbor))
        
        for job in beam:
            if id(job) not in seen_ids:
                all_candidates.append(job)
                seen_ids.add(id(job))
        
        if not all_candidates:
            break
        
        all_candidates.sort(key=lambda j: space.get_score(j), reverse=True)
        new_beam = all_candidates[:k]
        
        scores = [space.get_score(j) for j in new_beam]
        if len(set(round(s, 1) for s in scores)) == 1:
            beam = new_beam
            break
        
        beam = new_beam
    
    beam.sort(key=lambda j: space.get_score(j), reverse=True)
    return beam[:3]


def tabu_search(
    space: JobSearchSpace,
    max_iter: int = 50,
    tabu_tenure: int = 7
) -> List[Job]:
    current = space.get_random_job()
    current_score = space.get_score(current)
    
    best = current
    best_score = current_score
    
    visited: Dict[int, float] = {id(current): current_score}
    tabu_list: List[int] = [id(current)]
    
    for _ in range(max_iter):
        neighbors = space.get_neighbors(current, k=5)
        
        if not neighbors:
            break
        
        best_neighbor = None
        best_neighbor_score = float('-inf')
        
        for neighbor in neighbors:
            if id(neighbor) in tabu_list:
                continue
            
            score = space.get_score(neighbor)
            visited[id(neighbor)] = score
            
            if score > best_neighbor_score:
                best_neighbor = neighbor
                best_neighbor_score = score
        
        if best_neighbor is None:
            non_tabu = [j for j in neighbors if id(j) not in tabu_list]
            if non_tabu:
                best_neighbor = random.choice(non_tabu)
                best_neighbor_score = space.get_score(best_neighbor)
            else:
                best_neighbor = random.choice(neighbors)
                best_neighbor_score = space.get_score(best_neighbor)
        
        current = best_neighbor
        current_score = best_neighbor_score
        
        tabu_list.append(id(current))
        if len(tabu_list) > tabu_tenure:
            tabu_list.pop(0)
        
        if current_score > best_score:
            best = current
            best_score = current_score
    
    visited_jobs = [(job, visited[id(job)]) for job in space.jobs if id(job) in visited]
    visited_jobs.sort(key=lambda x: x[1], reverse=True)
    return [job for job, _ in visited_jobs[:3]]
