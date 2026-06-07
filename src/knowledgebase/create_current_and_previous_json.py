from create_previous_temp_json import create_previous_temp_json
from save_temp_json_to_json import save_temp_json_to_json
from delete_previous_json import delete_previous_json
from create_current_temp_json import create_current_temp_json

def create_current_and_previous_json(categories: list[str], cache_dir: str) -> int:
    """
    Acquires or updates data.
    - Success -> 0
    - Failure -> 1
    """
    try:
        current_temp_path = create_current_temp_json(categories, cache_dir)
    except:
        result = 1
    else:
        try:
            previous_temp_path = create_previous_temp_json(cache_dir)
        except:
            save_temp_json_to_json(current_temp_path)
            delete_previous_json(cache_dir)
            result = 0
        else:
            save_temp_json_to_json(current_temp_path)
            save_temp_json_to_json(previous_temp_path)
            result = 0
    return result

if __name__ == "__main__":
    TARGET_CATEGORIES = [
    "cs.AI",
    "cs.LG",
    "stat.ML",
    "cs.CL",
    "cs.CV",
    "cs.NE",
    ]
    result = create_current_and_previous_json(TARGET_CATEGORIES ,"/cache")
    print(result)