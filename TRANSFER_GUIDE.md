# Subtext AI Transfer Guide

This guide is for moving the project to another machine **without using Git**.

Your current goal is:
- transfer the project by copy/zip
- keep **all `intent30` models**
- skip the dissonance models because they are not your final focus

## What To Copy

### Required Project Files
Copy these folders/files:
- `src/`
- `ui/`
- `scripts/`
- `skills/`
- `data/processed/`
- `requirements.txt`
- `MODEL_ARTIFACT.md`
- `AGENTS.md`
- `TRANSFER_GUIDE.md`

### Required Intent Models
Copy all current `intent30` model folders:
- `models/intent30_text_emoji_baseline`
- `models/intent30_text_emoji_weighted`
- `models/intent30_text_only_baseline`

## What You Can Skip

You do **not** need to copy:
- `ui/node_modules/`
- `__pycache__/`
- `.venv/` or `venv/`
- `.git/`
- `data/uploads/`
- dissonance model folders such as:
  - `models/dissonance3_text_emoji_weighted`
  - `models/dissonance3_text_only_weighted`
  - `models/dissonance_debug`
  - `models/dissonance_mini`
- old architecture experiment folders such as:
  - `models/arch_baseline`
  - `models/arch_bertweet`
  - `models/arch_dual_encoder`
  - `models/arch_weighted`
  - `models/arch_weighted_full`

## Recommended Transfer Method

### Option 1: Copy to External Drive
1. Copy the whole `subtext-ai` folder.
2. Before copying, remove or exclude the folders listed in `What You Can Skip`.
3. Make sure the three `intent30` model folders are included.
4. Paste the project onto the new machine.

### Option 2: Zip the Project
1. Create a zip of the `subtext-ai` folder.
2. Exclude:
   - `ui/node_modules/`
   - `.venv/` or `venv/`
   - `__pycache__/`
   - `data/uploads/`
   - all dissonance model folders
   - old experimental architecture model folders
3. Keep the three `intent30` model folders inside `models/`.
4. Move the zip to the new machine and extract it.

## Important Size Note

The `intent30` models are large.

Approximate sizes:
- `models/intent30_text_emoji_baseline`: about `7.6 GB`
- `models/intent30_text_emoji_weighted`: about `7.6 GB`
- `models/intent30_text_only_baseline`: about `7.6 GB`

If you copy all three `intent30` models, expect about `22 to 23 GB` just for models.

## New Machine Prerequisites

Install:
- Python `3.10+`
- Node.js `20+`

## Backend Setup On The New Machine

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Frontend Setup On The New Machine

```powershell
cd ui
npm install
cd ..
```

## Optional CUDA / GPU Setup

If you want GPU support on the new machine:

```powershell
pip install --upgrade --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

Then verify:

```powershell
@'
import torch
print(torch.__version__)
print(torch.cuda.is_available())
if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
'@ | python -
```

## Run The Project On The New Machine

Use two terminals.

### Terminal 1: Backend
```powershell
cd C:\dev\subtext-ai
.\venv\Scripts\activate
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: Frontend
```powershell
cd C:\dev\subtext-ai\ui
npm run dev
```

## URLs

- Frontend: `http://localhost:5173`
- Backend docs: `http://127.0.0.1:8000/docs`

## Quick Checklist

- Copy the project folder
- Keep all three `intent30` model folders
- Skip dissonance models
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Start backend
- Start frontend
- Test the upload flow

## Fastest Practical Recommendation

If you want the simplest transfer:

1. Copy the entire project folder.
2. Delete these before transfer:
   - `ui/node_modules`
   - `venv` or `.venv`
   - `data/uploads`
   - all `dissonance*` model folders
   - all `arch_*` model folders
3. Keep:
   - `models/intent30_text_emoji_baseline`
   - `models/intent30_text_emoji_weighted`
   - `models/intent30_text_only_baseline`
4. On the new machine, reinstall Python and Node dependencies.
5. Run backend and frontend.

That will give you the intent-focused version of the project on the new machine.
