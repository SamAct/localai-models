# Model manifest — LocalAI app family

What each app downloads, the source (Google's litert-community) repo, and your mirror.
All sizes/commits are from Google's `1_0_15` allowlist snapshot (`google_1_0_15.json`).
SHA-256 is recorded after the first `upload.py` run (the answerer files are large; verify
on device against `sizeInBytes`).

| File | Used by | Size | Source (gated?) | Your mirror (public) |
|---|---|---|---|---|
| `gemma-4-E4B-it.litertlm` | LocalDocs answerer (default) | 3.66 GB | `litert-community/gemma-4-E4B-it-litert-lm` (public) | `<you>/gemma-4-E4B-it-litert-lm` |
| `gemma-4-E2B-it.litertlm` | LocalNotes answerer (default) | 2.59 GB | `litert-community/gemma-4-E2B-it-litert-lm` (public) | `<you>/gemma-4-E2B-it-litert-lm` |
| `embeddinggemma-300M_seq256_mixed-precision.tflite` | LocalDocs "smarter search" | 179 MB | `litert-community/embeddinggemma-300m` (**GATED**) | `<you>/embeddinggemma-300m` |
| `sentencepiece.model` | embedder tokenizer | 4.7 MB | `litert-community/embeddinggemma-300m` (**GATED**) | `<you>/embeddinggemma-300m` |

Known hashes (local copies):
- `gemma-4-E4B-it.litertlm` sha256 `0b2a8980ce155fd97673d8e820b4d29d9c7d99b8fa6806f425d969b145bd52e0` (commit `28299f30…` on the source).

Catalog: `model_allowlists/1_0_15.json` is Google's snapshot with the two answerer entries'
`url` fields overridden to your mirror. The embedder is NOT in this catalog — the app reads
its repo from `EmbedderModelStore.kt` constants (see `app-changes.md`).

Total to serve per fresh install: ~3.84 GB (answerer + embedder). HuggingFace serves it free
from its CDN; no egress cost to you.
