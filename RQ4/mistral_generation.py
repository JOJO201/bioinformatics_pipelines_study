import json
import time
import requests
import csv
from pathlib import Path

# ——— CONFIGURATION ———
INVOKE_URL     = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY        = "YOUR_NVIDIA_API_KEY"
INPUT_JSON     = Path("biostars_classified.json")        # Input Q&A + classification
OUTPUT_JSON    = Path("biostars_with_mistral.json")      # Enriched output
OUTPUT_CSV     = Path("biostars_mistral_answers.csv")    # CSV output

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

MODEL_NAME   = "mistralai/mistral-medium-3-instruct"
MAX_TOKENS   = 512
TEMPERATURE  = 1.00
TOP_P        = 1.00
PAUSE_SEC    = 2
# ————————————————

def generate_with_mistral(question: str) -> str:
    """Generate an answer using Mistral via NVIDIA API."""
    payload = {
        "model":       MODEL_NAME,
        "messages":    [{"role": "system", "content": "You are a knowledgeable bioinformatics assistant."},
                        {"role": "user",   "content": question}],
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
    # Load classified Q&A
    qa_list = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    enriched = []

    for idx, item in enumerate(qa_list, start=1):
        question = item["question_text"]
        print(f"[{idx}/{len(qa_list)}] Generating Mistral answer for post {item['post_id']}…")
        mistral_answer = generate_with_mistral(question)
        item["mistral_answer"] = mistral_answer
        enriched.append(item)
        time.sleep(PAUSE_SEC)

    # Save enriched JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(enriched, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"✅ Saved enriched JSON → {OUTPUT_JSON}")

    # Write CSV
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "post_id", "url", "title",
            "category_id", "category_name",
            "question_text", "accepted_answer", "mistral_answer"
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
                it.get("mistral_answer", "").replace("\n", " ")
            ])
    print(f"✅ Saved CSV → {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
