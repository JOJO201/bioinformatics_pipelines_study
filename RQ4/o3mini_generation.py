import json
import time
import csv
from openai import OpenAI
from pathlib import Path

from openai import Client

# Set up your API key (ensure OPENAI_API_KEY is set in your environment or replace with your key)
client = Client(api_key='apikey')
# ——— CONFIG ———
INPUT_JSON        = Path("biostars_classified.json")   # or your JSON with questions & metadata
OUTPUT_JSON       = Path("biostars_with_answers.json") # optional: to save enriched JSON
OUTPUT_CSV        = Path("biostars_answers.csv")

MODEL_O3MINI      = "o3-mini"
PAUSE_SEC         = 2
# ————————————————



def generate_answer_o3mini(question: str) -> str:
    """Generate an answer with o3-mini and high reasoning effort."""
    resp = client.chat.completions.create(
        model=MODEL_O3MINI,
        messages=[
            {"role": "system", "content": "You are a knowledgeable bioinformatics assistant."},
            {"role": "user",   "content": question}
        ],
        reasoning_effort="high"
    )
    return resp.choices[0].message.content.strip()

def main():
    # load the JSON of Q&A and classifications
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))

    # enrich each record with a model answer
    for idx, item in enumerate(data, start=1):
        q = item.get("question_text", "")
        print(f"[{idx}/{len(data)}] Generating answer for post {item.get('post_id')}...")
        item["model_answer"] = generate_answer_o3mini(q)
        time.sleep(PAUSE_SEC)

    # (Optional) save enriched JSON
    OUTPUT_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # write out CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # header
        writer.writerow([
            "post_id",
            "url",
            "title",
            "question_text",
            "accepted_answer",
            "category_id",
            "category_name",
            "model_answer"
        ])
        # rows
        for item in data:
            cat = item.get("classification", {})
            writer.writerow([
                item.get("post_id", ""),
                item.get("url", ""),
                item.get("title", "").replace("\n", " "),
                item.get("question_text", "").replace("\n", " "),
                item.get("accepted_answer", "").replace("\n", " "),
                cat.get("category_id", ""),
                cat.get("category_name", ""),
                item.get("model_answer", "").replace("\n", " ")
            ])

    print(f"\n✅ Answers generated and saved to:\n  JSON: {OUTPUT_JSON}\n  CSV:  {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
