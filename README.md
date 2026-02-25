# 🧙🏻‍♂ Memes Genz — AI Meme Generator

Welcome to **Memes Genz**! This is a fun web application built with **Streamlit** and **Groq AI**. It helps you create hilarious memes using just your voice or uploaded photos.

---

## 🌟 What can this app do?

1.  **📝 Classic Meme Generation**: Just describe a funny situation (like "When my code finally works"), and the AI will write a perfect caption and find a matching meme template!
2.  **📸 Roast My Face**: Upload a photo or take a selfie, and the AI will "roast" you by turning that photo into a savage meme.
3.  **🎙️ Voice Control**: Don't want to type? Just use the built-in voice recorder to say your meme idea.
4.  **💾 Meme Vault**: All the memes you create are saved in your "Vault" during your session. You can download them or share them directly to WhatsApp.
5.  **🌈 Gen Z Themes**: Change the app's look with cool themes like "Cyber Blue", "Vaporwave Pink", and "Neon Green".

---

## 🚀 How to use it (For Beginners)

### 1. 🌐 Accessing the App
If the app is deployed, you can simply visit the URL (e.g., `https://memes-genz.streamlit.app`).

### 🚀 How to Host this yourself (Streamlit Cloud)
Want to put this on the internet for free? Follow these steps:

1.  **Upload to GitHub**: Create a new repository on GitHub and upload all these files (the `.gitignore` will automatically hide your private keys).
2.  **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3.  **Deploy App**: Click "New app", select your repository, and click "Deploy".
4.  **Add your Keys (CRITICAL)**: 
    - Once the app page opens, click the **"Manage app"** button in the bottom right.
    - Click the **three dots `⋮`** → **Settings** → **Secrets**.
    - Paste your keys there just like you did in the `secrets.toml` file!
    - Click **Save**, and your app is live!

### 2. ✍️ Making your first meme
-   Go to the **Classic** tab.
-   Type a situation in the box.
-   Click **"Generate Meme Text"**.
-   If you like the text, click **"Generate Visual Meme"** to see the final image!

---

## 🛠️ How to run it on your computer

If you want to run this code locally, follow these simple steps:

### Step 1: Install Python
Make sure you have [Python](https://www.python.org/) installed on your computer.

### Step 2: Download the Code
Download this folder to your computer.

### Step 3: Open your Terminal
Open Command Prompt (Windows) or Terminal (Mac). `cd` into the project folder.

### Step 4: Install the "Required" stuff
Copy and paste this command and press Enter:
```bash
pip install -r requirements.txt
```

### Step 5: Add your Secrets (API Keys)
This app needs a "Key" to talk to the AI.
1. Create a folder named `.streamlit`.
2. Inside it, create a file named `secrets.toml`.
3. Add your keys like this:
```toml
GROQ_API_KEY = "your_groq_key_here"
```

### Step 6: Start the App!
Run this command:
```bash
streamlit run app.py
```

---

## 📦 Built With
-   **Streamlit**: For the website interface.
-   **Groq AI**: For writing jokes and scanning photos (using Llama-3 models).
-   **Imgflip**: For the classic meme templates.

Developed with ❤️ for the Gen Z community.
