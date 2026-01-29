import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components


hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ================= 1. PAGE CONFIGURATION =================
st.set_page_config(
    page_title="Drug Design Lab",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    /* GLOBAL DARK THEME & RESET */
    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
        background-color: #0f172a; /* Slate 900 - Main Background */
    }
    
    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
        max-width: 100% !important;
    }

    h1, h2, h3, p, span, div, li {
        color: #f8fafc; /* Slate 50 */
        font-family: 'Source Sans Pro', sans-serif;
    }

    /* ================= NAVBAR STYLING ================= */
    /* Target the container holding the navbar elements */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #1e293b; /* Darker Slate for the header background */
        padding: 1rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        border-radius: 0;
        
        /* THE GRADIENT LINE */
        border-bottom: 4px solid;
        border-image-slice: 1;
        border-image-source: linear-gradient(90deg, #06b6d4, #ec4899);
    }

    /* NAVBAR TITLE */
    .nav-title {
        font-size: 26px;
        font-weight: 800;
        color: white;
        margin-top: 5px;
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

    /* NAVIGATION BUTTONS (ICONS) */
    div.stButton > button {
        background-color: rgba(255, 255, 255, 0.05); /* Subtler background */
        color: #e2e8f0;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        font-size: 22px;
        height: 45px;
        width: 100%;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.15);
        border-color: #06b6d4; /* Cyan border on hover */
        transform: translateY(-2px);
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
    }
    
    div.stButton > button:active {
        transform: scale(0.96);
    }
    
    /* GLASS CARDS FOR CONTENT */
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
    # Columns: Title (Wide) | Spacer | Icons (Narrow)
    col_layout = [3, 2] + [0.5] * len(pages)
    cols = st.columns(col_layout)

    # -- LEFT: Title --
    with cols[0]:
        st.markdown('<div class="nav-title">🔬⏣⌬ <span> Drug Design Lab </span> ⌬⏣🧬</div>', unsafe_allow_html=True)

    # -- RIGHT: Icons --
    for col, (page_name, icon) in zip(cols[2:], pages.items()):
        with col:
            if st.button(icon, key=f"nav_{page_name}", help=page_name):
                st.session_state.page = page_name
                st.rerun()

# ================= 5. PAGE ROUTING =================

# --- RESEARCHER PROFILE ---
if st.session_state.page == "Researcher Profile":
    st.markdown("## 👩‍🔬 Researcher Profile")
    st.markdown("""
    <div class="glass">
        <h3 style="background: linear-gradient(90deg, #06b6d4, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Pharmacy Master's Student – AI Drug Discovery
        </h3>
        <br>
        <p style="color: #cbd5e1;"><strong>Institution:</strong> University of Cape Town</p>
        <p style="color: #cbd5e1;"><strong>Research Interests:</strong> QSAR, ADMET, Molecular Docking, Generative AI</p>
        <p style="color: #cbd5e1;"><strong>Technical Skills:</strong> Python, RDKit, Deep Learning, PyTorch</p>
    </div>
    """, unsafe_allow_html=True)

# --- AI PROJECTS ---
elif st.session_state.page == "AI Projects":
    st.markdown("## 🤖 AI Projects")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="glass">
            <h3>🔹 Virtual Screening Pipeline</h3>
            <p>AI models predict compound bioactivity before lab testing. Utilizing Random Forest and XGBoost for initial triage.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass">
            <h3>🔹 Toxicity Prediction Models</h3>
            <p>Deep Neural Networks (DNN) trained on Tox21 dataset to classify potential toxicity risks early in the design phase.</p>
        </div>
        """, unsafe_allow_html=True)

# --- LAB DATA EXPLORER ---
elif st.session_state.page == "Lab Data Explorer":
    st.markdown("## 🧪 Lab Data Explorer")
    
    # Sample Data
    compound_data = pd.DataFrame({
        "Compound ID": [f"CMPD-{i}" for i in range(1, 11)],
        "IC50 (nM)": np.random.uniform(10, 1000, 10),
        "LogP": np.random.uniform(0.2, 7, 10),
        "Solubility (mg/mL)": np.random.uniform(0.01, 12, 10)
    })

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Experimental Data (CSV)", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Showing sample dataset. Upload a CSV to view your own data.")
        st.dataframe(compound_data, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PUBLICATIONS ---
elif st.session_state.page == "Publications":
    st.markdown("## 🌐 Publications")
    st.markdown("""
    <div class="glass">
        <ul>
            <li><strong>"Deep Learning in Pharmacokinetics"</strong> - <em>Journal of ChemInfo (2024)</em></li>
            <li><strong>"Optimizing ADMET profiles with GA"</strong> - <em>Preprint (2023)</em></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- CONTACT ---
elif st.session_state.page == "Contact":
    st.markdown("## 📩 Contact")
    st.markdown("""
    <div class="glass">
        <p><b>Email:</b> research@drugdesignlab.com</p>
        <p><b>GitHub:</b> github.com/drugdesignlab</p>
        <p><b>LinkedIn:</b> linkedin.com/in/researcher</p>
    </div>
    """, unsafe_allow_html=True)

# --- GAME ---
elif st.session_state.page == "Antibiotic Fighter Game":
    st.markdown("## 🎮 Antibiotic Space Fighter")
    st.caption("Use **Left/Right Arrows** to move and **Spacebar** to shoot antibiotics at the bacteria!")
    
    col_spacer, col_game, col_spacer2 = st.columns([1, 6, 1])
    with col_game:
        components.html("""
        <div style="display:flex; justify-content:center;">
            <canvas id="game" width="700" height="400" style="border: 2px solid #ec4899; border-radius: 10px; box-shadow: 0 0 20px rgba(236, 72, 153, 0.4);"></canvas>
        </div>
        <script>
        const c = document.getElementById("game");
        const x = c.getContext("2d");
        let p={x:330,y:350,w:40,h:20},b=[],e=[],s=0;
        
        setInterval(()=>e.push({x:Math.random()*660,y:0,w:20,h:20}),800);
        
        document.onkeydown=q=>{
          if(q.key=="ArrowLeft")p.x-=20;
          if(q.key=="ArrowRight")p.x+=20;
          if(q.key==" ")b.push({x:p.x+18,y:p.y});
        };
        
        function loop(){
          x.fillStyle="#0f172a";
          x.fillRect(0,0,700,400);
          
          x.fillStyle="#ec4899";
          b.forEach(o=>o.y-=6);
          b.forEach(o=>x.fillRect(o.x,o.y,4,10));
          
          x.fillStyle="#22c55e";
          e.forEach(o=>o.y+=2);
          e.forEach(o=>x.fillRect(o.x,o.y,o.w,o.h));
          
          b.forEach((o,i)=>e.forEach((u,j)=>{
            if(o.x < u.x + u.w && o.x + 4 > u.x && o.y < u.y + u.h && o.y + 10 > u.y){
              b.splice(i,1);
              e.splice(j,1);
              s++;
            }
          }));
          
          x.fillStyle="#06b6d4";
          x.fillRect(p.x,p.y,p.w,p.h);
          
          x.fillStyle="white";
          x.font = "20px Arial";
          x.fillText("Bacteria Destroyed: "+s, 20, 30);
          
          requestAnimationFrame(loop);
        }
        loop();
        </script>
        """, height=450)