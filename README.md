# AI Job Recommender

A job recommendation system that scrapes job listings from Wuzzuf, parses CVs, and finds the best matches using local search algorithms.

## Features

- **CV Extraction**: Extract text, skills, and experience from PDF/DOCX files.
- **Job Scraping**: Automated scraping of job listings and details from Wuzzuf using Selenium.
- **Similarity Scoring**: Hybrid matching using semantic similarity (Sentence Transformers), skill overlap, and experience years.
- **Local Search Algorithms**:
  - Hill Climbing
  - Simulated Annealing
  - Local Beam Search
  - Tabu Search

## Project Structure

- `cv_extraction.py`: CV parsing logic.
- `wuzzuf_scraper.py`: Web scraper for job data.
- `similarities.py`: Multi-factor similarity scoring.
- `search_space.py`: Search space representation.
- `search_algorithms.py`: Optimization algorithms for job discovery.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Google Chrome is installed (required for Wuzzuf scraping).
