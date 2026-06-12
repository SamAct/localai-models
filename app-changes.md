# App changes — point the apps at your self-hosted models

Apply these **after** `upload.py` succeeds and this catalog repo is pushed (so the URLs
resolve). Two one-line constant changes; then rebuild + push the apps.

## 1. Catalog URL — BOTH apps

The apps fetch `…/model_allowlists/1_0_15.json`. Point that base at this catalog repo's raw
URL (which serves the answerer `url` overrides to your HF mirrors).

**File:** `…/ui/modelmanager/ModelManagerViewModel.kt`  (LocalDocs **and** LocalNotes)

```kotlin
// before
private const val ALLOWLIST_BASE_URL =
  "https://raw.githubusercontent.com/google-ai-edge/gallery/refs/heads/main/model_allowlists"
// after
private const val ALLOWLIST_BASE_URL =
  "https://raw.githubusercontent.com/SamAct/localai-models/main/model_allowlists"
```

## 2. Embedder repo — LocalDocs only

**File:** `…/data/library/EmbedderModelStore.kt`

```kotlin
// before
private const val EMBEDDER_HF_REPO = "litert-community/embeddinggemma-300m"
// after  (your public mirror — no HF token needed anymore)
private const val EMBEDDER_HF_REPO = "SamAct/embeddinggemma-300m"
```

`EMBEDDER_HF_COMMIT = "main"` stays. The `Bearer` token path is now dead weight (the repo is
public) but harmless — leave it, or pass `null` to `downloadEmbedder(...)`. LocalNotes has no
embedder, so it needs only change #1.

## 3. Rebuild, verify, commit, push

```powershell
# LocalDocs
cd "D:\Projects\AGENTIC\edge-genai\apps\localdocs\Android\src"; .\gradlew :app:assembleDebug -x lintDebug
# LocalNotes
cd "D:\Projects\AGENTIC\edge-genai\repos\gallery\Android\src"; .\gradlew :app:assembleDebug -x lintDebug
```

Verify on device: a fresh install's Download gate should now fetch the answerer from
`huggingface.co/<you>/…` (check `AGDownloadWorker: About to download …` in logcat), and
"smarter search" should fetch the embedder with **no** token prompt. Then commit + push both
app repos.

> If your HuggingFace username is **not** `SamAct`: the catalog (`1_0_15.json`) is regenerated
> by `upload.py` with your real HF handle, so only the **GitHub** owner in the URL above stays
> `SamAct` (that's your GitHub account, which hosts this catalog). No edit needed.
