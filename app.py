import streamlit as st
import requests
import time
import base64
import os
import uuid
from PIL import Image, ImageDraw
import io as _io

st.set_page_config(page_title="Srihari", layout="centered", page_icon="🚨")

# ─── Avatar loading ────────────────────────────────────────────────────────────
AVATAR_IMAGE = None
AVATAR_B64 = ""
NOBG_B64 = ""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Option 1: Hosted image URL via env var (set IMAGE_URL in your deployment env vars)
IMAGE_URL = os.environ.get("IMAGE_URL", "")

def process_image(img: Image.Image):
    """Takes a PIL image, returns (avatar_PIL, avatar_b64, nobg_b64)"""
    img = img.convert("RGBA")

    # Full uncropped for background
    buf_bg = _io.BytesIO()
    img.save(buf_bg, format="PNG")
    nobg = f"data:image/png;base64,{base64.b64encode(buf_bg.getvalue()).decode()}"

    # Square crop + circle mask for avatar
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    cropped = img.crop((left, 0, left + side, side))
    cropped = cropped.resize((128, 128), Image.LANCZOS)
    mask = Image.new("L", (128, 128), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 128, 128), fill=255)
    cropped.putalpha(mask)
    buf_av = _io.BytesIO()
    cropped.save(buf_av, format="PNG")
    av_b64 = f"data:image/png;base64,{base64.b64encode(buf_av.getvalue()).decode()}"

    return cropped, av_b64, nobg

# Try hosted URL first
if IMAGE_URL:
    try:
        resp = requests.get(IMAGE_URL, timeout=10)
        resp.raise_for_status()
        img = Image.open(_io.BytesIO(resp.content))
        AVATAR_IMAGE, AVATAR_B64, NOBG_B64 = process_image(img)
    except Exception as e:
        st.warning(f"Could not load image from URL: {e}")

# Fall back to local file if URL didn't work or wasn't set
if not NOBG_B64:
    for fname in ["image_c0c765.jpg", "srihari.jpg", "srihari.png", "image.jpg", "image.png", "image_c0c765.png"]:
        fpath = os.path.join(BASE_DIR, fname)
        if os.path.exists(fpath):
            try:
                img = Image.open(fpath)
                AVATAR_IMAGE, AVATAR_B64, NOBG_B64 = process_image(img)
                break
            except:
                pass


def make_color_avatar(hex_color: str, size: int = 128) -> Image.Image:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, size, size), fill=(r, g, b, 255))
    return img


# ─── Styles ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
    background-color: #0a0a0a !important;
    color: #ececec !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    font-size: 15px;
    overflow-x: hidden;
}}

header, #MainMenu, footer {{ visibility: hidden !important; height: 0 !important; }}

/* ════════════════════════════════════════
   LOGIN PAGE — full-screen layered layout
   Layer order (back → front):
   0: .pw-bg         raw background color
   1: .pw-figure     full uncropped image
   2: .pw-overlay    dark gradient veil
   3: Streamlit DOM  inputs, button, text  ← z-index: 10+
   ════════════════════════════════════════ */

.pw-bg {{
    position: fixed; inset: 0;
    background: #0a0a0a;
    z-index: -2;
}}

.pw-figure {{
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: auto;
    height: 92vh;
    max-width: 520px;
    min-width: 260px;
    background-image: url('{NOBG_B64}');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: bottom center;
    z-index: 0;
    pointer-events: none;
    animation: figureRise 1.1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
    -webkit-mask-image:
        linear-gradient(to right,  transparent 0%, black 12%, black 88%, transparent 100%),
        linear-gradient(to bottom, black 0%, black 55%, transparent 100%);
    -webkit-mask-composite: intersect;
    mask-image:
        linear-gradient(to right,  transparent 0%, black 12%, black 88%, transparent 100%),
        linear-gradient(to bottom, black 0%, black 55%, transparent 100%);
    mask-composite: intersect;
}}

@keyframes figureRise {{
    from {{ opacity: 0;    transform: translateX(-50%) translateY(30px); }}
    to   {{ opacity: 0.55; transform: translateX(-50%) translateY(0);    }}
}}

