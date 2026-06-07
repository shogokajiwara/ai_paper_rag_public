import os
from acquire_all_categories import acquire_all_categories
from merge_json_for_all_caterogies import merge_json_for_all_categories

def create_current_temp_json(categories: list[str],cache_dir: str) -> str:

    os.makedirs(cache_dir, exist_ok=True)
    category_paths = acquire_all_categories(categories, cache_dir)
    current_temp_path = merge_json_for_all_categories(category_paths)
    
    return current_temp_path

if __name__ == "__main__":
    TARGET_CATEGORIES = [
    "cs.AI",
    "cs.LG",
    "stat.ML",
    "cs.CL",
    "cs.CV",
    "cs.NE",
    ]
    current_temp_path = create_current_temp_json(TARGET_CATEGORIES,"/cache")
    print(current_temp_path)