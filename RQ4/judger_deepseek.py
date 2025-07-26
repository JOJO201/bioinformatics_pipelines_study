import json
import time
from openai import OpenAI
from pathlib import Path
from openai import Client

# Set up your API key (ensure OPENAI_API_KEY is set in your environment or replace with your key)
client = Client(api_key='yourkey')
# ——— CONFIG ———
INPUT_JSON        = Path("biostars_deepseek.json")  # has model_answer + classification
OUTPUT_JSON       = Path("biostars_judged_deepseek.json")

MODEL_JUDGE       = "o4-mini"
PAUSE_SEC         = 2
# ————————————————


def judge_answer(question: str, model_answer: str, gold_answer: str) -> dict:
    """Ask o3-mini to judge if the model_answer is acceptable."""
    prompt = f"""
You are an impartial expert in bioinformatics pipelines.

Question:
\"\"\"{question}\"\"\"

Model’s Answer:
\"\"\"{model_answer}\"\"\"

Accepted (Gold) Answer:
\"\"\"{gold_answer}\"\"\"

Is the model’s answer acceptable?  
Respond _only_ as JSON with:
{{
  "acceptable": <true or false>,
  "justification": "<one-sentence rationale>"
}}
"""
    resp = client.chat.completions.create(
        model=MODEL_JUDGE,
        messages=[
            {"role": "system",  "content": "You are a strict, unbiased evaluator."},
            {"role": "user",    "content": prompt}
        ],
        reasoning_effort="high"
    )
    text = resp.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # fallback to marking unacceptable if parse fails
        return {"acceptable": False, "justification": text}

def main():
    # load your JSON which already has classification + model_answer
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    output = []

    for idx, item in enumerate(data, 1):
        print(f"[{idx}/{len(data)}] Judging post {item.get('post_id')}…")
        q   = item.get("question_text", "")
        ma  = item.get("deepseek_answer", "")
        ga  = item.get("accepted_answer", "")
        # carry over classification
        cls = item.get("classification", {})

        judgment = judge_answer(q, ma, ga)
        # build final record
        record = {
            "post_id":        item.get("post_id"),
            "url":            item.get("url"),
            "title":          item.get("title"),
            "question_text":  q,
            "accepted_answer":ga,
            "deepseek_answer":   ma,
            "classification": {
                "category_id":   cls.get("category_id"),
                "category_name": cls.get("category_name")
            },
            "judgment": judgment
        }
        output.append(record)
        time.sleep(PAUSE_SEC)

    # write out enriched JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"\n✅ Saved judged results with categories → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
