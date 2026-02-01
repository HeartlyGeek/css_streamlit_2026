# app.py
import os
import base64
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit.components.v1 as components

from game import get_game_html, GAME_HEIGHT


# ================= Helpers (secrets/env) =================
SA_TZ = ZoneInfo("Africa/Johannesburg")


def _get_from_secrets_path(path: str):
    """
    Supports:
      - flat keys: "EMAILJS_SERVICE_ID"
      - nested keys: "emailjs.service_id"
    """
    try:
        cur = st.secrets
    except Exception:
        return None

    parts = path.split(".")
    for p in parts:
        try:
            cur = cur[p]
        except Exception:
            return None
    return cur


def get_secret(*paths: str, default: str = "") -> str:
    """
    Try multiple key paths in this order:
      1) st.secrets (flat or nested via dot paths)
      2) environment variables (only for flat keys)
    """
    for p in paths:
        v = _get_from_secrets_path(p)
        if v is not None and str(v).strip() != "":
            return str(v).strip()

    # env fallback: only for keys that look like flat env names
    for p in paths:
        if "." not in p:
            v = os.environ.get(p, "")
            if v.strip():
                return v.strip()

    return default


def get_emailjs_config():
    """
    Supports either:
      EMAILJS_SERVICE_ID / EMAILJS_TEMPLATE_ID / EMAILJS_PUBLIC_KEY / EMAILJS_PRIVATE_KEY
    or:
      [emailjs] service_id / template_id / public_key / private_key
    """
    service_id = get_secret(
        "EMAILJS_SERVICE_ID",
        "emailjs.service_id",
        default="",
    )
    template_id = get_secret(
        "EMAILJS_TEMPLATE_ID",
        "emailjs.template_id",
        default="",
    )
    public_key = get_secret(
        "EMAILJS_PUBLIC_KEY",
        "emailjs.public_key",
        default="",
    )
    private_key = get_secret(
        "EMAILJS_PRIVATE_KEY",
        "EMAILJS_ACCESS_TOKEN",
        "emailjs.private_key",
        "emailjs.access_token",
        default="",
    )

    return {
        "service_id": service_id,
        "template_id": template_id,
        "public_key": public_key,
        "private_key": private_key,
    }


def send_email_via_emailjs(from_name: str, reply_to: str, subject: str, message: str):
    """
    Sends using EmailJS REST API.
    Required:
      service_id, template_id, public_key(user_id)
    Optional:
      private_key(accessToken)
    """
    cfg = get_emailjs_config()
    service_id = cfg["service_id"]
    template_id = cfg["template_id"]
    public_key = cfg["public_key"]
    private_key = cfg["private_key"]

    if not (service_id and template_id and public_key):
        return (
            False,
            "EmailJS not configured. Ensure .streamlit/secrets.toml exists and includes "
            "EMAILJS_SERVICE_ID / EMAILJS_TEMPLATE_ID / EMAILJS_PUBLIC_KEY (or [emailjs] section).",
        )

    url = "https://api.emailjs.com/api/v1.0/email/send"

    # matches your template variables: {{from_name}}, {{reply_to}}, {{subject}}, {{date}}, {{message}}
    now_str = datetime.now(SA_TZ).strftime("%Y-%m-%d %H:%M %Z")

    payload = {
        "service_id": service_id,
        "template_id": template_id,
        "user_id": public_key,  # EmailJS calls this "Public Key"
        "template_params": {
            "from_name": from_name,
            "reply_to": reply_to,
            "subject": subject,
            "date": now_str,
            "message": message,
        },
    }

    # Optional private key support (EmailJS calls it accessToken)
    if private_key:
        payload["accessToken"] = private_key

    try:
        r = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=20,
        )
        if r.status_code in (200, 201):
            return True, "Sent ✅"

        # Show useful error without dumping secrets
        txt = (r.text or "").strip()
        if len(txt) > 400:
            txt = txt[:400] + "..."
        return False, f"EmailJS error {r.status_code}: {txt}"

    except Exception as e:
        return False, f"Failed to send: {e}"


