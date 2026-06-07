import re
import requests
import os
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
BASE_URL = "https://oaipmh.arxiv.org/oai"
ARXIV_NS = "{http://arxiv.org/OAI/arXiv/}"

def fetch_arxiv_papers(category: str, cache_dir: str) -> str:

    head, tail = category.split(".")
    set_spec = f"{head}:{head}:{tail}"

    path = os.path.join(cache_dir, f"{category}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            papers = json.load(f)
        latest_date = max(paper["updated"] for paper in papers)
        start_day = latest_date
    except:
        start_day = (datetime.now(timezone.utc) - relativedelta(years=1)).strftime("%Y-%m-%d")
        papers = []
   
    params = {
        "verb": "ListRecords",
        "metadataPrefix": "arXiv",
        "from": start_day,
        "set": set_spec
    }

    
    while True:
        resp = requests.get(BASE_URL, params=params, timeout=300)
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        ns = {"oai": "http://www.openarchives.org/OAI/2.0/"}

        for record in root.findall(".//oai:record", ns):
            metadata = record.find("oai:metadata", ns)
            if metadata is None:
                continue

            # namespace 付き arXiv ノードを取得
            arxiv = metadata.find(f"{ARXIV_NS}arXiv")
            if arxiv is None:
                continue

            paper =  {
                "id": arxiv.findtext(f"{ARXIV_NS}id"),
                "title": arxiv.findtext(f"{ARXIV_NS}title"),
                "authors": [
                    (
                        a.findtext(f"{ARXIV_NS}name")
                        or (
                            ((a.findtext(f"{ARXIV_NS}forenames") or "") + " " +
                             (a.findtext(f"{ARXIV_NS}keyname") or "")).strip()
                        )
                    )
                    for a in arxiv.findall(f"{ARXIV_NS}authors/{ARXIV_NS}author")
                ],

                "abstract": arxiv.findtext(f"{ARXIV_NS}abstract"),
                "categories": arxiv.findtext(f"{ARXIV_NS}categories"),
                "updated": arxiv.findtext(f"{ARXIV_NS}updated"),
            }
            papers.insert(0, paper)
        
        # --- 重複削除 ---
        unique = {}

        for p in papers:
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
        papers = list(unique.values())

        papers.sort(
            key=lambda p: (
            p["updated"],          # まず updated でソート
            p["id"]                # updated が同じなら id でソート
            ),
            reverse=True           # 降順
        )

        # --- start_day より updated が古い論文を削除 ---
        papers = [p for p in papers if p["updated"] >= start_day]

        token = root.find(".//oai:resumptionToken", ns)
        if token is None or token.text is None:
            break

        params = {"verb": "ListRecords", "resumptionToken": token.text}

    # paper format check
    paper_pattern = {
    "id": r"^(\d{4}\.\d{4,5}(v\d+)?|[a-zA-Z\-]+\/\d{7}(v\d+)?)$",
    "title": r".+",
    "authors": list,
    "updated": r"^\d{4}-\d{2}-\d{2}$",
    "abstract": str,
    "categories": str,
    }

    for idx, paper in enumerate(papers):

        # --- 必須キーの存在チェック ---
        for key in paper_pattern:
            assert key in paper, f"Paper {idx} is missing key: {key}"

        # --- 型チェック or 正規表現チェック ---
        for key, rule in paper_pattern.items():

            value = paper[key]

            # 型チェック（rule が type の場合）
            if isinstance(rule, type):
                assert isinstance(value, rule), (
                    f"Invalid type for {key}: expected {rule}, got {type(value)}"
                )

            # 正規表現チェック（rule が str の場合）
            elif isinstance(rule, str):
                assert re.fullmatch(rule, str(value)), (
                    f"Invalid format for {key}: {value}"
                )

            else:
                raise ValueError(f"Invalid rule for {key}: {rule}")
    
    for i in range(len(papers) - 1):

        p1 = papers[i]
        p2 = papers[i + 1]

        # updated が降順になっているか
        assert p1["updated"] >= p2["updated"], (
            f"Sort error: updated order incorrect between {p1['id']} and {p2['id']}"
        )

        # updated が同じなら id が降順になっているか
        if p1["updated"] == p2["updated"]:
            assert p1["id"] >= p2["id"], (
                f"Sort error: id order incorrect between {p1['id']} and {p2['id']}"
            )
            
    # --- id 重複チェック ---
    seen_ids = set()
    for p in papers:
        pid = p["id"]
        assert pid not in seen_ids, f"Duplicate id found: {pid}"
        seen_ids.add(pid)
            
    # --- start_day より前の updated が存在しないことを確認 ---
    for p in papers:
        assert p["updated"] >= start_day, (
            f"Found outdated paper: id={p['id']} updated={p['updated']} < start_day={start_day}"
        )

    os.makedirs(cache_dir, exist_ok=True)
    current_temp_path = os.path.join(cache_dir, f"{category}.json.tmp")

    # Write to temporary file
    with open(current_temp_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    return current_temp_path


if __name__ == "__main__":
    current_temp_path = fetch_arxiv_papers("cs.AI","/cache")
    print(current_temp_path)