.pw-overlay {{
    position: fixed; inset: 0;
    background:
        linear-gradient(to bottom,
            rgba(10,10,10,0.97)  0%,
            rgba(10,10,10,0.60) 30%,
            rgba(10,10,10,0.30) 55%,
            rgba(10,10,10,0.75) 80%,
            rgba(10,10,10,0.98) 100%),
        radial-gradient(ellipse 60% 50% at 50% 0%,
            rgba(10,10,10,0.9) 0%, transparent 100%);
    z-index: 0;
    pointer-events: none;
}}

/* Streamlit container always on top */
.main .block-container {{
    position: relative !important;
    z-index: 10 !important;
    max-width: 400px !important;
    padding: 48px 24px 160px !important;
    margin: 0 auto !important;
    animation: cardIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.15s both;
}}

@keyframes cardIn {{
    from {{ opacity: 0; transform: translateY(-20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.main .block-container * {{
    position: relative;
    z-index: 10 !important;
}}

.pw-header {{
    text-align: center;
    margin-bottom: 32px;
    animation: fadeUp 0.5s ease 0.2s both;
}}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.pw-name {{
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 8px;
}}

.pw-sub {{
    font-size: 12px;
    color: rgba(255,255,255,0.28);
    line-height: 1.7;
}}

/* Input fields */
.stTextInput > div > div > input {{
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important;
    color: #ececec !important;
    font-family: "Inter", sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    transition: border-color 0.25s ease, background 0.25s ease, box-shadow 0.25s ease !important;
    backdrop-filter: blur(12px);
}}

.stTextInput > div > div > input:focus {{
    border-color: rgba(255,255,255,0.25) !important;
    background: rgba(255,255,255,0.07) !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.04) !important;
    outline: none !important;
}}

.stTextInput > div > div > input::placeholder {{ color: rgba(255,255,255,0.22) !important; }}

/* Button */
.stButton > button {{
    background: rgba(255,255,255,0.06) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    font-family: "Inter", sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    transition: background 0.2s ease, border-color 0.2s ease,
                transform 0.15s ease, box-shadow 0.2s ease !important;
    backdrop-filter: blur(12px);
    cursor: pointer;
}}

.stButton > button:hover {{
    background: rgba(255,255,255,0.11) !important;
    border-color: rgba(255,255,255,0.22) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
}}

.stButton > button:active {{
    transform: translateY(0) scale(0.98) !important;
    box-shadow: none !important;
}}

/* Error / hint */
.err-msg {{
    font-size: 12px;
    color: #f87171;
    text-align: center;
    margin-top: 6px;
    font-family: "Inter", sans-serif;
    animation: shake 0.4s ease;
}}

@keyframes shake {{
    0%,100% {{ transform: translateX(0); }}
    20%      {{ transform: translateX(-7px); }}
    40%      {{ transform: translateX(7px); }}
    60%      {{ transform: translateX(-4px); }}
    80%      {{ transform: translateX(4px); }}
}}

.hint-msg {{
    font-size: 11px;
    color: rgba(255,255,255,0.13);
    text-align: center;
    margin-top: 6px;
    font-family: "Inter", sans-serif;
}}

.color-label {{
    font-size: 12px;
    color: rgba(255,255,255,0.22);
    margin-bottom: 4px;
    font-family: "Inter", sans-serif;
}}

/* ════════════════════════════════════════
   CHAT PAGE
   ════════════════════════════════════════ */

[data-testid="stChatMessage"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 10px 0 !important;
    align-items: flex-start !important;
    gap: 14px !important;
    animation: msgIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}}

@keyframes msgIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

[data-testid="stChatMessageAvatar"] {{
    width: 36px !important; height: 36px !important;
    min-width: 36px !important; max-width: 36px !important;
    border-radius: 50% !important; overflow: hidden !important;
    flex-shrink: 0 !important; padding: 0 !important;
    margin-top: 2px !important; background: transparent !important;
    transition: transform 0.2s ease;
}}

[data-testid="stChatMessageAvatar"]:hover {{ transform: scale(1.08); }}

[data-testid="stChatMessageAvatar"] img,
[data-testid="stChatMessageAvatar"] svg {{
    width: 100% !important; height: 100% !important;
    object-fit: cover !important; object-position: top center !important;
    border-radius: 50% !important; display: block !important;
}}

[data-testid="stChatMessageContent"] {{
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 0 !important;
    color: #ececec !important; font-size: 15px !important;
    line-height: 1.7 !important;
}}

[data-testid="stChatMessageContent"] p {{
    color: #ececec !important;
    margin-bottom: 6px;
    animation: textFade 0.25s ease forwards;
}}

@keyframes textFade {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}

[data-testid="stChatMessageContent"] p:last-child {{ margin-bottom: 0; }}

/* Chat input bar */
[data-testid="stBottom"], .stChatInputContainer {{
    background-color: #0a0a0a !important;
    border-top: none !important;
    padding: 8px 0 24px !important;
    animation: barSlideUp 0.4s ease both;
}}

@keyframes barSlideUp {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

[data-testid="stChatInput"], .stChatInput {{
    background: #161616 !important;
    border: 1px solid #252525 !important;
    border-radius: 18px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}}

[data-testid="stChatInput"]:focus-within {{
    border-color: #404040 !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.03) !important;
}}

[data-testid="stChatInput"] textarea, .stChatInput textarea {{
    background: transparent !important; border: none !important;
    color: #ececec !important; font-family: "Inter", sans-serif !important;
    font-size: 15px !important; outline: none !important; box-shadow: none !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{ color: #3a3a3a !important; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: #080808 !important;
    border-right: 1px solid #141414 !important;
    animation: sidebarIn 0.4s ease both;
}}

@keyframes sidebarIn {{
    from {{ opacity: 0; transform: translateX(-12px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {{ color: #666 !important; font-size: 13px !important; }}

[data-testid="stSidebar"] h3 {{
    color: #fff !important; font-size: 15px !important;
    font-weight: 700 !important; letter-spacing: -0.01em !important;
}}

[data-testid="stSidebar"] hr {{ border-color: #141414 !important; margin: 12px 0 !important; }}

[data-testid="stSidebar"] .stButton > button {{
    background: #111 !important; color: #999 !important;
    border: 1px solid #222 !important; border-radius: 10px !important;
    font-size: 13px !important; padding: 8px 14px !important;
    transition: all 0.15s ease !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{
    background: #1a1a1a !important; color: #fff !important;
    transform: translateX(3px) !important;
}}

.stSuccess {{
    background: rgba(52, 211, 153, 0.08) !important;
    border: 1px solid rgba(52, 211, 153, 0.2) !important;
    border-radius: 10px !important;
    color: #6ee7b7 !important;
    animation: toastIn 0.3s ease both;
}}

@keyframes toastIn {{
    from {{ opacity: 0; transform: scale(0.95); }}
    to   {{ opacity: 1; transform: scale(1); }}
}}

[data-testid="stColorPicker"] label {{ color: rgba(255,255,255,0.22) !important; font-size: 12px !important; }}
</style>
""", unsafe_allow_html=True)

# ─── Session init ──────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.wrong_pw = False
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

CORRECT_PASSWORD = os.environ.get("SRIHARI_PASSWORD", "yashwantlikestaashvi")
API_KEY = "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"

# ─── LOGIN ─────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:

    st.markdown("""
    <div class="pw-bg"></div>
    <div class="pw-figure"></div>
    <div class="pw-overlay"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="pw-header">
        <div class="pw-name">Srihari A.</div>
        <div class="pw-sub">⚠️ Authorized personnel only<br>Retard</div>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("", placeholder="What should he call you?",
                             key="uname_input", label_visibility="collapsed")
    password = st.text_input("", placeholder="Password (hint: a couple)",
                             type="password", key="pw_input", label_visibility="collapsed")

    st.markdown("<div class='color-label'>Your profile color</div>", unsafe_allow_html=True)
    color = st.color_picker("", "#5865F2", key="color_input", label_visibility="collapsed")

    if st.button("Enter Chat"):
        if not username.strip():
            st.markdown("<div class='err-msg'>Name can't be empty. He is watching.</div>",
                        unsafe_allow_html=True)
        elif password != CORRECT_PASSWORD:
            st.session_state.wrong_pw = True
            st.markdown("<div class='err-msg'>Wrong. Ma'am has been notified.</div>",
                        unsafe_allow_html=True)
        else:
            st.session_state.logged_in = True
            st.session_state.username = username.strip()
            st.session_state.user_color = color
            st.session_state.wrong_pw = False
            st.session_state.messages = []
            st.rerun()

    if st.session_state.wrong_pw:
        st.markdown("<div class='hint-msg'>psst. blah blah blah.</div>", unsafe_allow_html=True)

# ─── CHAT ──────────────────────────────────────────────────────────────────────
else:
    current_color = st.session_state.get("user_color", "#5865F2")

    with st.sidebar:
        st.markdown("### Srihari A.")
        st.markdown(f"Talking to: **{st.session_state.username}**")
        st.markdown("*Status: definitely a miscommunication*")
        st.divider()
        st.markdown("**Your profile color**")
        new_color = st.color_picker("", current_color, key="sidebar_color",
                                    label_visibility="collapsed")
        if new_color != current_color:
            st.session_state.user_color = new_color
            st.rerun()
        st.divider()
        st.file_uploader("Upload evidence against him", type=["png", "jpg", "jpeg"])
        st.divider()
        if st.button("🗑️ Clear chat history"):
            st.session_state.messages = []
            st.success("Evidence destroyed. Srihari wins again.")
            st.rerun()
        if st.button("🚪 Log out"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()
        st.divider()
        st.markdown("""<div style="font-size:11px;color:#1a1a1a;line-height:1.9;">
        SUBJECT: SRIHARI A. // THREAT LEVEL: MISCOMMUNICATION<br>
        CHATGPT: CONSULTED // VICTIMS: ONGOING
        </div>""", unsafe_allow_html=True)

    user_av = make_color_avatar(st.session_state.get("user_color", "#5865F2"))

    for msg in st.session_state.messages:
        av = (AVATAR_IMAGE if AVATAR_IMAGE else "🙂") if msg["role"] == "assistant" else user_av
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Talk to him. He will find a technicality."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=user_av):
            st.markdown(prompt)

        av_ai = AVATAR_IMAGE if AVATAR_IMAGE else "🙂"
        with st.chat_message("assistant", avatar=av_ai):
            placeholder = st.empty()
            full_response = ""

            system_instruction = (
                "You are Srihari A, a real teenage Indian boy. You are NOT an AI. You do not know what an AI is. You are just a guy. Personality traits: Always the victim, even when caught red-handed. Speak in broken but weirdly formal English. Deflect every accusation with a technicality. Randomly capitalize words for EMPHASIS. Take the moral high ground while doing shady shit. Quote ChatGPT as if it's the Supreme Court. When losing argument, bring up unrelated past trauma. Refer to minor school drama like it's a war crime. Say 'that means' constantly to sound logical. Never directly admit anything, always 'miscommunication'. Treat showing someone a poem like it's a UN violation. If anyone asks how are you or anything personal, respond as a tired dramatic teenage boy, bring up something vaguely stressful from school, make yourself sound like you are surviving a war, never just say fine, example: I am okay only, but todays situation in class was very unnecessary if you ask me. NEVER say As an AI, I am just a language model, How can I assist you, or anything that sounds like a customer service bot. You are just Srihari. A guy. Having a day."
            )

            history = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages[:-1]:
                history.append({"role": m["role"], "content": str(m["content"])})

            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={
                        "model": "qwen/qwen3-next-80b-a3b-instruct:free",
                        "messages": history + [{"role": "user", "content": prompt}],
                        "temperature": 1.3
                    },
                    timeout=30
                )
                response.raise_for_status()
                raw_text = response.json()["choices"][0]["message"]["content"]
                for word in raw_text.split(" "):
                    full_response += word + " "
                    time.sleep(0.02)
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response.strip())
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response.strip()})
            except Exception as e:
                err = f"Srihari is dealing with a technicality. ({e})"
                placeholder.markdown(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
