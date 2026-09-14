
import re
from collections import Counter


def parse_log_stats(log_path="rag_app.log"):

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {
            "total_searches": 0,
            "top_titles": [],
            "avg_score": 0.0,
            "total_answers": 0,
        }

    total_searches = 0
    total_answers = 0
    titles = []
    scores = []

    search_pattern = re.compile(r"Arama baslatildi\. Query: (.+?) \| top_k=")
    result_pattern = re.compile(r"Sonuc \| score=([\d.]+) \| title=(.+)")
    answer_pattern = re.compile(r"(History destekli cevap uretildi|Cevap uretildi)")

    for line in lines:
        if search_pattern.search(line):
            total_searches += 1
        result_match = result_pattern.search(line)
        if result_match:
            scores.append(float(result_match.group(1)))
            titles.append(result_match.group(2).strip())
        if answer_pattern.search(line):
            total_answers += 1

    top_titles = Counter(titles).most_common(5)
    avg_score = sum(scores) / len(scores) if scores else 0.0

    return {
        "total_searches": total_searches,
        "top_titles": top_titles,
        "avg_score": avg_score,
        "total_answers": total_answers,
    }