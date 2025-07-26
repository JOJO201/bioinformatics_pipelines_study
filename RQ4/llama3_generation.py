import json
import time
import csv
from pathlib import Path
from openai import OpenAI

# ——— CONFIGURATION ———
NV_API_KEY        = "YOUR_NVIDIA_API_KEY"
BASE_URL          = "https://integrate.api.nvidia.com/v1"
INPUT_JSON        = Path("biostars_classified.json")
OUTPUT_JSON       = Path("biostars_with_llama3.json")
OUTPUT_CSV        = Path("biostars_llama3_answers.csv")

MODEL_NAME        = "nvidia/llama-3.3-nemotron-super-49b-v1"
TEMPERATURE       = 0.6
TOP_P             = 0.95
MAX_TOKENS        = 4096
FREQ_PENALTY      = 0
PRES_PENALTY      = 0
PAUSE_SEC         = 2
# ————————————————

# Initialize NVIDIA-backed client
client = OpenAI(
    base_url = BASE_URL,
    api_key  = NV_API_KEY
)

def generate_with_llama3(question: str) -> str:
    """Generate an answer using NVIDIA Llama 3.3 (non-streaming)."""
    resp = client.chat.completions.create(
        model             = MODEL_NAME,
        messages          = [
            {"role": "system", "content": "You are a knowledgeable bioinformatics assistant."},
            {"role": "user",   "content": question}
        ],
        temperature       = TEMPERATURE,
        top_p             = TOP_P,
        max_tokens        = MAX_TOKENS,
        frequency_penalty = FREQ_PENALTY,
        presence_penalty  = PRES_PENALTY,
        stream            = False
    )
    return resp.choices[0].message.content.strip()

def main():
    # Load classified Q&A data
    qa_list = json.loads(INPUT_JSON.read_text(encoding="utf-8"))

    enriched = []
    for idx, item in enumerate(qa_list, start=1):
        question = item["question_text"]
        print(f"[{idx}/{len(qa_list)}] Generating Llama3 answer for post {item['post_id']}…")
        llama_answer = generate_with_llama3(question)
        item["llama3_answer"] = llama_answer
        enriched.append(item)
        time.sleep(PAUSE_SEC)

    # Save enriched JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(enriched, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"✅ Saved enriched JSON → {OUTPUT_JSON}")

    # Write out CSV
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "post_id","url","title",
            "category_id","category_name",
            "question_text","accepted_answer","llama3_answer"
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
                it.get("llama3_answer","").replace("\n"," ")
            ])
    print(f"✅ Saved CSV → {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
