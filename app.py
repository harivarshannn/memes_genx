import streamlit as st
from supabase import create_client, Client, ClientOptions
import requests
import json
import os
import io
import textwrap
import random
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

# --- 1. PAGE CONFIG (must be first Streamlit call) ---
st.set_page_config(page_title="𝔪𝔢𝔪𝔢𝔰 𝔤𝔢𝔫𝔷", page_icon="🧙🏻‍♂", layout="wide")

# --- 2. INITIALIZE SESSION STATE ---
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Cyber Blue"
if "meme_history" not in st.session_state:
    st.session_state.meme_history = []
if "user" not in st.session_state:
    st.session_state.user = None
if "credits" not in st.session_state:
    st.session_state.credits = 0
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
    .auth-container, .meme-card {{
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }}
    .login-btn {{
        background: rgba(255, 255, 255, 0.05);
        color: #fff;
        padding: 10px 24px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: 800;
        border: 1px solid rgba(255,255,255,0.2);
        transition: 0.3s;
    }}
    .login-btn:hover {{
        background: linear-gradient(135deg, {p_color}, {s_color});
        color: #000;
        border: none;
        box-shadow: 0 0 20px {p_color}80;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. THE VAULT SETUP ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    ALL_GEMINI_KEYS = st.secrets["GEMINI_KEYS"]
except Exception:
    st.error("🚨 Missing API Keys! Check .streamlit/secrets.toml")
    st.stop()


class LocalStorage:
    """File-based session persistence for Supabase auth tokens."""
    def __init__(self):
        self.file_path = "session.json"

    def get_item(self, key):
        if not os.path.exists(self.file_path):
            return None
        try:
            with open(self.file_path, "r") as f:
                return json.load(f).get(key)
        except Exception:
            return None

    def set_item(self, key, value):
        data = {}
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
            except Exception:
                pass
        data[key] = value
        with open(self.file_path, "w") as f:
            json.dump(data, f)

    def remove_item(self, key):
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
            if key in data:
                del data[key]
                with open(self.file_path, "w") as f:
                    json.dump(data, f)
        except Exception:
            pass


supabase: Client = create_client(
    SUPABASE_URL, SUPABASE_KEY, options=ClientOptions(storage=LocalStorage())
)

# --- 5. OAUTH CALLBACK HANDLER ---
if "code" in st.query_params:
    try:
        res = supabase.auth.exchange_code_for_session({"auth_code": st.query_params["code"]})
        user_email = res.user.email
        user_data = supabase.table("users").select("credits").eq("email", user_email).execute()
        if not user_data.data:
            supabase.table("users").insert({"email": user_email, "credits": 3}).execute()
            st.session_state.credits = 3
        else:
            st.session_state.credits = user_data.data[0]["credits"]
        st.session_state.user = user_email
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")
        st.query_params.clear()

# --- 6. TOP NAVIGATION ---
col_logo, col_auth = st.columns([3, 1])
with col_logo:
    st.markdown("<h1>🧙🏻‍♂ 𝔪𝔢𝔪𝔢𝔰 𝔤𝔢𝔫𝔷</h1>", unsafe_allow_html=True)

with col_auth:
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    if st.session_state.user is None:
        st.markdown(
            "<p style='font-size: 12px; text-align: center; margin-bottom: 5px;'>Sign in to generate</p>",
            unsafe_allow_html=True,
        )
        btn_col1, btn_col2 = st.columns(2)
        try:
            res_g = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {"redirect_to": "https://memes-genz.streamlit.app/"},
            })
            with btn_col1:
                st.markdown(
                    f'<a href="{res_g.url}" class="login-btn" target="_self" '
                    f'style="display:block; text-align:center; padding: 8px; font-size: 14px;">Google</a>',
                    unsafe_allow_html=True,
                )
            res_gh = supabase.auth.sign_in_with_oauth({
                "provider": "github",
                "options": {"redirect_to": "https://memes-genz.streamlit.app/"},
            })
            with btn_col2:
                st.markdown(
                    f'<a href="{res_gh.url}" class="login-btn" target="_self" '
                    f'style="display:block; text-align:center; padding: 8px; font-size: 14px; '
                    f'background: #333; border-color: #555;">GitHub</a>',
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.error(f"Auth Error: {e}")
    else:
        st.markdown(f"🪙 **{st.session_state.credits}** Credits", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            supabase.auth.sign_out()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 7. SIDEBAR SETTINGS ---
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

    with st.expander("👤 Account & Profile"):
        display_name = "Not logged in"
        if st.session_state.user:
            try:
                user_info = supabase.auth.get_user()
                display_name = user_info.user.user_metadata.get(
                    "full_name", st.session_state.user.split("@")[0]
                )
            except Exception:
                display_name = st.session_state.user.split("@")[0]
        st.text_input("Full Name", value=display_name, disabled=True)
        st.text_input(
            "Email",
            value=st.session_state.user if st.session_state.user else "Not logged in",
            disabled=True,
        )

    with st.expander("💳 Billing & Usage"):
        if st.session_state.user:
            st.metric(label="Available Credits", value=st.session_state.credits)
            st.progress(min(st.session_state.credits / 10, 1.0))
            st.caption("1 Credit = 1 Meme Generated")
        else:
            st.info("Log in to view your credit balance.")

    with st.expander("🎨 Graphics Preferences"):
        meme_language = st.selectbox("🌐 Meme Language", ["Tanglish", "English", "German", "Hindi"])
        meme_text_color = st.color_picker("Text Color", "#FFFFFF")

    with st.expander("🔌 Integrations"):
        st.button("🔗 Connect GitHub", use_container_width=True)
        st.button("🐦 Connect X (Twitter)", use_container_width=True)


# --- 8. IMAGE ENGINE ---
def burn_meme_text(img: Image.Image, text: str, color: str) -> Image.Image:
    """Burn meme caption text onto the bottom of a PIL image with a black stroke."""
    draw = ImageDraw.Draw(img)
    img_w, img_h = img.size
    font_size = max(24, int(img_h / 12))
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=25)
    line_height = font_size + 8
    total_text_height = line_height * len(lines)
    # Position text so it always lands near the bottom, regardless of image size
    y_text = img_h - total_text_height - 20

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x_text = (img_w - text_w) / 2
        draw.text((x_text, y_text), line, font=font, fill=color, stroke_width=3, stroke_fill="black")
        y_text += line_height

    return img


# --- 9. GEMINI API HELPER ---
def call_gemini(prompt: str, image: Image.Image | None = None) -> str | None:
    """
    Try each Gemini key and a set of models in order.
    Returns the 'caption' string from the JSON response, or None on failure.
    """
    models_text   = ["gemini-1.5-flash-8b", "gemini-1.5-flash", "gemini-2.0-flash-exp"]
    models_vision = ["gemini-1.5-flash"]

    for key in ALL_GEMINI_KEYS:
        genai.configure(api_key=key)
        model_list = models_vision if image else models_text
        for m_name in model_list:
            try:
                model = genai.GenerativeModel(m_name)
                parts = [prompt, image] if image else [prompt]
                response = model.generate_content(
                    parts,
                    generation_config={"response_mime_type": "application/json"},
                )
                data = json.loads(response.text)
                return data.get("caption")
            except Exception:
                continue
    return None


# --- 10. MAIN UI ---
main_col1, main_col2, main_col3 = st.columns([1, 2, 1])
with main_col2:
    st.markdown("<h3 style='text-align: center;'>🎙️ Conjure Comedy</h3>", unsafe_allow_html=True)

    tab_classic, tab_vision = st.tabs(["📝 Classic Meme Generator", "📸 Roast My Face (Vision AI)"])

    # --------------------------------------------------
    # TAB 1: CLASSIC TEXT / AUDIO → IMGFLIP
    # --------------------------------------------------
    with tab_classic:
        with st.container(border=True):
            st.markdown(
                "<p style='color: #888; font-size: 14px; font-weight: bold; margin-bottom: 0px;'>"
                "1. Record situation (Optional)</p>",
                unsafe_allow_html=True,
            )
            audio_value = st.audio_input("Voice Input", label_visibility="collapsed")

            if audio_value:
                if st.button("⚡ Quick Transcribe to Edit", key="transcribe_btn", use_container_width=True):
                    with st.spinner("Decoding your voice..."):
                        try:
                            genai.configure(api_key=ALL_GEMINI_KEYS[0])
                            model = genai.GenerativeModel("gemini-1.5-flash-8b")
                            audio_data = {"mime_type": "audio/wav", "data": audio_value.read()}
                            transcription = model.generate_content(
                                ["Transcribe exactly what is spoken. No extra text.", audio_data]
                            )
                            st.session_state.draft_text = transcription.text
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to transcribe: {e}")

            st.markdown(
                "<p style='color: #888; font-size: 14px; font-weight: bold; margin-top: 15px; margin-bottom: 0px;'>"
                "2. Type or Edit</p>",
                unsafe_allow_html=True,
            )
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
            with st.spinner("AI is thinking..."):
                persona = (
                    "local Chennai Vadivelu style" if meme_language == "Tanglish" else "savage GenZ"
                )
                gemini_prompt = (
                    f"You are a {persona} meme creator. "
                    f"Situation: {prompt_input}. Language: {meme_language}. "
                    "Output ONLY a JSON object with a 'caption' key."
                )
                caption = call_gemini(gemini_prompt)
                if caption:
                    st.session_state.generated_caption = caption
                    st.rerun()
                else:
                    st.error("🚨 All API keys exhausted. Try again later.")

        if st.session_state.generated_caption:
            st.markdown(
                f'<div class="meme-card"><div class="meme-text">"{st.session_state.generated_caption}"</div></div>',
                unsafe_allow_html=True,
            )
            if st.session_state.user and st.session_state.credits > 0:
                if st.button("🌐 Generate Visual Meme", key="burn_imgflip_btn", use_container_width=True):
                    with st.spinner("Burning text to image..."):
                        try:
                            res = requests.get("https://api.imgflip.com/get_memes").json()
                            meme = random.choice(res["data"]["memes"])
                            img = Image.open(
                                io.BytesIO(requests.get(meme["url"]).content)
                            ).convert("RGB")
                            final = burn_meme_text(img, st.session_state.generated_caption, meme_text_color)
                            st.image(final, use_container_width=True)
                            st.session_state.credits -= 1
                            supabase.table("users").update(
                                {"credits": st.session_state.credits}
                            ).eq("email", st.session_state.user).execute()
                            st.session_state.meme_history.append(
                                {"image": final, "caption": st.session_state.generated_caption}
                            )
                        except Exception as e:
                            st.error(f"Error: {e}")
            elif not st.session_state.user:
                st.warning("Sign in to generate images!")

    # --------------------------------------------------
    # TAB 2: VISION AI (ROAST MY FACE)
    # --------------------------------------------------
    with tab_vision:
        with st.container(border=True):
            st.markdown(
                "<p style='color: #888; font-size: 14px; font-weight: bold;'>"
                "Upload a photo or snap a selfie for the AI to roast.</p>",
                unsafe_allow_html=True,
            )
            upload_pic = st.file_uploader(
                "Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
            )
            camera_pic = st.camera_input("Or take a Selfie", label_visibility="collapsed")

            user_img_source = camera_pic if camera_pic else upload_pic

            if user_img_source:
                user_pil_img = Image.open(user_img_source).convert("RGB")
                st.image(user_pil_img, caption="Target Locked 🎯", use_container_width=True)

                if st.button("🔥 Roast This Image", key="roast_btn", use_container_width=True):
                    if not st.session_state.user or st.session_state.credits <= 0:
                        st.warning("Sign in and ensure you have credits to use the Vision AI!")
                    else:
                        with st.spinner("Scanning pixels for maximum emotional damage..."):
                            persona = (
                                "local Chennai Vadivelu style"
                                if meme_language == "Tanglish"
                                else "savage GenZ internet troll"
                            )
                            vision_prompt = (
                                f"You are a {persona}. Analyze this image and roast it brutally but playfully. "
                                f"Create a funny, relatable meme caption based ONLY on what you see. "
                                f"Language: {meme_language}. Output ONLY a JSON object with a 'caption' key."
                            )
                            roast_caption = call_gemini(vision_prompt, image=user_pil_img)
                            if roast_caption:
                                final_roast = burn_meme_text(
                                    user_pil_img.copy(), roast_caption, meme_text_color
                                )
                                st.image(final_roast, use_container_width=True)
                                st.session_state.credits -= 1
                                supabase.table("users").update(
                                    {"credits": st.session_state.credits}
                                ).eq("email", st.session_state.user).execute()
                                st.session_state.meme_history.append(
                                    {"image": final_roast, "caption": roast_caption}
                                )
                                st.success("Roast generated and saved to your vault!")
                            else:
                                st.error("🚨 API Limits exhausted.")

# --- 11. MEME HISTORY VAULT ---
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
    st.info("Your vault is empty! Generate some memes above and they will safely store here during your session.")
else:
    history_cols = st.columns(3)
    for index, past_meme in enumerate(reversed(st.session_state.meme_history)):
        original_index = len(st.session_state.meme_history) - 1 - index
        with history_cols[index % 3]:
            with st.container(border=True):
                st.image(past_meme["image"], use_container_width=True)
                st.markdown(
                    f"<div style='background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; "
                    f"margin-bottom: 10px; font-style: italic; font-size: 14px;'>"
                    f"&quot;{past_meme['caption']}&quot;</div>",
                    unsafe_allow_html=True,
                )
                col_dl, col_wa = st.columns(2)
                with col_dl:
                    buf = io.BytesIO()
                    past_meme["image"].save(buf, format="PNG")
                    st.download_button(
                        label="⬇️ Save",
                        data=buf.getvalue(),
                        file_name=f"memegenz_{original_index}.png",
                        mime="image/png",
                        use_container_width=True,
                        key=f"dl_{original_index}",
                    )
                with col_wa:
                    viral_message = (
                        f"Bro look at this meme I just made using AI! 😂\n\n"
                        f"\"{past_meme['caption']}\"\n\n"
                        f"Make yours at: https://memes-genz.streamlit.app/"
                    )
                    encoded_message = urllib.parse.quote(viral_message)
                    whatsapp_url = f"https://wa.me/?text={encoded_message}"
                    st.markdown(
                        f'<a href="{whatsapp_url}" target="_blank" style="display: block; text-align: center; '
                        f'background-color: #25D366; color: white; padding: 6px; border-radius: 8px; '
                        f'text-decoration: none; font-weight: bold; font-size: 15px; '
                        f'border: 1px solid #1da851; transition: 0.2s;">🟢 Share</a>',
                        unsafe_allow_html=True,
                    )
                if st.button("❌ Remove", key=f"del_{original_index}", use_container_width=True):
                    st.session_state.meme_history.pop(original_index)
                    st.rerun()