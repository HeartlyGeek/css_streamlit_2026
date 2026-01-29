import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# ================= 1. PAGE CONFIGURATION =================
st.set_page_config(
    page_title="Drug Design Lab",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ================= 2. STATE MANAGEMENT =================
if 'page' not in st.session_state:
    st.session_state.page = "Researcher Profile"

# Define pages and icons
pages = {
    "Researcher Profile": "👩‍🔬",
    "AI Projects": "🤖",
    "Lab Data Explorer": "🧪",
    "Publications": "🌐",
    "Contact": "📩",
    "Antibiotic Fighter Game": "🎮",
}

# ================= 3. CSS STYLING =================
st.markdown("""
<style>
    /* GLOBAL RESET */
    [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
    }
    .block-container {
        padding-top: 1rem !important;
        max-width: 100% !important;
    }

    /* TYPOGRAPHY */
    .nav-title {
        font-size: clamp(20px, 4vw, 28px);
        font-weight: 800;
        color: white;
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-title span {
        background: linear-gradient(90deg, #06b6d4, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* SEPARATOR */
    .separator {
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #06b6d4, #ec4899);
        border-radius: 2px;
        margin-top: 15px;
        margin-bottom: 30px;
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
    }

    /* DROPDOWN MENU BUTTON STYLING */
    /* This targets the popover button specifically */
    div[data-testid="stPopover"] > button {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255,255,255,0.2);
        color: #ec4899; /* Pink color for the icon */
        font-size: 24px;
        height: 50px;
        width: 50px; /* Square shape */
        border-radius: 12px;
        transition: all 0.2s ease;
        float: right; /* Ensure it sticks to the right */
    }
    div[data-testid="stPopover"] > button:hover {
        background-color: rgba(255, 255, 255, 0.15);
        border-color: #06b6d4;
        color: #06b6d4; /* Blue glow on hover */
        transform: scale(1.05);
    }

    /* MENU ITEM BUTTONS (Inside the dropdown) */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        background-color: transparent;
        color: #e2e8f0;
        text-align: left;
    }
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ec4899;
    }

    /* GLASS CARDS */
    .glass {
        background: #1e293b;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

</style>
""", unsafe_allow_html=True)

# ================= 4. NAVBAR RENDERING =================
with st.container():
    # Split into two columns: Title (Left) and Menu (Right)
    # The [9, 1] ratio ensures the title gets most space and pushes the menu to the edge
    col_title, col_menu = st.columns([9, 1])

    # --- COL 1: Title ---
    with col_title:
        st.markdown('<div class="nav-title">🔬⏣⌬ <span> Drug Design Lab </span> ⌬⏣🧬</div>', unsafe_allow_html=True)

    # --- COL 2: Unified Dropdown Menu (PC & Mobile) ---
    with col_menu:
        # The popover acts as the dropdown list
        with st.popover("☰", use_container_width=True):
            st.markdown("### Navigate")
            for page_name, icon in pages.items():
                # Highlight the active page
                if page_name == st.session_state.page:
                    button_label = f"📍 **{page_name}**"
                else:
                    button_label = f"{icon}  {page_name}"
                
                if st.button(button_label, key=f"nav_{page_name}", use_container_width=True):
                    st.session_state.page = page_name
                    st.rerun()

# --- SEPARATOR LINE ---
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)


# ================= 5. PAGE ROUTING =================

# --- RESEARCHER PROFILE ---
if st.session_state.page == "Researcher Profile":
    st.markdown("## 👩‍🔬 Researcher Profile")
    st.markdown("""
    <div class="glass">
        <h3 style="background: linear-gradient(90deg, #06b6d4, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Pharmacy Student – AI Drug Discovery
        </h3>
        <br>
        <p style="color: #cbd5e1;"><strong>Institution:</strong> North West University</p>
        <p style="color: #cbd5e1;"><strong>Research Interests:</strong> AI, ML, Molecular Docking, Gene Mapping, Drug Delivery </p>
    </div>
    <div class="glass">
        <h3 style="background: linear-gradient(90deg, #06b6d4, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Education 
        </h3>
        <br>
        <p style="color: #cbd5e1;"><strong>Bachelor in pharmacy:</strong> 2022-Present ~ NWU </p>
        <p style="color: #cbd5e1;"><strong>TEFL Diploma:</strong> 2021 ~ i-to-i </p>
        <p style="color: #cbd5e1;"><strong>Matriculated:</strong> 2020 ~ Wesvalia </p>
    </div>
    """, unsafe_allow_html=True)

