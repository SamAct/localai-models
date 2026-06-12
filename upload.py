#!/usr/bin/env python3
"""
Mirror the LocalAI app-family models to your OWN public, ungated HuggingFace repos,
attach the required Gemma NOTICE, and regenerate the app catalog (allowlist JSON) to
point at your repos.

Why: the answerer (Gemma 4 E4B/E2B) lives on the *public* litert-community HF repos and
the embedder (EmbeddingGemma) lives on a *gated* one. Mirroring all three under your own
account removes the gate (no HF token in the app), gives you stable URLs you control, and
keeps the apps off Google's repos entirely. Re-hosting is permitted by the Gemma Terms of
Use as long as each repo carries the NOTICE (see NOTICE.txt) — handled here.

PREREQS (see README.md for detail):
  1. huggingface_hub installed (already present in this environment).
  2. An HF *write* token:  setx HF_TOKEN hf_xxx   (new shell)   — or run `hf auth login`.
  3. ONE-TIME: accept the Gemma license on the gated SOURCE embedder repo so your token can
     pull it:  https://huggingface.co/litert-community/embeddinggemma-300m  (click "Agree").
     The two answerer source repos are public — nothing to accept.

RUN:
  python upload.py --dry-run     # print the plan, touch nothing
  python upload.py               # create repos + mirror every file + attach NOTICE + regen catalog
"""
import argparse
import json
import os
import sys

from huggingface_hub import HfApi, hf_hub_download, whoami

HERE = os.path.dirname(os.path.abspath(__file__))
# Reuse the already-downloaded E4B to skip a 3.66 GB re-download if present.
LOCAL_E4B = r"D:/Projects/AGENTIC/edge-genai/models/gemma-4-E4B-it.litertlm"

# Each mirror repo keeps the SAME name as its litert-community source.
MODELS = [
    {
        "repo": "gemma-4-E4B-it-litert-lm",
        "src": "litert-community/gemma-4-E4B-it-litert-lm",
        "files": ["gemma-4-E4B-it.litertlm"],
        "local": {"gemma-4-E4B-it.litertlm": LOCAL_E4B},
        "gated_src": False,
    },
    {
        "repo": "gemma-4-E2B-it-litert-lm",
        "src": "litert-community/gemma-4-E2B-it-litert-lm",
        "files": ["gemma-4-E2B-it.litertlm"],
        "local": {},
        "gated_src": False,
    },
    {
        "repo": "embeddinggemma-300m",
        "src": "litert-community/embeddinggemma-300m",
        "files": ["embeddinggemma-300M_seq256_mixed-precision.tflite", "sentencepiece.model"],
        "local": {},
        "gated_src": True,  # you must accept the Gemma license on the SOURCE repo first
    },
]

# The two answerer entries whose `url` in the catalog must point at your mirror.
ANSWERER_MIRRORS = {
    "litert-community/gemma-4-E4B-it-litert-lm": "gemma-4-E4B-it-litert-lm",
    "litert-community/gemma-4-E2B-it-litert-lm": "gemma-4-E2B-it-litert-lm",
}


def regen_allowlist(user: str) -> None:
    """Rewrite model_allowlists/1_0_15.json from Google's snapshot, pointing answerer
    `url`s at `user`'s mirror repos. Safe to run repeatedly."""
    src = os.path.join(HERE, "google_1_0_15.json")
    dst = os.path.join(HERE, "model_allowlists", "1_0_15.json")
    d = json.load(open(src, encoding="utf-8"))
    n = 0
    for m in d["models"]:
        repo = ANSWERER_MIRRORS.get(m.get("modelId", ""))
        if repo:
            m["url"] = f"https://huggingface.co/{user}/{repo}/resolve/main/{m['modelFile']}?download=true"
            n += 1
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    json.dump(d, open(dst, "w", encoding="utf-8"), indent=2)
    print(f"  regenerated catalog with {n} answerer url overrides -> {user}/*")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = os.environ.get("HF_TOKEN")
    api = HfApi(token=token)
    try:
        user = whoami(token=token)["name"]
    except Exception as e:  # noqa: BLE001
        sys.exit(f"Not authenticated. Set HF_TOKEN or run `hf auth login`. ({e})")
    print(f"Authenticated as HF user: {user}")

    notice = open(os.path.join(HERE, "NOTICE.txt"), encoding="utf-8").read()

    print("\n== Catalog ==")
    regen_allowlist(user)

    for m in MODELS:
        dst = f"{user}/{m['repo']}"
        gated = " [GATED source — accept its license first]" if m["gated_src"] else ""
        print(f"\n== {dst} (from {m['src']}){gated} ==")
        if args.dry_run:
            for f in m["files"]:
                print(f"  would mirror {f}")
            continue
        api.create_repo(dst, repo_type="model", private=False, exist_ok=True)
        api.upload_file(path_or_fileobj=notice.encode(), path_in_repo="NOTICE.txt", repo_id=dst)
        for f in m["files"]:
            if api.file_exists(dst, f):  # idempotent: re-runs only do what's missing
                print(f"  skip {f} (already on {dst})")
                continue
            local = m["local"].get(f)
            if local and os.path.exists(local):
                src_path = local
                print(f"  using local {f}")
            else:
                print(f"  downloading {f} from {m['src']} ...")
                src_path = hf_hub_download(m["src"], f, token=token)
            print(f"  uploading {f} -> {dst} ...")
            api.upload_file(path_or_fileobj=src_path, path_in_repo=f, repo_id=dst)
        print(f"  done -> https://huggingface.co/{dst}")

    if not args.dry_run:
        print(
            "\nAll models mirrored. Next:\n"
            "  1. Commit + push the regenerated model_allowlists/1_0_15.json in this repo.\n"
            "  2. Apply app-changes.md (ALLOWLIST_BASE_URL + embedder repo), rebuild, push the apps."
        )


if __name__ == "__main__":
    main()
