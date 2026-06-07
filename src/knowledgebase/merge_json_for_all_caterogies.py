import os
import json

def merge_json_for_all_categories(category_paths: list[str]) -> str:

    papers_in_all_categories = []
    for category_path in category_paths:
        with open(category_path, "r", encoding="utf-8") as f:
            papers_in_a_category = json.load(f)
            if isinstance(papers_in_a_category, list):
                    papers_in_all_categories.extend(papers_in_a_category)
    
    # --- 重複削除 ---
    unique = {}

    for p in papers_in_all_categories:
        pid = p["id"]
        updated = p["updated"]

        # 初めて見る id → 登録
        if pid not in unique:
            unique[pid] = p
            
        else:
            # 既に同じ id がある場合 → updated が新しい方を残す
            if updated > unique[pid]["updated"]:
                unique[pid] = p

        # unique の値だけを papers に戻す
    papers_in_all_categories = list(unique.values())

    papers_in_all_categories.sort(
        key=lambda p: (
        p["updated"],          # まず updated でソート
        p["id"]                # updated が同じなら id でソート
        ),
        reverse=True           # 降順
    )

    # Save to JSON
    current_temp_path = os.path.join(os.path.dirname(category_paths[0]), "all_categories.json.tmp")
    with open(current_temp_path, "w", encoding="utf-8") as f:
        json.dump(papers_in_all_categories, f, ensure_ascii=False, indent=2)

    return current_temp_path

if __name__ == "__main__":
    current_temp_path = merge_json_for_all_categories(['/cache/cs.AI.json', '/cache/cs.LG.json', '/cache/stat.ML.json', '/cache/cs.CL.json', '/cache/cs.CV.json', '/cache/cs.NE.json'])
    print(current_temp_path)