# --- AI PROJECTS ---
elif st.session_state.page == "AI Projects":
    st.markdown("## 🤖 AI Projects")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="glass"><h3>🔹 Virtual Screening</h3><p>AI models predict compound bioactivity.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="glass"><h3>🔹 Toxicity Prediction</h3><p>DNN trained on Tox21 dataset.</p></div>""", unsafe_allow_html=True)

# --- LAB DATA EXPLORER ---
elif st.session_state.page == "Lab Data Explorer":
    st.markdown("## 🧪 Lab Data Explorer")
    compound_data = pd.DataFrame({
        "Compound ID": [f"CMPD-{i}" for i in range(1, 11)],
        "IC50 (nM)": np.random.uniform(10, 1000, 10),
        "LogP": np.random.uniform(0.2, 7, 10)
    })
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Experimental Data (CSV)", type="csv")
    if uploaded:
        st.dataframe(pd.read_csv(uploaded), use_container_width=True)
    else:
        st.info("Showing sample dataset.")
        st.dataframe(compound_data, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PUBLICATIONS ---
elif st.session_state.page == "Publications":
    st.markdown("## 🌐 Publications")
    st.markdown("""<div class="glass"><ul><li>"Deep Learning in Pharmacokinetics"</li></ul></div>""", unsafe_allow_html=True)

# --- CONTACT ---
elif st.session_state.page == "Contact":
    st.markdown("## 📩 Contact")
    st.markdown("""<div class="glass"><p>Email: research@drugdesignlab.com</p></div>""", unsafe_allow_html=True)

# --- GAME ---
elif st.session_state.page == "Antibiotic Fighter Game":
    st.markdown("## 🎮 Antibiotic Space Fighter")
    st.caption("Use **Left/Right Arrows** to move and **Spacebar** to shoot!")
    
    col_spacer, col_game, col_spacer2 = st.columns([1, 6, 1])
    with col_game:
        components.html("""
        <div style="display:flex; justify-content:center;">
            <canvas id="game" width="700" height="400" style="border: 2px solid #ec4899; border-radius: 10px; box-shadow: 0 0 20px rgba(236, 72, 153, 0.4);"></canvas>
        </div>
        <script>
        const c = document.getElementById("game"); const x = c.getContext("2d");
        let p={x:330,y:350,w:40,h:20},b=[],e=[],s=0;
        setInterval(()=>e.push({x:Math.random()*660,y:0,w:20,h:20}),800);
        document.onkeydown=q=>{if(q.key=="ArrowLeft")p.x-=20;if(q.key=="ArrowRight")p.x+=20;if(q.key==" ")b.push({x:p.x+18,y:p.y});};
        function loop(){
          x.fillStyle="#0f172a";x.fillRect(0,0,700,400);
          x.fillStyle="#ec4899";b.forEach(o=>o.y-=6);b.forEach(o=>x.fillRect(o.x,o.y,4,10));
          x.fillStyle="#22c55e";e.forEach(o=>o.y+=2);e.forEach(o=>x.fillRect(o.x,o.y,o.w,o.h));
          b.forEach((o,i)=>e.forEach((u,j)=>{if(o.x<u.x+u.w&&o.x+4>u.x&&o.y<u.y+u.h&&o.y+10>u.y){b.splice(i,1);e.splice(j,1);s++;}}));
          x.fillStyle="#06b6d4";x.fillRect(p.x,p.y,p.w,p.h);
          x.fillStyle="white";x.font="20px Arial";x.fillText("Score: "+s,20,30);
          requestAnimationFrame(loop);
        }
        loop();
        </script>
        """, height=450)