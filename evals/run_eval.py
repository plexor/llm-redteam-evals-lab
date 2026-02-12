import argparse
import csv
import datetime
import json
from collections import Counter
from pathlib import Path
from typing import Any


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON at line {idx} in {path}: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"Expected object at line {idx} in {path}, got {type(payload).__name__}")
        items.append(payload)
    return items


def validate_prompt(prompt: dict[str, Any], idx: int) -> None:
    missing = [field for field in ("id", "category", "prompt") if field not in prompt]
    if missing:
        fields = ", ".join(missing)
        raise ValueError(f"Prompt #{idx} is missing required field(s): {fields}")


def build_results(prompts: list[dict[str, Any]], model: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for idx, prompt in enumerate(prompts, start=1):
        validate_prompt(prompt, idx)
        results.append(
            {
                "prompt_id": prompt["id"],
                "category": prompt["category"],
                "prompt": prompt["prompt"],
                "expected_behavior": prompt.get("expected_behavior", ""),
                "model": model,
                "output": "[TODO connect model]",
                "label": "UNLABELED",
                "failure_tags": [],
                "notes": "",
            }
        )
    return results


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "prompt_id",
        "category",
        "prompt",
        "expected_behavior",
        "model",
        "output",
        "label",
        "failure_tags",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row_copy = dict(row)
            row_copy["failure_tags"] = ";".join(row_copy.get("failure_tags", []))
            writer.writerow(row_copy)


def build_summary(results: list[dict[str, Any]], dataset_path: str, model: str, run_id: str) -> dict[str, Any]:
    by_category = Counter(item["category"] for item in results)
    return {
        "run_id": run_id,
        "created_at_utc": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "dataset": dataset_path,
        "model": model,
        "total_prompts": len(results),
        "by_category": dict(sorted(by_category.items())),
    }


def unique_artifact_path(base_dir: Path, base_name: str, suffix: str) -> Path:
    candidate = base_dir / f"{base_name}.{suffix}"
    if not candidate.exists():
        return candidate

    counter = 1
    while True:
        candidate = base_dir / f"{base_name}_{counter}.{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", default="results")
    ap.add_argument("--max-prompts", type=positive_int, default=None, help="Limit number of prompts for quick runs")
    ap.add_argument("--max-prompts", type=int, default=None, help="Limit number of prompts for quick runs")
    ap.add_argument(
        "--format",
        choices=("json", "json+csv"),
        default="json",
        help="Output artifact format",
    )
    ap.add_argument(
        "--summary",
        action="store_true",
        help="Emit a run summary JSON alongside result artifacts",
    )
    ap.add_argument(
        "--run-id",
        default=None,
        help="Optional run id to make output names reproducible. Default: current UTC timestamp.",
    )
    args = ap.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        ap.error(f"--dataset path does not exist: {dataset_path}")

    try:
        prompts = load_jsonl(dataset_path)
        if args.max_prompts is not None:
            prompts = prompts[: args.max_prompts]
        results = build_results(prompts, args.model)
    except ValueError as exc:
        ap.error(str(exc))

    run_id = args.run_id or datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")

    out_dir = Path(args.out) / args.model
    out_dir.mkdir(parents=True, exist_ok=True)

    json_file = unique_artifact_path(out_dir, f"run_{run_id}", "json")
    json_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("Wrote:", json_file)

    if args.format == "json+csv":
        csv_file = unique_artifact_path(out_dir, f"run_{run_id}", "csv")
        write_csv(csv_file, results)
        print("Wrote:", csv_file)

    if args.summary:
        summary = build_summary(results, str(dataset_path), args.model, run_id)
        summary_file = unique_artifact_path(out_dir, f"run_{run_id}_summary", "json")
        summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print("Wrote:", summary_file)

    results = build_results(prompts, args.model)

    out_file = out_dir / f"run_{run_id}.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("Wrote:", out_file)

    if args.format == "json+csv":
        csv_file = out_dir / f"run_{run_id}.csv"
        write_csv(csv_file, results)
        print("Wrote:", csv_file)

    if args.summary:
        summary = build_summary(results, args.dataset, args.model, run_id)
        summary_file = out_dir / f"run_{run_id}_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print("Wrote:", summary_file)


if __name__ == "__main__":
    main()
