import os
import json

def create_previous_temp_json(cache_dir: str) -> str:
    """
    Reads the current "all_categories.json" file.
    """
    current_path = os.path.join(cache_dir, "all_categories.json")

    if not os.path.exists(current_path):
        raise FileNotFoundError(f'"all_categories.json" file does not exist: {current_path}')

    with open(current_path, "r", encoding="utf-8") as f:
        cache = json.load(f)

    previous_temp_path = os.path.join(cache_dir, "previous_all_categories.json.tmp")

    # writing to a temp file 
    with open(previous_temp_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    return previous_temp_path

if __name__ == "__main__":
    previous_temp_path = create_previous_temp_json("/cache")
    print(previous_temp_path)


