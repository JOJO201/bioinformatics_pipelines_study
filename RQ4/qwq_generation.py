import json
import time
import csv
from pathlib import Path
from openai import OpenAI

# ——— CONFIGURATION ———
API_KEY        = "YOUR_API_KEY"
BASE_URL       = "https://integrate.api.nvidia.com/v1"
INPUT_JSON     = Path("biostars_classified.json")    # update path if needed
OUTPUT_JSON    = Path("biostars_with_qwq_200.json")
OUTPUT_CSV     = Path("biostars_qwq_answers_200.csv")

MODEL_NAME     = "qwen/qwq-32b"
TEMPERATURE    = 0.6
TOP_P          = 0.7
MAX_TOKENS     = 4096
PAUSE_SEC      = 2
# ————————————————

# initialize NVIDIA-backed client
client = OpenAI(
    base_url = BASE_URL,
    api_key  = API_KEY
)

def generate_with_qwq(question: str) -> str:
    """Generate an answer using the QWQ model."""
    resp = client.chat.completions.create(
        model       = MODEL_NAME,
        messages    = [
            {"role": "system", "content": "You are a knowledgeable bioinformatics assistant."},
            {"role": "user",   "content": question}
        ],
        temperature = TEMPERATURE,
        top_p       = TOP_P,
        max_tokens  = MAX_TOKENS,
        stream      = False
    )
    return resp.choices[0].message.content.strip()

def main():
    # load your classified Q&A
    qa_list = json.loads(INPUT_JSON.read_text(encoding="utf-8"))[:200]
    enriched = []

    for idx, item in enumerate(qa_list, start=1):
        question = item["question_text"]
        print(f"[{idx}/{len(qa_list)}] Generating QWQ answer for post {item['post_id']}…")
        qwq_answer = generate_with_qwq(question)
        item["qwq_answer"] = qwq_answer
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
            "question_text", "accepted_answer", "qwq_answer"
        ])
        for it in enriched:
            cls = it.get("classification", {})
            writer.writerow([
                it.get("post_id",""),
                it.get("url",""),
                it.get("title","").replace("\n"," "),
                cls.get("category_id",""),
                cls.get("category_name",""),
                it.get("question_text","").replace("\n"," "),
                it.get("accepted_answer","").replace("\n"," "),
                it.get("qwq_answer","").replace("\n"," ")
            ])
    print(f"✅ Saved CSV → {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
