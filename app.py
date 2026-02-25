import streamlit as st
import requests
import json
import os
import io
import textwrap
import random
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
from groq import Groq
import base64

# --- 1. PAGE CONFIG (must be first Streamlit call) ---
st.set_page_config(page_title="𝔪𝔢𝔪𝔢𝔰 𝔤𝔢𝔫𝔷", page_icon="🧙🏻‍♂", layout="wide")

# --- 2. INITIALIZE SESSION STATE ---
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Cyber Blue"
if "meme_history" not in st.session_state:
    st.session_state.meme_history = []
if "generated_caption" not in st.session_state:
    st.session_state.generated_caption = None
if "draft_text" not in st.session_state:
    st.session_state.draft_text = ""

# --- 3. DYNAMIC GEN Z THEME ENGINE ---
theme_colors = {
    "Neon Green (Default)": {"primary": "#ccff00", "secondary": "#00ffa3", "bg": "#160b24"},
    "Cyber Blue":           {"primary": "#00f0ff", "secondary": "#0057ff", "bg": "#0a0b14"},
    "Vaporwave Pink":       {"primary": "#ff00ff", "secondary": "#00ffff", "bg": "#1a0b2e"},
    "Sunset Orange":        {"primary": "#ff4d00", "secondary": "#ffcc00", "bg": "#1c0d02"},
}

