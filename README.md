# 🧙🏻‍♂ 𝔪𝔢𝔪𝔢𝔰 𝔤𝔢𝔫𝔷

> AI-powered meme generator for the chronically online. Powered by Google Gemini & Supabase.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://memes-genz.streamlit.app/)

---

## ✨ Features

- **Classic Meme Generator** — Type or speak a situation, get an AI-generated meme caption
- **Roast My Face (Vision AI)** — Upload a photo and let Gemini roast it into a meme
- **Voice Input** — Record audio and transcribe it into the prompt
- **Meme Vault** — Session history with download & WhatsApp share
- **Multi-theme UI** — Neon Green, Cyber Blue, Vaporwave Pink, Sunset Orange
- **Auth with Credits** — Google & GitHub OAuth via Supabase; 3 free credits on signup

---

## 🚀 Deploy on Streamlit Community Cloud

### 1. Fork / Push to GitHub
Push this repo to your GitHub account.

### 2. Go to [share.streamlit.io](https://share.streamlit.io)
- Click **"New app"**
- Select your GitHub repo
- Set **Main file path** → `app.py`
- Click **"Deploy"**

### 3. Add Secrets
In the Streamlit Cloud dashboard → **Settings → Secrets**, paste:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
GEMINI_KEYS  = ["your-gemini-key-1", "your-gemini-key-2"]
```

---

## 🛠️ Local Development

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/memes-genz.git
cd memes-genz

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add secrets
# Create .streamlit/secrets.toml with:
# SUPABASE_URL = "..."
# SUPABASE_KEY = "..."
# GEMINI_KEYS  = ["..."]

# 5. Run
streamlit run app.py
```

---

## 🔑 Required API Keys

| Service | Purpose | Get it at |
|---------|---------|-----------|
| **Google Gemini** | Caption generation & Vision AI | [aistudio.google.com](https://aistudio.google.com) |
| **Supabase** | Auth (Google/GitHub OAuth) & Credits DB | [supabase.com](https://supabase.com) |

---

## 📦 Tech Stack

- [Streamlit](https://streamlit.io) — UI framework
- [Google Gemini](https://ai.google.dev) — LLM for captions and vision
- [Supabase](https://supabase.com) — Auth & database
- [Pillow](https://pillow.readthedocs.io) — Image processing
- [Imgflip API](https://imgflip.com/api) — Random meme templates
