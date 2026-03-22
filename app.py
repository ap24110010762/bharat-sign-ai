import ast
# Manual fix for Python 3.14 compatibility
if not hasattr(ast, 'Str'):
    ast.Str = ast.Constant

import streamlit as st
import easyocr
from aksharamukha import transliterate
import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Bharat Sign AI", layout="wide")

# --- PREMIUM MINIMALIST CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #ffffff; }
    
    /* Sleek Top Header */
    .header-container { 
        text-align: center; 
        padding: 2.5rem 1rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        border-radius: 0 0 40px 40px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .header-container h1 { font-size: 2.5rem; font-weight: 800; color: white !important; margin: 0; }
    .header-container p { font-size: 1rem; opacity: 0.8; letter-spacing: 1px; }

    /* Ultra-Clean Dark Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #0f172a;
        color: #f8fafc;
        padding-top: 20px;
    }
    
    /* Styling the Sidebar Labels */
    [data-testid="stSidebar"] .stSelectbox label, 
    [data-testid="stSidebar"] .stToggle label {
        color: #94a3b8 !important;
        font-weight: 400 !important;
        font-size: 0.85rem;
        margin-bottom: 5px;
    }

    /* Main Content Section Header */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .accent-bar { width: 5px; height: 22px; background: #3b82f6; border-radius: 10px; }

    /* Action Button */
    .stButton>button {
        background: #3b82f6; 
        color: white;
        font-weight: 700; 
        border-radius: 12px; 
        height: 3.5rem;
        transition: all 0.3s ease;
        border: none;
        width: 100%;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    .stButton>button:hover { 
        background: #2563eb; 
        transform: translateY(-2px);
        color: white;
    }
    
    /* Remove Streamlit branding */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- TOP HEADER ---
st.markdown("""
    <div class='header-container'>
        <h1>Bharat Sign AI</h1>
        <p>Advanced Script Transliteration Engine</p>
    </div>
    """, unsafe_allow_html=True)

# --- CLEAN SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Selection directly in sidebar
    target_lang_display = st.selectbox(
        "Choose Language", 
        ["Tamil", "Telugu", "Kannada", "Malayalam", "Bengali", "Gujarati", "Gurmukhi", "Hindi", "ISO (English)"]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    improve_img = st.toggle("Enhance Image", value=True)
    st.markdown("<p style='color:#64748b; font-size:0.75rem;'>Improves script detection accuracy</p>", unsafe_allow_html=True)

# --- OCR ENGINE ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['hi', 'en'])
reader = load_ocr()

# --- MAIN CONTENT ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("<div class='section-header'><div class='accent-bar'></div>Source Image</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        
        if improve_img:
            img = cv2.convertScaleAbs(img, alpha=1.2, beta=20)
            img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # CHANGED: Fixed 'width' setting to stop warnings
        st.image(img_rgb, width="stretch")

with col2:
    st.markdown("<div class='section-header'><div class='accent-bar'></div>Processed Result</div>", unsafe_allow_html=True)
    
    if uploaded_file:
        if st.button("EXECUTE AI ANALYSIS"):
            with st.spinner("Analyzing scripts..."):
                
                lang_map = {
                    "Tamil": "Tamil", "Telugu": "Telugu", "Kannada": "Kannada",
                    "Malayalam": "Malayalam", "Bengali": "Bengali", "Gujarati": "Gujarati",
                    "Gurmukhi": "Gurmukhi", "Hindi": "Devanagari", "ISO (English)": "ISO"
                }
                actual_target = lang_map.get(target_lang_display)

                results = reader.readtext(img)
                
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.imshow(img_rgb)
                
                found_text = False
                for (bbox, text, prob) in results:
                    if prob > 0.15:
                        found_text = True
                        try:
                            trans_text = transliterate.process('Devanagari', actual_target, text)
                        except: 
                            trans_text = text
                        
                        top_left = tuple(map(int, bbox[0]))
                        ax.text(top_left[0], top_left[1]-20, trans_text, 
                                fontsize=18, color='white', fontweight='bold', 
                                family='Nirmala UI', 
                                bbox=dict(facecolor='#3b82f6', alpha=0.9, edgecolor='none', boxstyle='round,pad=0.5'))
                        
                        rect = plt.Rectangle(top_left, bbox[2][0]-bbox[0][0], bbox[2][1]-bbox[0][1], 
                                             fill=False, edgecolor='#10b981', linewidth=4)
                        ax.add_patch(rect)

                ax.axis('off')
                
                if found_text:
                    # CHANGED: Fixed 'width' setting inside plot section
                    st.pyplot(fig)
                    st.success(f"Transliterated to {target_lang_display}")
                else:
                    st.error("No text detected.")
    else:
        st.info("Upload an image on the left to start.")

st.markdown("<br>", unsafe_allow_html=True)
