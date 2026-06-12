# LocalAI model hosting

Self-hosting for the **LocalDocs** and **LocalNotes** on-device apps. The apps download a
Gemma answerer (E4B / E2B) and an EmbeddingGemma search model; this repo makes those come
from **your** accounts instead of Google's, and un-gates the embedder.

## What goes where (and why not all in git)

| Asset | Host | In this repo? |
|---|---|---|
| Model binaries (~3.8 GB) | **HuggingFace** (your account, public, ungated) | ❌ no — git can't host GB files (100 MB push limit; LFS bandwidth is metered/$$). HF is a free, purpose-built model CDN. |
| Catalog (`model_allowlists/1_0_15.json`) | **this GitHub repo** (raw URL) | ✅ yes — small JSON, versioned, served public |
| `NOTICE.txt`, license pointer, manifest, upload script | this repo | ✅ yes |

So: **binaries on HuggingFace, everything text/config in git.** The apps fetch the catalog
JSON from this repo's raw URL; the catalog's `url` fields point at your HF model files.

## One-time setup (you must do — needs your credentials)

1. **HF write token** → https://huggingface.co/settings/tokens (role: *Write*). Then:
   ```powershell
   setx HF_TOKEN "hf_xxxxxxxx"      # open a NEW terminal after this
   ```
   (or `python -m huggingface_hub.commands.huggingface_cli login`).
2. **Accept the Gemma license** on the gated source embedder (one click), so your token can
   pull it for mirroring: https://huggingface.co/litert-community/embeddinggemma-300m
   *(The two answerer source repos are public — nothing to accept.)*

## Mirror the models

```powershell
python upload.py --dry-run     # sanity-check the plan
python upload.py               # creates <you>/gemma-4-E4B-it-litert-lm, …-E2B…, …/embeddinggemma-300m,
                               # uploads each file, attaches NOTICE.txt, and regenerates the catalog JSON
```
Reuses the local 3.66 GB E4B copy if present (skips a re-download). Expect a while for the
E2B + embedder pulls + the 3 uploads.

## Publish the catalog + repoint the apps

```powershell
git add model_allowlists/1_0_15.json && git commit -m "catalog: point answerers at my HF mirror" && git push
```
Then apply **`app-changes.md`** (two one-line constants), rebuild, verify on device, and push
the app repos. Done — the apps now run entirely off your hosting.

## Files
- `upload.py` — mirror script (HuggingFace) + catalog regenerator.
- `model_allowlists/1_0_15.json` — the custom catalog the apps fetch (answerer `url`s → your HF).
- `google_1_0_15.json` — Google's upstream snapshot (source of truth for regen; don't edit).
- `NOTICE.txt` — Gemma §3.1 notice attached to every mirror repo.
- `MANIFEST.md` — file inventory + sizes + hashes.
- `app-changes.md` — the exact app edits to apply after mirroring.

## License / compliance
Redistributing Gemma is permitted by the [Gemma Terms of Use](https://ai.google.dev/gemma/terms)
provided each repo carries the notice (handled by `upload.py`) and downstream users are bound
to the [Prohibited Use Policy](https://ai.google.dev/gemma/prohibited_use_policy) — which the
apps already do via their in-app ToS. See `edge-genai/docs/MODEL_LICENSES.md` for the full read.
This is not legal advice; have counsel confirm before the paid launch.
