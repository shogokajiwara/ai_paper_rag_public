import time
import logging
from fetch_arxiv_papers import fetch_arxiv_papers
from save_temp_json_to_json import save_temp_json_to_json

logger = logging.getLogger(__name__)

def acquire_latest_arxiv_data(category: str, cache_dir: str) -> str:
    retry_delays = [5, 10, 20]  # seconds

    for i in range(4):
        try:
            current_temp_path = fetch_arxiv_papers(category,cache_dir)
            current_path = save_temp_json_to_json(current_temp_path)
            return str(current_path)
        
        except Exception as e:
            logger.critical(f"category={category}, retry={i}, error={e}")
            if i < 3:
                time.sleep(retry_delays[i])
            else:
                raise e
    
    raise RuntimeError("Unexpected error")

if __name__ == "__main__":
    current_path = acquire_latest_arxiv_data("cs.AI","/cache")
    print(current_path)
