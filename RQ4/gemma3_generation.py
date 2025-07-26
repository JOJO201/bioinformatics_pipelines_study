import json
import time
import requests
import csv
from pathlib import Path

# ——— CONFIGURATION ———
INVOKE_URL     = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY        = "YOUR_API_KEY"
INPUT_JSON     = Path("biostars_classified.json")
OUTPUT_JSON    = Path("biostars_with_gemma3_600.json")
OUTPUT_CSV     = Path("biostars_gemma3_answers_600.csv")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

MODEL_NAME   = "google/gemma-3-27b-it"
MAX_TOKENS   = 4096
TEMPERATURE  = 0.20
TOP_P        = 0.70
PAUSE_SEC    = 2
# ————————————————

def generate_with_gemma3(question: str) -> str:
    payload = {
        "model":       MODEL_NAME,
        "messages":    [{"role": "user", "content": question}],
        "max_tokens":  MAX_TOKENS,
        "temperature": TEMPERATURE,
        "top_p":       TOP_P,
        "stream":      False
    }
    resp = requests.post(INVOKE_URL, headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

def main():
    # load your classified Q&A
    qa_list = json.loads(INPUT_JSON.read_text(encoding="utf-8"))[400:]
    enriched = []

    for idx, item in enumerate(qa_list, start=1):
        question = item["question_text"]
        print(f"[{idx}/{len(qa_list)}] Generating Gemma3 answer for post {item['post_id']}…")
        gemma3_answer=""
        try:
            gemma3_answer = generate_with_gemma3(question)
        except:
            print("error")
        item["gemma3_answer"] = gemma3_answer
        enriched.append(item)
        time.sleep(PAUSE_SEC)

    # save enriched JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(enriched, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"✅ Saved enriched JSON → {OUTPUT_JSON}")

    # write out CSV
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "post_id", "url", "title",
            "category_id", "category_name",
            "question_text", "accepted_answer", "gemma3_answer"
        ])
        for it in enriched:
            cls = it.get("classification", {})
            writer.writerow([
                it.get("post_id", ""),
                it.get("url", ""),
                it.get("title", "").replace("\n", " "),
                cls.get("category_id", ""),
                cls.get("category_name", ""),
                it.get("question_text", "").replace("\n", " "),
                it.get("accepted_answer", "").replace("\n", " "),
                it.get("gemma3_answer", "").replace("\n", " ")
            ])
    print(f"✅ Saved CSV → {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