colors = theme_colors[st.session_state.app_theme]
p_color, s_color, bg_color = colors["primary"], colors["secondary"], colors["bg"]

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap');

    .stApp {{
        background: radial-gradient(circle at 10% 10%, {bg_color} 0%, #050505 100%);
        color: #fafafa;
        font-family: 'Outfit', sans-serif;
    }}
    h1, h2, h3 {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, {p_color}, {s_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 15px {p_color}66;
    }}
    .stButton>button {{
        background: linear-gradient(135deg, {p_color}, {s_color});
        color: #000 !important;
        font-weight: 800;
        border-radius: 12px;
        border: none;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 15px {p_color}4D;
    }}
    .stButton>button:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 25px {p_color}99;
    }}
    section[data-testid="stSidebar"] {{
        background-color: rgba(10, 11, 20, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 5px 0 30px {p_color}33 !important;
    }}
    div[data-testid="stExpander"] {{
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }}
    div[data-testid="stExpander"]:hover {{
        border: 1px solid {p_color}80 !important;
        box-shadow: 0 0 20px {p_color}4D !important;
    }}
    .meme-card {{
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }}
    .meme-text {{
        font-size: 24px;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, {p_color}, {s_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. GROQ CLIENT SETUP ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    st.error("🚨 Missing Groq API Key! Check .streamlit/secrets.toml")
    st.stop()

# --- 5. TOP NAVIGATION ---
st.markdown("<h1 style='text-align: center;'>🧙🏻‍♂ 𝔪𝔢𝔪𝔢𝔰 𝔤𝔢𝔫𝔷</h1>", unsafe_allow_html=True)

# --- 6. SIDEBAR SETTINGS ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚙️ Workspace</h2>", unsafe_allow_html=True)
    st.markdown("---")

    with st.expander("✨ App Appearance", expanded=True):
        selected_theme = st.selectbox(
            "UI Color Theme",
            list(theme_colors.keys()),
            index=list(theme_colors.keys()).index(st.session_state.app_theme),
        )
        if selected_theme != st.session_state.app_theme:
            st.session_state.app_theme = selected_theme
            st.rerun()

    with st.expander("🎨 Graphics Preferences"):
        meme_language = st.selectbox("🌐 Meme Language", ["Tanglish", "English", "German", "Hindi"])
        meme_text_color = st.color_picker("Text Color", "#FFFFFF")

# --- 7. UTILS ---
def burn_meme_text(img: Image.Image, text: str, color: str) -> Image.Image:
    """Burn meme caption text onto the bottom of a PIL image."""
    draw = ImageDraw.Draw(img)
    img_w, img_h = img.size
    font_size = max(24, int(img_h / 12))
    try:
        # Try finding a font, default to basic if not found
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=25)
    line_height = font_size + 8
    total_text_height = line_height * len(lines)
    y_text = img_h - total_text_height - 30

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x_text = (img_w - text_w) / 2
        # Outline for readability
        for adj in range(-2, 3):
            for op in range(-2, 3):
                draw.text((x_text+adj, y_text+op), line, font=font, fill="black")
        draw.text((x_text, y_text), line, font=font, fill=color)
        y_text += line_height

    return img

def call_groq(prompt: str, image_bytes: bytes | None = None) -> str | None:
    """Calls Groq API for completion or vision."""
    try:
        if image_bytes:
            # Vision request
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                response_format={"type": "json_object"}
            )
        else:
            # Text request
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
        
        data = json.loads(response.choices[0].message.content)
        return data.get("caption")
    except Exception as e:
        st.error(f"Groq API Error: {e}")
        return None

# --- 8. MAIN UI ---
main_col1, main_col2, main_col3 = st.columns([1, 2, 1])
with main_col2:
    st.markdown("<h3 style='text-align: center;'>🎙️ Conjure Comedy</h3>", unsafe_allow_html=True)

    tab_classic, tab_vision = st.tabs(["📝 Classic Meme Generator", "📸 Roast My Face (Vision AI)"])

    # TAB 1: CLASSIC
    with tab_classic:
        with st.container(border=True):
            st.markdown("<p style='color: #888; font-size: 14px; font-weight: bold;'>1. Record situation (Optional)</p>", unsafe_allow_html=True)
            audio_value = st.audio_input("Voice Input", label_visibility="collapsed")

            if audio_value:
                if st.button("⚡ Transcribe", key="transcribe_btn", use_container_width=True):
                    with st.spinner("Decoding your voice..."):
                        try:
                            # Groq Whisper
                            transcription = client.audio.transcriptions.create(
                                file=("audio.wav", audio_value.read()),
                                model="whisper-large-v3",
                                response_format="text",
                            )
                            st.session_state.draft_text = transcription
                            st.rerun()
                        except Exception as e:
                            st.error(f"Transcription Error: {e}")

            st.markdown("<p style='color: #888; font-size: 14px; font-weight: bold; margin-top: 15px;'>2. Type or Edit</p>", unsafe_allow_html=True)
            prompt_input = st.text_area(
                "Input",
                value=st.session_state.draft_text,
                placeholder="Describe the situation...",
                height=80,
                label_visibility="collapsed",
            )
            if prompt_input != st.session_state.draft_text:
                st.session_state.draft_text = prompt_input

            st.markdown("<br>", unsafe_allow_html=True)
            generate_btn = st.button("✍️ Generate Meme Text", key="gen_text_btn", use_container_width=True)

        if generate_btn and prompt_input:
            with st.spinner("Groq is cooking..."):
                persona = "local Chennai Vadivelu style" if meme_language == "Tanglish" else "savage GenZ"
                prompt = (
                    f"You are a {persona} meme creator. "
                    f"Situation: {prompt_input}. Language: {meme_language}. "
                    "Output ONLY a JSON object with a 'caption' key containing the funny caption."
                )
                caption = call_groq(prompt)
                if caption:
                    st.session_state.generated_caption = caption
                    st.rerun()

        if st.session_state.generated_caption:
            st.markdown(
                f'<div class="meme-card"><div class="meme-text">"{st.session_state.generated_caption}"</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("🌐 Generate Visual Meme", key="burn_imgflip_btn", use_container_width=True):
                with st.spinner("Burning text to image..."):
                    try:
                        res = requests.get("https://api.imgflip.com/get_memes").json()
                        meme = random.choice(res["data"]["memes"])
                        img_res = requests.get(meme["url"])
                        img = Image.open(io.BytesIO(img_res.content)).convert("RGB")
                        final = burn_meme_text(img, st.session_state.generated_caption, meme_text_color)
                        st.image(final, use_container_width=True)
                        st.session_state.meme_history.append(
                            {"image": final, "caption": st.session_state.generated_caption}
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")

    # TAB 2: VISION
    with tab_vision:
        with st.container(border=True):
            upload_pic = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            camera_pic = st.camera_input("Take a Selfie", label_visibility="collapsed")

            user_img_source = camera_pic if camera_pic else upload_pic

            if user_img_source:
                img_bytes = user_img_source.read() # Read once
                user_pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                st.image(user_pil_img, caption="Target Locked 🎯", use_container_width=True)

                if st.button("🔥 Roast This Image", key="roast_btn", use_container_width=True):
                    with st.spinner("Scanning for emotional damage..."):
                        persona = "local Chennai Vadivelu style" if meme_language == "Tanglish" else "savage GenZ internet troll"
                        prompt = (
                            f"You are a {persona}. Analyze this image and roast it brutally but playfully. "
                            f"Create a funny, relatable meme caption based ONLY on what you see. "
                            f"Language: {meme_language}. Output ONLY a JSON object with a 'caption' key."
                        )
                        roast_caption = call_groq(prompt, image_bytes=img_bytes)
                        if roast_caption:
                            final_roast = burn_meme_text(user_pil_img.copy(), roast_caption, meme_text_color)
                            st.image(final_roast, use_container_width=True)
                            st.session_state.meme_history.append(
                                {"image": final_roast, "caption": roast_caption}
                            )
                            st.success("Roast complete!")

# --- 9. MEME VAULT ---
st.markdown("---")
col_title, col_clear = st.columns([4, 1], vertical_alignment="bottom")
with col_title:
    st.markdown("### 📜 Your Meme Vault")
with col_clear:
    if st.session_state.meme_history:
        if st.button("🗑️ Clear Vault", use_container_width=True):
            st.session_state.meme_history = []
            st.rerun()

if not st.session_state.meme_history:
    st.info("Your vault is empty! Generate memes and they'll appear here.")
else:
    history_cols = st.columns(3)
    for index, past_meme in enumerate(reversed(st.session_state.meme_history)):
        original_index = len(st.session_state.meme_history) - 1 - index
        with history_cols[index % 3]:
            with st.container(border=True):
                st.image(past_meme["image"], use_container_width=True)
                st.markdown(f"<div style='font-style: italic; font-size: 14px; margin-top: 10px;'>&quot;{past_meme['caption']}&quot;</div>", unsafe_allow_html=True)
                
                buf = io.BytesIO()
                past_meme["image"].save(buf, format="PNG")
                st.download_button(
                    label="⬇️ Download",
                    data=buf.getvalue(),
                    file_name=f"memegenz_{original_index}.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_{original_index}",
                )
                
                viral_message = f"Bro look at this meme I made! 😂\n\n\"{past_meme['caption']}\""
                encoded_message = urllib.parse.quote(viral_message)
                st.markdown(f'<a href="https://wa.me/?text={encoded_message}" target="_blank" style="display: block; text-align: center; background-color: #25D366; color: white; padding: 6px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 5px;">🟢 Share on WhatsApp</a>', unsafe_allow_html=True)
                
                if st.button("❌ Remove", key=f"del_{original_index}", use_container_width=True):
                    st.session_state.meme_history.pop(original_index)
                    st.rerun()