# ================= 1. PAGE CONFIGURATION =================
st.set_page_config(
    page_title="Drug Design Lab",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ================= 2. STATE MANAGEMENT =================
if "page" not in st.session_state:
    st.session_state.page = "Researcher Profile"

# keep Lab tab stable (prevents "Visualize" jumping back to "Data")
if "lab_tab" not in st.session_state:
    st.session_state.lab_tab = "Data"

# nav selection mirrors the page
if "nav_selection" not in st.session_state:
    st.session_state.nav_selection = st.session_state.page

# flag to force-close menu after a nav click
if "close_nav_js" not in st.session_state:
    st.session_state.close_nav_js = False

pages = {
    "Researcher Profile": "👩‍🔬",
    "AI Projects": "🤖",
    "Lab Data Explorer": "🧪",
    "Publications": "🌐",
    "Contact": "📩",
    "Antibiotic Fighter Game": "🎮",
}


def page_label(name: str) -> str:
    return f"{pages.get(name,'')}  {name}"


# ================= Popover compatibility (NO key) =================
def popover_compat(label="e", use_container_width=False):
    """
    Some Streamlit versions don't support popover at all (or don't support params).
    This returns either a popover or a graceful fallback expander.
    """
    try:
        return st.popover(label, use_container_width=use_container_width)
    except TypeError:
        try:
            return st.popover(label)
        except Exception:
            return st.expander("Navigate", expanded=False)


# ================= Menu icon (BLUE) =================
MENU_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
  <path d="M5 17H19" stroke="#00e5ff" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M5 12H19" stroke="#00e5ff" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M5 7H19"  stroke="#00e5ff" stroke-width="2.4" stroke-linecap="round"/>
</svg>
""".strip()
menu_icon_base64 = "data:image/svg+xml;base64," + base64.b64encode(MENU_SVG.encode("utf-8")).decode("utf-8")

# ================= 3. CSS =================
st.markdown(
    f"""
<style>
/* Hide Streamlit chrome */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
div[data-testid="stDecoration"] {{ display: none !important; }}
div[data-testid="stToolbar"] {{ display: none !important; }}
div[data-testid="stStatusWidget"] {{ display: none !important; }}
a[data-testid="stHeaderLink"] {{ display: none !important; }}
.stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a {{ display:none !important; }}

/* kill “Press Enter to submit form” helper */
div[data-testid="InputInstructions"] {{ display:none !important; }}

/* hard kill browser focus outlines + tap highlight */
*:focus, *:focus-visible {{ outline: none !important; }}
* {{ -webkit-tap-highlight-color: transparent !important; }}

/* Emoji render */
html, body, [data-testid="stAppViewContainer"], * {{
  font-family:
    system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial,
    "Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji" !important;
  font-variant-emoji: emoji;
}}

/* -------- theme vars -------- */
:root {{
  --bg: #070A13;
  --panel: rgba(17, 24, 39, 0.72);
  --panel2: rgba(10, 12, 22, 0.88);

  --text: #e5e7eb;
  --muted: #a7b0c3;

  --pink: #ff2bd6;
  --pink2:#ec4899;
  --cyan: #00e5ff;
  --vio:  #8b5cf6;

  --shadow: 0 14px 42px rgba(0,0,0,0.40);
  --shadow2: 0 20px 70px rgba(0,0,0,0.65);
  --radius: 18px;

  --grad: linear-gradient(90deg, var(--cyan), var(--pink2));
  --gradBorder: linear-gradient(135deg,
      rgba(255,43,214,0.90),
      rgba(0,229,255,0.62),
      rgba(139,92,246,0.48)
  );
}}

html, body, [data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(1200px 800px at 18% 10%, rgba(0,229,255,0.18), transparent 55%),
    radial-gradient(900px 600px at 82% 12%, rgba(255,43,214,0.16), transparent 55%),
    radial-gradient(700px 500px at 50% 92%, rgba(139,92,246,0.10), transparent 55%),
    var(--bg) !important;
  color: var(--text);
}}

.block-container {{
  padding-top: 0.35rem !important;
  padding-bottom: 2.0rem !important;
  max-width: 1100px !important;
}}

/* ===== Header (title + typing) ===== */
.headerWrap {{
  position: relative;
}}

.brand {{
  font-weight: 950;
  letter-spacing: -0.02em;
  font-size: clamp(32px, 4.2vw, 40px);
  line-height: 1.3;
  padding-bottom: 0.1em;
  display: inline-flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}}
