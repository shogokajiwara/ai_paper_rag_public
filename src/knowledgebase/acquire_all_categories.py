import time
from acquire_latest_arxiv_data import acquire_latest_arxiv_data

def acquire_all_categories(categories: list[str], cache_dir: str) -> list[str]:
    """Fetches arXiv data for a given list of categories and returns a list of paths."""
    category_paths = []
    for category in categories:
        category_path = acquire_latest_arxiv_data(category, cache_dir)
        category_paths.append(category_path)
        time.sleep(5)
    return category_paths

if __name__ == "__main__":
    TARGET_CATEGORIES = [
    "cs.AI",
    "cs.LG",
    "stat.ML",
    "cs.CL",
    "cs.CV",
    "cs.NE",
    ]
    category_paths = acquire_all_categories(TARGET_CATEGORIES,"/cache")
    print(category_paths)


