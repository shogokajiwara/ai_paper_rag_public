import os

def delete_previous_json(cache_dir: str) -> None:
    previous_path = os.path.join(cache_dir, "previous_all_categories.json")
    if os.path.exists(previous_path):
        os.remove(previous_path)

if __name__ == "__main__":
    delete_previous_json("/cache")
