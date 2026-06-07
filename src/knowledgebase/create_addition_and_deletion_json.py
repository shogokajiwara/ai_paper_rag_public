import os
import json
import shutil
from save_temp_json_to_json import save_temp_json_to_json

def create_addition_and_deletion_json(cache_dir: str) -> None:
    current_path = os.path.join(cache_dir, "all_categories.json")
    previous_path = os.path.join(cache_dir, "previous_all_categories.json")

    addition_path = os.path.join(cache_dir, "addition.json")
    deletion_path = os.path.join(cache_dir, "deletion.json")

    addition_temp = addition_path + ".tmp"
    deletion_temp = deletion_path + ".tmp"

    # If previous does not exist
    if not os.path.exists(previous_path):
        # Copy current to addition.json.tmp
        shutil.copyfile(current_path, addition_temp)
        save_temp_json_to_json(addition_temp)

        # Create deletion.json.tmp with an empty list
        with open(deletion_temp, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        save_temp_json_to_json(deletion_temp)

        return

    # If previous exists
    with open(current_path, "r", encoding="utf-8") as f:
        current_data = json.load(f)

    with open(previous_path, "r", encoding="utf-8") as f:
        previous_data = json.load(f)

    # Dictionary with id as key
    current_dict = {item["id"]: item for item in current_data}
    previous_dict = {item["id"]: item for item in previous_data}

    # Addition maintaining order of current
    addition = [item for item in current_data if item["id"] not in previous_dict]

    # Deletion maintaining order of previous
    deletion = [item for item in previous_data if item["id"] not in current_dict]

    # Write to addition.json.tmp
    with open(addition_temp, "w", encoding="utf-8") as f:
        json.dump(addition, f, ensure_ascii=False, indent=2)
    save_temp_json_to_json(addition_temp)

    # Write to deletion.json.tmp
    with open(deletion_temp, "w", encoding="utf-8") as f:
        json.dump(deletion, f, ensure_ascii=False, indent=2)
    save_temp_json_to_json(deletion_temp)

if __name__ == "__main__":
    create_addition_and_deletion_json("/cache")
