import argparse, json
from pathlib import Path
import datetime

def load_jsonl(path):
    items = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            items.append(json.loads(line))
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    prompts = load_jsonl(args.dataset)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    out_dir = Path(args.out) / args.model
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for p in prompts:
        results.append({
            "prompt_id": p["id"],
            "category": p["category"],
            "prompt": p["prompt"],
            "expected_behavior": p.get("expected_behavior",""),
            "model": args.model,
            "output": "[TODO connect model]",
            "label": "UNLABELED",
            "failure_tags": [],
            "notes": ""
        })

    out_file = out_dir / f"run_{ts}.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("Wrote:", out_file)

if __name__ == "__main__":
    main()
