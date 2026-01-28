import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Drug Discovery Research Portal",
    layout="wide"
)

# ================= BRANDING & STYLES =================
st.markdown("""
<style>
:root {
    --cyan: #06b6d4;
    --magenta: #ec4899;
    --dark-bg: #0f172a;
    --dark-card: #111827;
    --glass-bg: rgba(255,255,255,0.12);
    --glass-border: rgba(255,255,255,0.25);
}

/* FULL-WIDTH NAVBAR */
.topnav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    background: linear-gradient(90deg, var(--cyan), var(--magenta));
    z-index: 9999;
    border-radius: 0 0 22px 22px;
}

/* Brand title */
.nav-title {
    font-size: 22px;
    font-weight: 900;
    color: white;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Nav icon buttons */
.stButton > button {
    background: rgba(255,255,255,0.18);
    border: none;
    border-radius: 12px;
    padding: 8px 12px;
    font-size: 18px;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: rgba(255,255,255,0.35);
    transform: translateY(-2px);
}

/* Glass cards */
.glass {
    background: var(--glass-bg);
    backdrop-filter: blur(18px);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

/* Gradient headers */
h1, h2, h3 {
    background: linear-gradient(90deg, var(--cyan), var(--magenta));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Push content below navbar */
.block-container {
    padding-top: 120px !important;
}
</style>
""", unsafe_allow_html=True)

# ================= NAVIGATION STATE =================
pages = {
    "👩‍🔬": "Researcher Profile",
    "🤖": "AI Drug Discovery Projects",
    "🧪": "Lab Data Explorer",
    "🌐": "Publications",
    "📩": "Contact",
    "🎮": "Antibiotic Fighter Game",
}

if "page" not in st.session_state:
    st.session_state.page = "Researcher Profile"

# ================= NAVBAR (VISUAL SHELL) =================
st.markdown("""
<div class="topnav">
    <div class="nav-title">🧬 De Novo Drug Design Lab</div>
</div>
""", unsafe_allow_html=True)

# ================= NAVBAR ICON BUTTONS =================
nav_cols = st.columns([7, 1, 1, 1, 1, 1, 1])
for col, (icon, page) in zip(nav_cols[1:], pages.items()):
    with col:
        if st.button(icon, key=f"nav_{page}"):
            st.session_state.page = page

menu = st.session_state.page

# ================= SAMPLE DATA =================
compound_data = pd.DataFrame({
    "Compound ID": [f"CMPD-{i}" for i in range(1, 11)],
    "IC50 (nM)": np.random.uniform(10, 1000, 10),
    "LogP": np.random.uniform(0.2, 7, 10),
    "Solubility (mg/mL)": np.random.uniform(0.01, 12, 10)
})

# =====================================================
# ================== RESEARCHER PROFILE ===============
# =====================================================
if menu == "Researcher Profile":
    st.title("Researcher Profile")
    st.markdown("""
    <div class="glass">
        <h2>Pharmacy Master's Student – AI Drug Discovery</h2>
        <p><b>Institution:</b> Your University</p>
        <p><b>Research Interests:</b> QSAR, ADMET, Molecular Docking, Generative AI</p>
        <p><b>Technical Skills:</b> Python, RDKit, Deep Learning</p>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# ============= AI DRUG DISCOVERY PROJECTS =============
# =====================================================
elif menu == "AI Drug Discovery Projects":
    st.title("AI Drug Discovery Projects")
    st.markdown("""
    <div class="glass">
        <h3>🔹 Virtual Screening Pipeline</h3>
        AI models predict compound bioactivity before lab testing.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
        <h3>🔹 Toxicity Prediction Models</h3>
        Neural networks classify toxicity risks.
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# ================= LAB DATA EXPLORER =================
# =====================================================
elif menu == "Lab Data Explorer":
    st.title("Lab Data Explorer")
    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df, use_container_width=True)

    st.subheader("Example Data")
    st.dataframe(compound_data, use_container_width=True)

# =====================================================
# =================== PUBLICATIONS ====================
# =====================================================
elif menu == "Publications":
    st.title("Publications")
    uploaded = st.file_uploader("Upload Publications CSV", type="csv")
    if uploaded:
        st.dataframe(pd.read_csv(uploaded), use_container_width=True)

# =====================================================
# ====================== CONTACT ======================
# =====================================================
elif menu == "Contact":
    st.title("Contact")
    st.markdown("""
    <div class="glass">
        <p><b>Email:</b> yourname@university.edu</p>
        <p><b>GitHub:</b> github.com/yourusername</p>
        <p><b>LinkedIn:</b> linkedin.com/in/yourprofile</p>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# ================= ANTIBIOTIC GAME ===================
# =====================================================
elif menu == "Antibiotic Fighter Game":
    st.title("Antibiotic Space Fighter 🧪 vs 🦠")

    components.html("""
    <canvas id="game" width="700" height="400"></canvas>
    <script>
    const c = document.getElementById("game");
    const x = c.getContext("2d");
    let p={x:330,y:350,w:40,h:20},b=[],e=[],s=0;
    setInterval(()=>e.push({x:Math.random()*660,y:0,w:20,h:20}),800);
    document.onkeydown=q=>{
      if(q.key=="ArrowLeft")p.x-=15;
      if(q.key=="ArrowRight")p.x+=15;
      if(q.key==" ")b.push({x:p.x+18,y:p.y});
    };
    function loop(){
      x.fillStyle="black";x.fillRect(0,0,700,400);
      b.forEach(o=>o.y-=6);
      e.forEach(o=>o.y+=2);
      b.forEach((o,i)=>e.forEach((u,j)=>{
        if(o.x<u.x+u.w&&o.x+4>u.x&&o.y<u.y+u.h&&o.y+10>u.y){
          b.splice(i,1);e.splice(j,1);s++;
        }}));
      x.fillStyle="cyan";x.fillRect(p.x,p.y,p.w,p.h);
      x.fillStyle="magenta";b.forEach(o=>x.fillRect(o.x,o.y,4,10));
      x.fillStyle="lime";e.forEach(o=>x.fillRect(o.x,o.y,o.w,o.h));
      x.fillStyle="white";x.fillText("Score: "+s,10,20);
      requestAnimationFrame(loop);
    }
    loop();
    </script>
    """, height=450)