.brand span.title {{
  background: var(--grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.subtitle {{
  margin-top: 6px;
  color: var(--muted);
  font-size: 16 px;
}}

/* ===== Typing animation next to title ===== */
.typeWrap {{
  display: inline-flex;
  align-items: baseline;
  flex-wrap: nowrap;
  gap: 3px;
  font-size: 14px;
  font-weight: 900;
  color: rgba(229,231,235,0.85);
  text-shadow: 0 8px 20px rgba(0,0,0,0.35);
  white-space: nowrap;
}}
.typeText {{
  position: relative;
  display: inline-block;
  white-space: nowrap;
}}
.cursor {{
  display: inline-block;
  transform: translateY(-1px);
  color: var(--cyan);
  animation: blink 0.8s steps(1) infinite;
}}
@keyframes blink {{
  0%, 49% {{ opacity: 1; }}
  50%, 100% {{ opacity: 0; }}
}}

.page-title {{
  margin: 10px 0 10px 0;
  font-weight: 900;
  font-size: clamp(28px, 4.2vw, 40px);
  letter-spacing: -0.02em;
}}
.page-title .emoji {{
  margin-right: 10px;
  filter: drop-shadow(0 6px 16px rgba(0,0,0,0.35));
}}

/* Separator line */
.sep {{
  width: 100%;
  height: 4px;
  background: var(--grad);
  border-radius: 999px;
  margin: 16px 0 20px 0;
  box-shadow: 0 0 18px rgba(0,229,255,0.18), 0 0 18px rgba(255,43,214,0.12);
}}

/* =========================================================
   Cards: neon border
   ========================================================= */
.card {{
  position: relative;
  background:
    linear-gradient(var(--panel), var(--panel)) padding-box,
    var(--gradBorder) border-box;
  border: 1px solid transparent;
  border-radius: var(--radius);
  padding: 20px 20px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
}}
.card:hover {{
  box-shadow:
    0 0 0 1px rgba(255,43,214,0.22) inset,
    0 0 22px rgba(255,43,214,0.16),
    0 0 18px rgba(0,229,255,0.10),
    var(--shadow2);
}}
.card-title {{
  font-weight: 900;
  margin: 0 0 10px 0;
}}
.grad-title {{
  background: var(--grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.p {{
  color: var(--muted);
  line-height: 1.65;
  margin: 0.35rem 0;
}}

.inlineNote {{
  color: rgba(229,231,235,0.78);
  font-size: 14px;
  margin: 6px 0 10px 0;
}}
.inlineNote b {{
  color: rgba(229,231,235,0.94);
}}

[data-testid="stDataFrame"] {{
  border-radius: 16px;
  overflow: hidden;
  background: rgba(10,12,22,0.55) !important;
  border: 1px solid rgba(255,255,255,0.08);
}}

/* =========================================================
   Inputs: gradient border, NO focus/invalid highlight
   ========================================================= */
div[data-testid="stTextInput"] div[data-baseweb*="input"],
div[data-testid="stTextArea"] div[data-baseweb*="textarea"],
div[data-testid="stSelectbox"] div[data-baseweb*="select"] {{
  outline: none !important;
  box-shadow: none !important;
  border: none !important;
}}

div[data-testid="stTextInput"] div[data-baseweb*="input"] > div,
div[data-testid="stTextArea"] div[data-baseweb*="textarea"] > div,
div[data-testid="stSelectbox"] div[data-baseweb*="select"] > div {{
  background:
    linear-gradient(rgba(10, 12, 22, 0.78), rgba(10, 12, 22, 0.78)) padding-box,
    linear-gradient(135deg, rgba(255,43,214,0.70), rgba(0,229,255,0.48), rgba(139,92,246,0.28)) border-box !important;
  border: 1px solid transparent !important;
  border-radius: 14px !important;
  outline: none !important;
  box-shadow: none !important;
}}

div[data-testid="stTextInput"] div[data-baseweb*="input"]:focus-within,
div[data-testid="stTextInput"] div[data-baseweb*="input"] > div:focus-within,
div[data-testid="stTextArea"] div[data-baseweb*="textarea"]:focus-within,
div[data-testid="stTextArea"] div[data-baseweb*="textarea"] > div:focus-within,
div[data-testid="stSelectbox"] div[data-baseweb*="select"]:focus-within,
div[data-testid="stSelectbox"] div[data-baseweb*="select"] > div:focus-within {{
  outline: none !important;
  box-shadow: none !important;
}}

div[data-testid="stTextInput"] div[aria-invalid="true"],
div[data-testid="stTextArea"] div[aria-invalid="true"],
div[data-testid="stSelectbox"] div[aria-invalid="true"],
div[data-testid="stTextInput"] div[aria-invalid="true"] > div,
div[data-testid="stTextArea"] div[aria-invalid="true"] > div,
div[data-testid="stSelectbox"] div[aria-invalid="true"] > div {{
  outline: none !important;
  box-shadow: none !important;
  border-color: transparent !important;
}}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {{
  color: rgba(255,255,255,0.96) !important;
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  caret-color: rgba(0,229,255,0.95) !important;
}}

div[data-testid="stTextInput"] input:-webkit-autofill,
div[data-testid="stTextInput"] input:-webkit-autofill:hover,
div[data-testid="stTextInput"] input:-webkit-autofill:focus,
div[data-testid="stTextArea"] textarea:-webkit-autofill,
div[data-testid="stTextArea"] textarea:-webkit-autofill:hover,
div[data-testid="stTextArea"] textarea:-webkit-autofill:focus {{
  -webkit-text-fill-color: rgba(229,231,235,0.96) !important;
  transition: background-color 9999s ease-out 0s;
  -webkit-box-shadow: 0 0 0px 1000px rgba(10, 12, 22, 0.78) inset !important;
}}

/* =========================================================
   Buttons (general)
   ========================================================= */
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stButton"] > button,
div[data-testid="stDownloadButton"] > button,
div[data-testid="stFileUploader"] button {{
  background: linear-gradient(135deg, rgba(255,43,214,0.18), rgba(0,229,255,0.14)) !important;
  border: 1px solid rgba(255,43,214,0.30) !important;
  color: rgba(229,231,235,0.95) !important;
  border-radius: 14px !important;
  padding: 0.55rem 1.0rem !important;
  font-weight: 950 !important;
  box-shadow: 0 0 0 1px rgba(255,43,214,0.10) inset, 0 10px 26px rgba(0,0,0,0.35) !important;
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease, filter 0.12s ease;
}}
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover,
div[data-testid="stFileUploader"] button:hover {{
  transform: translateY(-1px);
  filter: brightness(1.05);
  border-color: rgba(0,229,255,0.55) !important;
  box-shadow: 0 0 18px rgba(0,229,255,0.16), 0 0 18px rgba(255,43,214,0.12), 0 14px 40px rgba(0,0,0,0.55) !important;
}}

/* =========================================================
   Radio -> pill buttons (global)
   ========================================================= */
div[data-testid="stRadio"] [role="radiogroup"] {{
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 10px !important;
  justify-content: flex-start !important;
  align-items: center !important;
}}

div[data-testid="stRadio"] label[data-baseweb="radio"] {{
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 999px !important;
  height: 38px !important;
  min-height: 38px !important;
  padding: 0 14px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  transition: transform .14s ease, border-color .14s ease, background .14s ease, box-shadow .14s ease;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {{
  display: none !important;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"] span {{
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  font-weight: 950 !important;
  color: rgba(229,231,235,0.92) !important;
  line-height: 1 !important;
  margin: 0 !important;
  padding: 0 !important;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {{
  transform: translateY(-1px);
  border-color: rgba(0,229,255,0.34) !important;
  box-shadow: 0 0 16px rgba(0,229,255,0.10), 0 0 18px rgba(255,43,214,0.08) !important;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {{
  background: linear-gradient(135deg, rgba(255,43,214,0.16), rgba(0,229,255,0.12)) !important;
  border-color: rgba(255,43,214,0.55) !important;
  box-shadow: 0 0 18px rgba(255,43,214,0.12), 0 0 16px rgba(0,229,255,0.10) !important;
}}

/* =========================================================
   File uploader panel
   ========================================================= */
div[data-testid="stFileUploader"] > div,
div[data-testid="stFileUploader"] section {{
  background:
    linear-gradient(var(--panel2), var(--panel2)) padding-box,
    linear-gradient(135deg, rgba(255,43,214,0.70), rgba(0,229,255,0.55), rgba(139,92,246,0.35)) border-box !important;
  border: 1px solid transparent !important;
  border-radius: var(--radius) !important;
  padding: 14px !important;
  box-shadow: 0 0 24px rgba(255,43,214,0.12), 0 0 20px rgba(0,229,255,0.10), var(--shadow) !important;
  backdrop-filter: blur(12px) !important;
}}

/* =========================================================
   Contact form card style
   ========================================================= */
div[data-testid="stForm"] {{
  background:
    linear-gradient(var(--panel), var(--panel)) padding-box,
    linear-gradient(135deg, rgba(255,43,214,0.62), rgba(0,229,255,0.45), rgba(139,92,246,0.30)) border-box !important;
  border: 1px solid transparent !important;
  border-radius: var(--radius) !important;
  padding: 18px 18px !important;
  box-shadow: 0 0 22px rgba(255,43,214,0.10), 0 0 18px rgba(0,229,255,0.08), var(--shadow) !important;
  backdrop-filter: blur(10px) !important;
}}
.contactIntro {{
  margin: 6px 0 14px 0;
  color: rgba(229,231,235,0.84);
  font-size: 14px;
}}
.contactIntro b {{
  color: rgba(229,231,235,0.96);
}}

/* =========================================================
   MENU: placed next to the SEP row (NOT fixed)
   ========================================================= */
div[data-testid="stPopover"],
div[data-testid="stExpander"] {{
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-end !important;
  justify-content: flex-start !important;
  gap: 10px !important;
  margin-top: 0 !important;
}}

div[data-testid="stPopover"],
div[data-testid="stExpander"] {{
  position: sticky !important;
  top: 10px !important;
  z-index: 2147483647 !important;
}}

div[data-testid="stPopover"] button {{
  background-image: url("{menu_icon_base64}"), linear-gradient(135deg, rgba(255,43,214,0.95), rgba(139,92,246,0.75)) !important;
  background-size: 22px 22px, cover !important;
  background-repeat: no-repeat, no-repeat !important;
  background-position: center, center !important;
  border: 1px solid rgba(255,43,214,0.65) !important;
  border-radius: 14px !important;
  height: 44px !important;
  width: 44px !important;
  padding: 0 !important;
  min-width: 44px !important;
}}
div[data-testid="stPopover"] button svg {{ display: none !important; }}
div[data-testid="stPopover"] button > div {{ opacity: 0 !important; }}

div[data-testid="stExpander"] summary {{
  list-style: none !important;
  cursor: pointer !important;

  background-image: url("{menu_icon_base64}"), linear-gradient(135deg, rgba(255,43,214,0.95), rgba(139,92,246,0.75)) !important;
  background-size: 22px 22px, cover !important;
  background-repeat: no-repeat, no-repeat !important;
  background-position: center, center !important;

  border: 1px solid rgba(255,43,214,0.65) !important;
  border-radius: 14px !important;
  height: 44px !important;
  width: 44px !important;

  padding: 0 !important;
  margin: 0 !important;

  color: transparent !important;
  font-size: 0 !important;
}}
div[data-testid="stExpander"] summary::-webkit-details-marker {{ display:none !important; }}
div[data-testid="stExpander"] summary svg {{ display:none !important; }}

div[data-testid="stPopoverBody"],
div[data-testid="stExpander"] details > div {{
width: min(80vw, 210px) !important;
min-width: fit-content !important;
height: fit-content !important; 
margin: 0 auto !important;         
padding-bottom: 80px !important;                 
overflow: visible !important;        
  padding: 22px 22px 20px 22px !important;
  padding-bottom: 80px;
  border-radius: 24px !important;
  background:
    linear-gradient(rgba(10, 12, 22, 0.86), rgba(10, 12, 22, 0.86)) padding-box,
    linear-gradient(135deg, rgba(255,43,214,0.62), rgba(0,229,255,0.52), rgba(139,92,246,0.40)) border-box !important;
  border: 1px solid transparent !important;
  box-shadow:
    0 20px 70px rgba(0,0,0,0.65),
    0 0 26px rgba(255,43,214,0.12),
    0 0 22px rgba(0,229,255,0.10) !important;
  backdrop-filter: blur(14px) !important;
  align-self: flex-end !important;
}}
div[data-testid="stPopoverBody"] * {{
  background-color: transparent !important;
}}
@media (max-width: 640px) {{
  div[data-testid="stPopoverBody"],
  div[data-testid="stExpander"] details > div {{
    max-width: calc(100vw - 28px) !important;
  }}
}}

.nav-head {{
  font-weight: 950;
  font-size: 22px;
  letter-spacing: -0.02em;
  margin: 2px 0 2px 0;
  background: var(--grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.nav-sub {{
  color: rgba(229,231,235,0.72);
  font-size: 12.5px;
  margin-bottom: 10px;
}}

div[data-testid="stPopoverBody"] div[data-testid="stRadio"] [role="radiogroup"],
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] [role="radiogroup"] {{
  display: flex !important;
  flex-direction: column !important;
  gap: 10px !important;
}}

div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"],
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"] {{
  width: 100% !important;
  border-radius: 16px !important;
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  padding: 12px 14px !important;
  cursor: pointer !important;
  position: relative !important;
  overflow: hidden !important;
  height: auto !important;
}}

div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child,
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {{
  display: none !important;
}}

div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"] span,
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"] span {{
  color: rgba(229,231,235,0.92) !important;
  font-weight: 900 !important;
  font-size: 15px !important;
}}

div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"]::before,
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"]::before {{
  content: "" !important;
  position: absolute !important;
  left: 0 !important;
  top: 0 !important;
  bottom: 0 !important;
  width: 4px !important;
  background: linear-gradient(180deg, rgba(0,229,255,0.75), rgba(255,43,214,0.75)) !important;
  opacity: 0 !important;
  transition: opacity 0.14s ease !important;
}}

div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"]:hover,
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {{
  transform: translateY(-1px);
  background: rgba(255,255,255,0.07) !important;
  border-color: rgba(0,229,255,0.35) !important;
}}

div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"]:hover::before,
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"]:hover::before {{
  opacity: 1 !important;
}}

div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"],
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {{
  background: linear-gradient(135deg, rgba(255,43,214,0.16), rgba(0,229,255,0.10)) !important;
  border-color: rgba(255,43,214,0.55) !important;
  box-shadow: 0 0 18px rgba(255,43,214,0.12), 0 0 16px rgba(0,229,255,0.08) !important;
}}
div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked)::before,
div[data-testid="stPopoverBody"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"]::before,
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked)::before,
div[data-testid="stExpander"] details > div div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"]::before {{
  opacity: 1 !important;
}}

.navIcons {{
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 5px;
  margin-bottom: 10px;
  padding-top: 0;
  border-top: none;
}}
.navIcons a {{
  width: 42px;
  height: 42px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  background:
    linear-gradient(rgba(10, 12, 22, 0.72), rgba(10, 12, 22, 0.72)) padding-box,
    linear-gradient(135deg, rgba(0,229,255,0.70), rgba(255,43,214,0.40)) border-box;
  border: 1px solid transparent;
  box-shadow: 0 0 18px rgba(0,229,255,0.10), 0 0 16px rgba(255,43,214,0.08);
  transition: transform .14s ease, box-shadow .14s ease, filter .14s ease;
}}
.navIcons a img {{
  width: 20px;
  height: 20px;
  border-radius: 6px;
  filter: invert(88%) sepia(30%) saturate(5400%) hue-rotate(155deg) brightness(115%) contrast(105%);
  opacity: 0.95;
}}
.navIcons a:hover {{
  transform: translateY(-2px) scale(1.08) rotate(-2deg);
  filter: brightness(1.08);
  box-shadow:
    0 0 22px rgba(0,229,255,0.18),
    0 0 22px rgba(255,43,214,0.14),
    0 16px 44px rgba(0,0,0,0.55);
}}

.siteFooter {{
  margin-top: 28px;
  padding: 18px 0 8px 0;
  text-align: center;
  color: rgba(229,231,235,0.55);
  font-size: 12px;
}}
.siteFooter .line {{
  height: 3px;
  width: min(520px, 92%);
  margin: 0 auto 12px auto;
  border-radius: 999px;
  background: var(--grad);
  opacity: 0.65;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ================= Helpers (UI) =================
def html_page_title(icon: str, title: str):
    st.markdown(
        f'<div class="page-title"><span class="emoji">{icon}</span>{title}</div>',
        unsafe_allow_html=True,
    )


def card(html_inner: str):
    st.markdown(f'<div class="card">{html_inner}</div>', unsafe_allow_html=True)


def safe_read_csv(uploaded_file) -> pd.DataFrame:
    try:
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        return pd.read_csv(uploaded_file, encoding="latin-1")
    except Exception:
        return pd.DataFrame()


def numeric_columns(df: pd.DataFrame):
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]


def style_plotly(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e5e7eb")),
        hoverlabel=dict(
            bgcolor="rgba(10,12,22,0.95)",
            font_color="#e5e7eb",
            bordercolor="rgba(0,229,255,0.35)",
        ),
        transition=dict(duration=450, easing="cubic-in-out"),
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.10)",
        tickcolor="rgba(255,255,255,0.10)",
        title_font=dict(color="#cbd5e1"),
        tickfont=dict(color="#cbd5e1"),
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.10)",
        tickcolor="rgba(255,255,255,0.10)",
        title_font=dict(color="#cbd5e1"),
        tickfont=dict(color="#cbd5e1"),
    )
    return fig


# ================= NAV: callback + close =================
def on_nav_change():
    sel = st.session_state.get("nav_selection", st.session_state.page)
    if sel != st.session_state.page:
        st.session_state.page = sel
        st.session_state.close_nav_js = True


# If flagged, inject JS to close popover OR expander after navigation.
# (Key added so it won't "stack" across reruns.)
if st.session_state.close_nav_js:
    components.html(
        """
        <script>
          (function(){
            try {
              const doc = window.parent.document;

              doc.dispatchEvent(
                new KeyboardEvent('keydown', {key:'Escape', code:'Escape', bubbles:true})
              );

              doc.querySelectorAll('details[open]').forEach(d => { d.open = false; });

              if (doc.body) doc.body.click();
            } catch (e) {}
          })();
        </script>
        """,
        height=0,
    )
    st.session_state.close_nav_js = False


# ================= 4. TOP HEADER =================
header_block = st.container()
with header_block:
    st.markdown(
        """
        <div class="headerWrap">
          <div class="brand">
            ⌬⏣🧬 <span class="title">Drug Design Lab</span>
            <span class="typeWrap">
              <span id="typeText" class="typeText" aria-label="typing-roles"></span>
              <span class="cursor">▍</span>
            </span>
          </div>
          <div class="subtitle">Clean, responsive lab profile • projects • data explorer • mini game</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Typewriter JS (Key added so it won't duplicate on reruns)
    components.html(
        """
        <script>
        (function(){
          const w = window.parent || window;

          const phrases = [
            "Pharmacist💊",
            "Tech enthusiast💻",
            "Nature lover🌱"
          ];

          function segmentGraphemes(str){
            try{
              if (w.Intl && w.Intl.Segmenter){
                const seg = new w.Intl.Segmenter(undefined, { granularity: 'grapheme' });
                return Array.from(seg.segment(str), x => x.segment);
              }
            } catch(e){}
            return Array.from(str);
          }

          try { if (w.__ddl_tw_timer) clearTimeout(w.__ddl_tw_timer); } catch(e) {}

          w.__ddl_tw_state = { i: 0, j: 0, deleting: false };

          function getEl(){
            try { return w.document.getElementById("typeText"); } catch(e) { return null; }
          }

          function tick(){
            const el = getEl();
            if(!el){ w.__ddl_tw_timer = setTimeout(tick, 120); return; }

            const s = w.__ddl_tw_state;
            const current = phrases[s.i] || "";
            const units = segmentGraphemes(current);

            const speedType = 120;
            const speedDelete = 70;
            const holdFull = 1200;
            const holdEmpty = 320;

            if(!s.deleting){
              s.j = Math.min(s.j + 1, units.length);
              el.textContent = units.slice(0, s.j).join("");
              if(s.j >= units.length){
                s.deleting = true;
                w.__ddl_tw_timer = setTimeout(tick, holdFull);
                return;
              }
              w.__ddl_tw_timer = setTimeout(tick, speedType);
              return;
            } else {
              s.j = Math.max(s.j - 1, 0);
              el.textContent = units.slice(0, s.j).join("");
              if(s.j <= 0){
                s.deleting = false;
                s.i = (s.i + 1) % phrases.length;
                w.__ddl_tw_timer = setTimeout(tick, holdEmpty);
                return;
              }
              w.__ddl_tw_timer = setTimeout(tick, speedDelete);
              return;
            }
          }

          tick();
        })();
        </script>
        """,
        height=0,
    )

# ================= 4b. SEP ROW + MENU =================
sep_col, menu_col = st.columns([0.92, 0.08], gap="small", vertical_alignment="center")

with sep_col:
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

with menu_col:
    pop = popover_compat(" ", use_container_width=False)
    with pop:
        st.markdown(
            """
            <div class="nav-head">Navigate</div>
            <div class="nav-sub">Pick a section</div>
            """,
            unsafe_allow_html=True,
        )

        st.radio(
            label="Navigation",
            options=list(pages.keys()),
            index=list(pages.keys()).index(st.session_state.page),
            format_func=page_label,
            key="nav_selection",
            label_visibility="collapsed",
            on_change=on_nav_change,
        )

        st.markdown(
            """
            <div class="navIcons">
              <a href="https://github.com" target="_blank" aria-label="GitHub 1">
                <img src="https://github.githubassets.com/favicons/favicon.png" />
              </a>
              <a href="https://za.linkedin.com/in/emmie-cockcroft-b57969296" target="_blank" aria-label="LinkedIn">
                <img src="https://cdn-icons-png.flaticon.com/512/61/61109.png" />
              </a>
              <a href="https://xoxothefrozenfox.github.io/EmmieCockcroftCV/" target="_blank" aria-label="CV">
                <img src="https://cdn-icons-png.flaticon.com/512/6406/6406017.png" />
              </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ================= 5. PAGE ROUTING =================
if st.session_state.page == "Researcher Profile":
    html_page_title("👩‍🔬", "Researcher Profile")

    left, right = st.columns(2, gap="large")

    with left:
        card(
            """
            <div class="card-title grad-title">Pharmacy Student — About</div>
            <div class="p">I am a committed pharmacy student with a strong desire to help those in need of medical care.
            I thrive in both collaborative and independent work environments, and I enjoy continuously learning.</div>
            <div class="p">Outside the medical realm, I find joy in teaching/tutoring, art, resin printing, and gaming.</div>
            <div class="card-title grad-title" style="margin-top: 25px; margin-bottom: 15px;">Interests</div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; row-gap: 20px; color: #cbd5e1; font-size: 14px;"><div>☕ Tea</div>
            <div>🎮 Gaming</div>
            <div>🍴 Cooking</div>
            <div>🖨️ 3D-Printing</div>
            <div>🖥️ Technology</div>
            <div>✈️ Traveling</div>
            <div>📕 Reading</div>
            <div>⚗️ Science</div>
            <div>🖌️ Art</div>
            <div>🐾 Pet-training</div>
            <div>🌿 Gardening</div>
            <div>💼 Business</div>
            """
        )

    with right:
        card(
            """
            <div class="card-title grad-title">Snapshot</div>
            <div class="p">🏫 NWU • Pharmacy (2022–Present)</div>
            <div class="p">🧑‍🏫 Teaching • Kyna (2023–2024)</div>
            <div class="p">🌍 TEFL • i-to-i (2021)</div>
            <div class="p">🎓 Matric • Wesvalia (2020)</div>
            <div style="height:10px"></div>
            <div class="card-title grad-title">Research Interests</div>
            <div class="p">AI • ML • Molecular Docking • Gene Mapping • Drug Delivery</div>
            """
        )

elif st.session_state.page == "AI Projects":
    html_page_title("🤖", "AI Projects")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        card(
            """
            <div class="card-title grad-title">Virtual Screening</div>
            <div class="p">Use ML to prioritize compounds and reduce wet-lab screening cost.</div>
            """
        )
    with c2:
        card(
            """
            <div class="card-title grad-title">Toxicity Prediction</div>
            <div class="p">Neural models trained on public datasets to flag risky candidates early.</div>
            """
        )

elif st.session_state.page == "Lab Data Explorer":
    html_page_title("🧪", "Lab Data Explorer")

    compound_data = pd.DataFrame(
        {
            "Compound ID": [f"CMPD-{i}" for i in range(1, 11)],
            "IC50 (nM)": np.random.uniform(10, 1000, 10),
            "LogP": np.random.uniform(0.2, 7, 10),
            "Molecular Weight": np.random.uniform(150, 500, 10),
        }
    )

    uploaded = st.file_uploader("Upload Experimental Data (CSV)", type="csv")

    if uploaded:
        df = safe_read_csv(uploaded)
        if df.empty:
            st.error("Could not read that CSV. Try exporting as UTF-8 and re-upload.")
            df = compound_data
        else:
            st.success("File uploaded successfully!")
    else:
        st.markdown(
            '<div class="inlineNote"><b>Showing sample dataset</b> (upload a CSV to view your own).</div>',
            unsafe_allow_html=True,
        )
        df = compound_data

    lab_tab = st.radio(
        label="e",
        options=["Data", "Visualize", "Quick stats"],
        horizontal=True,
        key="lab_tab",
        label_visibility="collapsed",
    )

    if lab_tab == "Data":
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif lab_tab == "Visualize":
        num_cols = numeric_columns(df)
        if len(num_cols) < 2:
            st.warning("Need at least two numeric columns to plot.")
        else:
            a, b, c = st.columns(3)
            with a:
                x_axis = st.selectbox("X-axis", options=num_cols, index=0, key="x_axis")
            with b:
                y_axis = st.selectbox("Y-axis", options=num_cols, index=1, key="y_axis")
            with c:
                chart_type = st.radio("Chart", ["Scatter", "Line", "Bar"], horizontal=True, key="chart_type")

            if chart_type == "Scatter":
                fig = px.scatter(df, x=x_axis, y=y_axis, hover_data=list(df.columns), opacity=0.92)
                fig.update_traces(
                    marker=dict(size=10, color="#00e5ff", line=dict(width=1, color="rgba(255,43,214,0.35)"))
                )
            elif chart_type == "Line":
                fig = px.line(df, x=x_axis, y=y_axis, markers=True)
                fig.update_traces(line=dict(width=3, color="#00e5ff"), marker=dict(size=7, color="#00e5ff"))
            else:
                fig = px.bar(df, x=x_axis, y=y_axis)
                fig.update_traces(
                    marker_color="#00e5ff",
                    marker_line_width=1,
                    marker_line_color="rgba(255,43,214,0.35)",
                )

            fig = style_plotly(fig)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Rows", f"{len(df):,}")
        with c2:
            st.metric("Columns", f"{df.shape[1]:,}")
        with c3:
            st.metric("Numeric cols", f"{len(numeric_columns(df)):,}")

        nums = numeric_columns(df)
        if nums:
            st.dataframe(df[nums].describe().T, use_container_width=True)

elif st.session_state.page == "Publications":
    html_page_title("🌐", "Publications")
    card("<div class='card-title grad-title'>Selected</div><div class='p'><b>Deep Learning in Pharmacokinetics</b></div>")

elif st.session_state.page == "Contact":
    html_page_title("📩", "Contact")
    st.markdown('<div class="contactIntro"><b>Send me a message below.</b></div>', unsafe_allow_html=True)

    # Form persistence
    if "contact_name" not in st.session_state:
        st.session_state.contact_name = ""
    if "contact_email" not in st.session_state:
        st.session_state.contact_email = ""
    if "contact_subject" not in st.session_state:
        st.session_state.contact_subject = ""
    if "contact_message" not in st.session_state:
        st.session_state.contact_message = ""
    if "contact_sending" not in st.session_state:
        st.session_state.contact_sending = False
    if "contact_notice" not in st.session_state:
        st.session_state.contact_notice = None  # {"kind":"success|error", "text":"..."}

    # Show last notice (prevents flicker + keeps message stable)
    if st.session_state.contact_notice:
        notice = st.session_state.contact_notice
        if notice["kind"] == "success":
            st.success(notice["text"])
        else:
            st.error(notice["text"])

    # Optional: config status (no secrets shown)
    # with st.expander("EmailJS config status (safe)", expanded=False):
    #     cfg = get_emailjs_config()
    #     st.write(
    #         {
    #             "service_id_present": bool(cfg["service_id"]),
    #             "template_id_present": bool(cfg["template_id"]),
    #             "public_key_present": bool(cfg["public_key"]),
    #             "private_key_present": bool(cfg["private_key"]),
    #             "secrets_file_hint": "Ensure .streamlit/secrets.toml (plural) in run directory.",
    #         }
    #     )

    with st.form("contact_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=st.session_state.contact_name, key="contact_name")
        with col2:
            email = st.text_input("Email", value=st.session_state.contact_email, key="contact_email")

        subject = st.text_input("Subject", value=st.session_state.contact_subject, key="contact_subject")
        message = st.text_area("Message", value=st.session_state.contact_message, key="contact_message", height=160)

        submitted = st.form_submit_button("Send", disabled=st.session_state.contact_sending)

    if submitted and not st.session_state.contact_sending:
        errs = []
        if not name.strip():
            errs.append("Name is required.")
        if not email.strip() or "@" not in email:
            errs.append("Valid email is required.")
        if not subject.strip():
            errs.append("Subject is required.")
        if not message.strip():
            errs.append("Message is required.")

        if errs:
            st.session_state.contact_notice = {"kind": "error", "text": " • " + "\n • ".join(errs)}
        else:
            st.session_state.contact_sending = True
            st.session_state.contact_notice = None

            with st.spinner("Sending..."):
                if submitted:
                    errs = []
                    if not name.strip():
                        errs.append("Name is required.")
                    if not email.strip() or "@" not in email:
                        errs.append("Valid email is required.")
                    if not subject.strip():
                        errs.append("Subject is required.")
                    if not message.strip():
                        errs.append("Message is required.")

                    if errs:
                        st.error(" • " + "\n • ".join(errs))
                    else:
                        # --- EMAILJS BROWSER SEND (THIS IS THE KEY PART) ---
                        components.html(
                            f"""
                            <script src="https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js"></script>
                            <script>
                            (function() {{
                                emailjs.init("{st.secrets['EMAILJS_PUBLIC_KEY']}");

                                emailjs.send(
                                "{st.secrets['EMAILJS_SERVICE_ID']}",
                                "{st.secrets['EMAILJS_TEMPLATE_ID']}",
                                {{
                                    from_name: `{name}`,
                                    reply_to: `{email}`,
                                    subject: `{subject}`,
                                    message: `{message}`,
                                    date: new Date().toLocaleString()
                                }}
                                ).then(
                                function() {{
                                    console.log("EmailJS success");
                                }},
                                function(error) {{
                                    console.error("EmailJS error:", error);
                                }}
                                );
                            }})();
                            </script>
                            """,
                            height=0,
                        )

                        st.success("Message sent successfully ✅")

elif st.session_state.page == "Antibiotic Fighter Game":
    html_page_title("🎮", "Nanobot vs Viruses")
    card(
        """
        <div class="card-title grad-title">Controls</div>
        <div class="p"><b>Move:</b> ← → (desktop) • Touch buttons (mobile)</div>
        <div class="p"><b>Fire:</b> Space / hold Fire</div>
        <div class="p"><b>Weapons:</b> Press <b>1</b>=Blaster, <b>2</b>=Missile, <b>3</b>=Laser, <b>4</b>=Shotgun</div>
        """
    )
    # Key added so the game iframe doesn't duplicate on reruns
    components.html(get_game_html(), height=GAME_HEIGHT)

# ================= Footer =================
st.markdown(
    """
    <div class="siteFooter">
      <div class="line"></div>
      © Charlene Cockcroft™
    </div>
    """,
    unsafe_allow_html=True,
)
