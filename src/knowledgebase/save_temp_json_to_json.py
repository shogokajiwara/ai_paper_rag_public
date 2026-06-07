import os

def save_temp_json_to_json(temp_path: str) ->str:
    """
    Atomically saves to a .json file.
    """
    path = temp_path.removesuffix(".tmp")
    os.replace(temp_path, path)

    return path

if __name__ == "__main__":
    path = save_temp_json_to_json("/cache/all_categories.json.tmp")
    print(path)
