import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from config import settings
from main import fetch_global_alerts, fetch_local_alerts
import sys
import importlib
import services.location_service
importlib.reload(services.location_service)
from services.location_service import LocationService
import services.ui_utils
importlib.reload(services.ui_utils)
from services.ui_utils import generate_card_html, generate_mini_popup_html, get_zoom_for_radius, format_expander_title, inject_global_clipboard_script, get_category_marker_icon, infer_category_from_brand
from services.logger_utils import setup_logger
import copy
import logging
import os

# Declare custom Kakao search component (Pure Frontend Autocomplete)
COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_components", "kakao_search")
kakao_search = components.declare_component("kakao_search", path=COMPONENT_DIR)

LOC_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_components", "device_location")
device_location = components.declare_component("device_location", path=LOC_COMPONENT_DIR)

from services.logger_utils import setup_logger
logger = setup_logger("app")

st.set_page_config(page_title="Info Waves", layout="wide")
inject_global_clipboard_script()

st.markdown("""
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Info Waves">
""", unsafe_allow_html=True)


theme_css = """
    :root, :root[data-theme="dark"] {
        --bg-main: #0B0F19;
        --bg-panel: rgba(22, 27, 43, 0.7);
        --text-main: #F8FAFC;
        --text-muted: #94A3B8;
        --border-color: rgba(255, 255, 255, 0.08);
        --primary: #3B82F6;
        --primary-glow: rgba(59, 130, 246, 0.3);
        --bg-subtle: rgba(255, 255, 255, 0.03);
        --hover-bg: rgba(255, 255, 255, 0.06);
        --search-bg: #1E293B;
        --search-color: #F8FAFC;
        --search-border: #334155;
        --search-icon: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%2394A3B8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>');
        --ctrl-bg: rgba(30, 41, 59, 0.9);
        --ctrl-border: rgba(255, 255, 255, 0.08);
    }
    :root[data-theme="light"] {
        --bg-main: #F1F5F9;
        --bg-panel: #FFFFFF;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --border-color: #CBD5E1;
        --primary: #2563EB;
        --primary-glow: rgba(37, 99, 235, 0.12);
        --bg-subtle: #F8FAFC;
        --hover-bg: #F1F5F9;
        --search-bg: #FFFFFF;
        --search-color: #0F172A;
        --search-border: #CBD5E1;
        --search-icon: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%2364748B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>');
        --ctrl-bg: rgba(255, 255, 255, 0.95);
        --ctrl-border: #CBD5E1;
    }
    :root[data-theme="dark"] .stTextInput input { background-color: #1E293B !important; color: white !important; border: 1px solid #334155 !important; }
    :root[data-theme="light"] .stTextInput input { background-color: #FFFFFF !important; color: black !important; border: 1px solid #CBD5E1 !important; }
"""

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');
    
    {theme_css}
    
    * {{
        font-family: 'Pretendard', -apple-system, sans-serif !important;
    }}
    
    [data-testid="stAppViewContainer"] {{ background-color: var(--bg-main) !important; color: var(--text-main) !important; transition: background-color 0.3s; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    
    /* Softly apply text color to common tags, letting Streamlit widgets override */
    p, span, h1, h2, h3, h4, h5, h6, label {{ 
        color: var(--text-main); 
    }}
    
    /* Invert tooltip colors to ensure readability on both themes */
    div[data-baseweb="tooltip"] {{
        background-color: var(--text-main) !important;
    }}
    div[data-baseweb="tooltip"] span, div[data-baseweb="tooltip"] div, div[data-baseweb="tooltip"] p {{
        color: var(--bg-main) !important;
    }}
    
    /* Completely hide Streamlit default running status widget text */
    [data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    /* Custom Glassmorphism Dimmed Spinner Overlay (Simple is the Best: Modern Minimal Ring) */
    [data-testid="stSpinner"] {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background: rgba(11, 15, 25, 0.45) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        z-index: 99999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    [data-testid="stSpinner"] > div {{
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        border: 2.5px solid rgba(255, 255, 255, 0.15) !important;
        border-top-color: #3B82F6 !important;
        animation: modernSpin 0.7s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite !important;
    }}
    @keyframes modernSpin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    /* Fix for Placeholders */
    ::placeholder {{
        color: var(--text-muted) !important;
        opacity: 1 !important;
    }}
    
    /* Hide Streamlit's 'Press Enter to apply' text */
    div[data-testid="InputInstructions"] {{
        display: none !important;
    }}
    
    /* User specified padding override for the radius slider */
    div[data-testid="stSlider"] div[data-baseweb="slider"], 
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div {{
        padding-top: 2px !important;
    }}
    
    /* Force ONLY the map's direct container and iframe to take full 100% width of the column */
    div[data-testid="element-container"]:has(iframe) {{
        width: 100% !important;
    }}
    div[data-testid="element-container"]:has(iframe) > div {{
        width: 100% !important;
    }}
    iframe[title="streamlit_folium.st_folium"] {{
        width: 100% !important;
    }}
    
    /* Parent column absolute anchoring */
    div[data-testid="column"]:first-child {{
        position: relative !important;
        padding-top: 0 !important;
    }}
    
    /* Rotate details arrow when open */
    details.branches-details[open] summary .dropdown-arrow {{
        transform: rotate(225deg) !important;
    }}

    /* Prevent Streamlit rerun dimming/flicker */
    div[data-testid="stAppViewContainer"] div[data-testid="stVerticalBlock"],
    div[data-testid="stAppViewContainer"] div[data-testid="element-container"] {{
        opacity: 1 !important;
        transition: none !important;
    }}

    /* 1. KakaoMap Clone: Top Search Bar */
    .kmap-search-anchor {{ display: none; }}
    div[data-testid="element-container"]:has(.kmap-search-anchor) {{
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
    }}
    div[data-testid="element-container"]:has(.kmap-search-anchor) + div[data-testid="element-container"] {{
        position: absolute !important;
        top: 30px !important;
        left: 0 !important;
        right: 0 !important;
        margin: 0 auto !important;
        width: 90% !important;
        max-width: 420px !important;
        z-index: 1000 !important;
        pointer-events: auto !important;
        opacity: 1 !important;
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }}
    div[data-testid="element-container"]:has(.kmap-search-anchor) + div[data-testid="element-container"] > div,
    div[data-testid="element-container"]:has(.kmap-search-anchor) + div[data-testid="element-container"] [data-testid="stCustomComponentV1"] {{
        width: 100% !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    div[data-testid="element-container"]:has(.kmap-search-anchor) + div[data-testid="element-container"] iframe {{
        width: 100% !important;
        height: 60px !important;
        min-height: 60px !important;
        border: none !important;
        outline: none !important;
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }}
    
    /* Streamlit Toast Notification Elevation & Mobile Centering */
    [data-testid="stToastContainer"] {{
        z-index: 999999 !important;
        position: fixed !important;
    }}
    
    @media (max-width: 480px) {{
        div[data-testid="element-container"]:has(.kmap-search-anchor) + div[data-testid="element-container"] {{
            top: 85px !important;
            max-width: 340px !important;
        }}
        div[data-testid="element-container"]:has(.kmap-search-anchor) + div[data-testid="element-container"] iframe {{
            height: 60px !important;
            min-height: 60px !important;
        }}
        [data-testid="stToastContainer"] {{
            top: 20px !important;
            bottom: auto !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            right: auto !important;
            width: 90% !important;
            max-width: 340px !important;
        }}
        [data-testid="stToast"] {{
            width: 100% !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6) !important;
            border-radius: 14px !important;
            background: rgba(30, 41, 59, 0.95) !important;
            color: #ffffff !important;
        }}
    }}
    
    /* 2. Floating Radius Controller */
    .kmap-ctrl-anchor {{ display: none; }}
    div[data-testid="stVerticalBlock"]:has(.kmap-ctrl-anchor) {{
        position: absolute !important;
        bottom: 30px !important;
        right: 20px !important;
        z-index: 999 !important;
        background: var(--ctrl-bg, rgba(30, 41, 59, 0.9)) !important;
        backdrop-filter: blur(12px) !important;
        padding: 12px 16px 8px 16px !important;
        border-radius: 16px !important;
        border: 1px solid var(--ctrl-border, rgba(255, 255, 255, 0.08)) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        width: 220px !important;
    }}
    
    /* Unify map mouse cursor everywhere (no switching between grab hand and pointing finger) */
    .leaflet-container, .leaflet-grab, .leaflet-interactive, .leaflet-marker-icon {{
        cursor: pointer !important;
    }}

    /* 2. KakaoMap Clone: Floating Radius Control (Horizontal Panel) */
    .kmap-radius-anchor {{ display: none; }}
    div[data-testid="element-container"]:has(.kmap-radius-anchor) {{
        display: none !important;
    }}
    
    div[data-testid="element-container"]:has(div[data-testid="stSlider"]) {{
        position: absolute !important;
        bottom: 120px !important;
        left: 0 !important;
        right: 0 !important;
        margin: 0 auto !important;
        width: 90% !important;
        max-width: 320px !important;
        height: 64px !important;
        z-index: 1000 !important;
        background: rgba(30, 41, 59, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        padding: 10px 20px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        display: flex !important;
        align-items: center !important;
        opacity: 1 !important;
    }}
    
    div[data-testid="element-container"]:has(div[data-testid="stSlider"]) div[data-testid="stSlider"] {{
        width: 100% !important;
        margin-top: 24px !important;
    }}
    
    div[data-testid="element-container"]:has(div[data-testid="stSlider"]) [data-testid="stWidgetLabel"] {{
        display: none !important;
    }}
    
    div[data-testid="element-container"]:has(div[data-testid="stSlider"]) * {{
        color: white !important;
    }}
    
    div[data-testid="element-container"]:has(div[data-testid="stSlider"]) [data-testid="stTickBar"] span {{
        font-size: 11px !important;
        font-weight: 600 !important;
    }}
    
    /* Remove gap in the column and make it relative */
    div[data-testid="stHorizontalBlock"] > div {{
        gap: 0 !important;
        position: relative !important;
    }}
    
    /* Remove padding/margin from iframe element-container */
    div[data-testid="column"]:has(iframe) > div[data-testid="element-container"]:has(iframe) {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    
    /* Fix iframe itself to be exactly 100% width and correct height */
    iframe[title="streamlit_folium.st_folium"] {{
        width: 100% !important;
        height: 550px !important;
        border-bottom-left-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
        margin-bottom: 0 !important;
        display: block !important;
    }}
    
    /* 3. Button attached directly below the map */
    .kmap-btn-anchor {{ display: none; }}
    div[data-testid="stVerticalBlock"]:has(.kmap-btn-anchor):not(:has(iframe[title="streamlit_folium.st_folium"])) {{
        margin-top: 0 !important;
        padding-top: 0 !important;
        transform: translateY(-4px) !important;
    }}
    
    div[data-testid="stVerticalBlock"]:has(.kmap-btn-anchor):not(:has(iframe[title="streamlit_folium.st_folium"])) button {{
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        height: 52px !important;
        margin: 0 !important;
        width: 100% !important;
        font-size: 15px !important;
    }}
    
    /* Ensure primary buttons keep their white text */
    button[kind="primary"] p, button[kind="primary"] span {{
        color: white !important;
    }}
    
    /* Move Theme Toggle Button to Far Right */
    [data-testid="column"]:last-of-type .stButton {{
        display: flex;
        justify-content: flex-end;
    }}
    
    .reportview-container .main .block-container {{ padding-top: 1rem; max-width: 1200px; }}
    
    /* Hero Section */
    .hero-container {{
        text-align: center;
        padding: 20px 20px 40px;
        margin-bottom: 24px;
        position: relative;
    }}
    .hero-title {{
        font-size: 3.4rem;
        font-weight: 800;
        margin-bottom: 12px;
        background: linear-gradient(135deg, var(--primary), #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }}
    .hero-subtitle {{
        font-size: 1.15rem;
        color: var(--text-muted);
        font-weight: 500;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }}
    
    /* Premium Panel (Control Panel) */
    .premium-panel {{
        background: var(--bg-panel);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.04);
    }}

    /* Button Modernization */
    .stButton>button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        background: var(--primary) !important;
        border: none !important;
        color: white !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px var(--primary-glow) !important;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px var(--primary-glow) !important;
        filter: brightness(1.1);
    }}
    
    /* Theme Toggle Button specific */
    button[kind="secondary"] {{
        background: var(--bg-subtle) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: none !important;
    }}
    button[kind="secondary"]:hover {{
        background: var(--hover-bg) !important;
    }}
    
    /* Streamlit Expander (전국구 핫딜 카테고리 영역) Styling & Spacing */
    [data-testid="stExpander"] {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 24px !important;
        box-shadow: none !important;
    }}
    
    /* Category Expander Main Container with Restored Border Line & 15px Padding */
    details.eqpbllx4,
    details.st-emotion-cache-13na8ym,
    [data-testid="stExpander"] > details,
    [data-testid="stExpander"] details {{
        padding: 15px !important;
        background-color: var(--bg-panel) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
    }}
    
    [data-testid="stExpander"] summary,
    details.eqpbllx4 summary,
    details.st-emotion-cache-13na8ym summary {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        padding: 8px 4px 12px 4px !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        color: var(--text-main) !important;
        background-color: transparent !important;
    }}

    [data-testid="stExpander"] summary:focus,
    [data-testid="stExpander"] summary:focus-visible,
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] summary:active {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }}

    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        padding: 15px 4px 12px 4px !important;
        border: none !important;
    }}
    
    /* Toggle Icon & SVG Border / Outline Transparency Rules */
    svg[data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderIcon"],
    .eyeqlp51,
    .ex0cdmw0,
    .st-emotion-cache-1pbsqtx,
    svg.eyeqlp51,
    svg.ex0cdmw0,
    svg.st-emotion-cache-1pbsqtx,
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"] {{
        border: none !important;
        border-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        background-color: transparent !important;
        stroke: none !important;
    }}

    /* Remove stroke from SVG bounding box path to eliminate the square box outline around the arrow icon */
    [data-testid="stExpander"] summary svg path[fill="none"],
    svg[data-testid="stExpanderToggleIcon"] path[fill="none"] {{
        stroke: none !important;
        border: none !important;
    }}

    /* Ensure Streamlit Expander Toggle Icon / Arrow SVG color & 100% visibility */
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"] svg,
    [data-testid="stExpander"] details summary svg {{
        fill: var(--text-main) !important;
        color: var(--text-main) !important;
        opacity: 1 !important;
        visibility: visible !important;
    }}
    
    /* Info Card Styles */
    .info-card {{
        background: var(--bg-panel);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
        border: 1px solid var(--border-color);
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s, border-color 0.25s;
        overflow: hidden;
    }}
    .info-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.09), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
        border-color: rgba(37, 99, 235, 0.4);
    }}
    .info-card-link {{
        display: block;
        padding: 20px;
        text-decoration: none !important;
        color: var(--text-main) !important;
        cursor: pointer;
    }}
    .info-card-header {{
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }}
    .info-card-logo {{
        width: 48px;
        height: 48px;
        border-radius: 14px;
        object-fit: contain;
        margin-right: 14px;
        border: 1px solid var(--border-color);
        background: white; 
        padding: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}
    .info-card-brand {{
        font-weight: 700;
        font-size: 1.2rem;
        color: var(--text-main);
    }}
    .info-card-title {{
        font-size: 1.05rem;
        color: var(--text-main);
        line-height: 1.6;
        font-weight: 500;
        opacity: 0.9;
    }}
    .info-card-branches {{
        padding: 0 20px 16px;
    }}
    details.branches-details {{
        margin-top: 10px;
        background: var(--bg-subtle);
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }}
    details.branches-details > summary {{
        cursor: pointer;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0;
        user-select: none;
        color: var(--text-main);
        opacity: 0.85;
        transition: opacity 0.2s;
    }}
    details.branches-details > summary:hover {{ opacity: 1; }}
    details.branches-details > ul {{
        margin: 0;
        padding: 4px 12px 12px;
        font-size: 0.95rem;
        color: var(--text-main);
    }}
    .branch-item {{
        margin-bottom: 8px;
        padding: 12px 14px;
        border-radius: 10px;
        cursor: pointer;
        transition: background 0.2s;
        list-style: none;
    }}
    .branch-item > summary::-webkit-details-marker {{
        display: none;
    }}
    .branch-item:hover {{
        background: var(--hover-bg);
    }}
    .branch-name {{
        font-weight: 600;
        color: var(--text-main);
    }}
    
    @media (max-width: 768px) {{
        .hero-title {{ font-size: 2.2rem; }}
        .hero-subtitle {{ font-size: 0.95rem; }}
        .premium-panel {{ padding: 16px; }}
        #custom-theme-toggle {{
            width: 44px !important;
            height: 44px !important;
            min-width: 44px !important;
            max-width: 44px !important;
        }}
        
        /* Tighten gap between map search button and benefits list on mobile */
        div[data-testid="stHorizontalBlock"]:has(iframe[title="streamlit_folium.st_folium"]) {{
            gap: 12px !important;
        }}
        
        div[data-testid="column"]:has(iframe[title="streamlit_folium.st_folium"]) {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        
        /* Zero out height & margins of hidden anchor elements ONLY (not the slider itself) */
        div[data-testid="element-container"]:has(.kmap-search-anchor),
        div[data-testid="element-container"]:has(.kmap-radius-anchor) {{
            margin: 0 !important;
            padding: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
        }}
        
        /* Ensure radius slider box remains visible & properly positioned INSIDE map boundary on mobile */
        div[data-testid="element-container"]:has(.kmap-radius-anchor) + div[data-testid="element-container"] {{
            display: flex !important;
            height: 64px !important;
            min-height: 64px !important;
            bottom: 115px !important;
            z-index: 1000 !important;
        }}
        
        /* Reduce top margin of column 2 (benefits list) on stacked mobile view */
        div[data-testid="column"]:has(h4) {{
            margin-top: 8px !important;
            padding-top: 0 !important;
        }}
        div[data-testid="column"]:has(h4) h4 {{
            margin-top: 4px !important;
        }}

        /* Clean Textless Loading Spinner CSS */
        div[data-testid="stSpinner"] > div > p,
        div[data-testid="stSpinner"] span,
        div[data-testid="stSpinner"] label {{
            display: none !important;
        }}
        div[data-testid="stSpinner"] > div {{
            margin: 10px auto !important;
            justify-content: center !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# Top Right Theme Toggle (Pure Frontend - ZERO Map Refresh)
col_spacer, col_theme = st.columns([12, 1])
with col_theme:
    st.html("""
    <div style="display:flex; justify-content:flex-end; width:100%;">
        <button id="custom-theme-toggle" title="테마 변경" style="background:var(--ctrl-bg); color:var(--text-main); border:1px solid var(--ctrl-border); border-radius:12px; width:44px; height:44px; min-width:44px; max-width:44px; padding:0; cursor:pointer; font-size:18px; transition:all 0.2s; box-shadow:0 2px 8px rgba(0,0,0,0.1); display:flex; align-items:center; justify-content:center;">☀️</button>
    </div>
    """)

# Hero Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Info Waves</div>
    <div class="hero-subtitle">전국구 핫딜부터 내 동네 숨은 혜택까지</div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60, show_spinner=False)
def get_global_data():
    try:
        return fetch_global_alerts()
    except Exception as e:
        logger.exception(f"Global alerts fetching failed: {e}")
        st.error("서버에서 정보를 가져오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
        return {}

with st.spinner(""):
    global_results = get_global_data()
location_service = LocationService()
auto_lat, auto_lon = location_service.get_current_location()

if "map_lat" not in st.session_state:
    st.session_state["map_lat"] = auto_lat
    st.session_state["map_lon"] = auto_lon
if "map_key_id" not in st.session_state:
    st.session_state["map_key_id"] = 0
if "radius_val" not in st.session_state:
    st.session_state["radius_val"] = 3.0
if "data_view" not in st.session_state:
    st.session_state["data_view"] = "내 주변 맞춤 혜택"
if "map_click_disabled" not in st.session_state:
    st.session_state["map_click_disabled"] = False

# HTML5 Geolocation: Automatically request current mobile/desktop device location ONLY ONCE on app load
if not st.session_state.get("_device_loc_initialized"):
    loc_event = device_location(key="device_geolocation")
    if loc_event and loc_event.get("status") == "success":
        dev_lat = round(float(loc_event.get("lat")), 6)
        dev_lon = round(float(loc_event.get("lon")), 6)
        st.session_state["_device_loc_initialized"] = True
        st.session_state["map_lat"] = dev_lat
        st.session_state["map_lon"] = dev_lon
        st.session_state["map_key_id"] += 1
        logger.info(f"📍 Device Real Location Initialized: {dev_lat}, {dev_lon}")
#        st.rerun()

def handle_search():
    sq = st.session_state.get("kmap_search", "")
    if sq:
        s_lat, s_lon = location_service.search_place(sq)
        if s_lat and s_lon:
            st.session_state["map_lat"] = s_lat
            st.session_state["map_lon"] = s_lon
            st.session_state["map_key_id"] += 1
            st.session_state["data_view"] = "내 주변 맞춤 혜택"
            st.session_state["map_click_disabled"] = False
            st.session_state.pop("_search_error", None)
            
            radius_km_val = st.session_state.get("radius_val", 3.0)
            searched_key = (round(float(s_lat), 5), round(float(s_lon), 5), round(float(radius_km_val), 2))
            try:
                st.session_state["_last_searched_key"] = searched_key
                st.session_state["local_results"] = fetch_local_alerts(s_lat, s_lon, global_results, radius_km_val)
                st.session_state["_local_results_ver"] = st.session_state.get("_local_results_ver", 0) + 1
            except Exception as e:
                logger.error(f"Automatic local alerts search failed for '{sq}': {e}")
            st.rerun()
        else:
            err_msg = f"'{sq}'의 위치를 찾을 수 없습니다."
            st.session_state["_search_error"] = err_msg
            st.toast(err_msg, icon="❌")
            st.rerun()

# --- Top Navigation ---
col_menu1, col_menu2 = st.columns(2)
curr_view = st.session_state.get("data_view", "내 주변 맞춤 혜택")

def set_view_local():
    st.session_state["data_view"] = "내 주변 맞춤 혜택"

def set_view_global():
    st.session_state["data_view"] = "전국구 핫딜"

with col_menu1:
    st.button("🎯 내 주변 혜택", type="primary" if curr_view == "내 주변 맞춤 혜택" else "secondary", use_container_width=True, on_click=set_view_local)

with col_menu2:
    st.button("🔥 전국구 핫딜", type="primary" if curr_view == "전국구 핫딜" else "secondary", use_container_width=True, on_click=set_view_global)

st.markdown("<br/>", unsafe_allow_html=True)

if st.session_state.get("_search_error"):
    st.warning(st.session_state["_search_error"], icon="⚠️")
    st.session_state.pop("_search_error", None)

# --- Ensure coordinates & radius are globally synchronized ---
lat_input = st.session_state["map_lat"]
lon_input = st.session_state["map_lon"]
radius_input = st.session_state.get("radius_val", 3.0)

current_loc_key = (
    round(float(lat_input), 5),
    round(float(lon_input), 5),
    round(float(radius_input), 2)
)

# Automatically fetch/synchronize local results if key changed or results are missing
if "local_results" not in st.session_state or st.session_state.get("_last_searched_key") != current_loc_key:
    try:
        st.session_state["_last_searched_key"] = current_loc_key
        st.session_state["local_results"] = fetch_local_alerts(lat_input, lon_input, global_results, radius_input)
        st.session_state["_local_results_ver"] = st.session_state.get("_local_results_ver", 0) + 1
    except Exception as e:
        logger.error(f"Automatic local alerts fetch failed: {e}")

# --- Main Layout ---
if curr_view == "내 주변 맞춤 혜택":
    col_map, col_data = st.columns([1, 1], gap="medium")

    with col_map:
        # 1. Base Map Rendering
        radius_km_val = st.session_state.get("radius_val", 3.0)
        map_key = f"loc_map_main_{st.session_state['map_key_id']}"
        
        # ALWAYS build a fresh map to prevent any st_folium dynamic update crashes.
        m = folium.Map(
            location=[lat_input, lon_input],
            zoom_start=13,
            control_scale=True,
            **{"doubleClickZoom": False}
        )
        
        # Add FontAwesome 4.7.0 stylesheet CDN for crisp marker icon rendering
        m.get_root().html.add_child(folium.Element('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">'))
        
        # Add basic elements directly to the map
        folium.CircleMarker(
            location=[lat_input, lon_input],
            radius=8,
            color="#2563EB",
            weight=2,
            fill=True,
            fill_color="#3B82F6",
            fill_opacity=1.0,
            interactive=False
        ).add_to(m)
        
        folium.Circle(
            location=[lat_input, lon_input],
            radius=radius_km_val * 1000,
            color="#10B981",
            weight=2,
            fill=True,
            fill_color="#34D399",
            fill_opacity=0.2,
            interactive=False
        ).add_to(m)
        
        if "local_results" in st.session_state:
            local_results = st.session_state["local_results"]
            for category, items in local_results.items():
                if not items or category == "내 주변 매장 혜택": continue
                grouped_items = {}
                for item in items:
                    key = (item.get("brand", "알 수 없음"), item.get("title", ""), item.get("details", ""))
                    if key not in grouped_items: grouped_items[key] = []
                    grouped_items[key].append(item)
                
                for (brand, title, link), branch_items in grouped_items.items():
                    for branch in branch_items:
                        b_lat = branch.get("lat")
                        b_lon = branch.get("lon")
                        if b_lat and b_lon:
                            popup_html = generate_mini_popup_html(brand, title, link)
                            popup = folium.Popup(folium.Html(popup_html, script=True), max_width=320)
                            icon_style = get_category_marker_icon(brand, branch.get("orig_category") or category)
                            folium.Marker(
                                location=[b_lat, b_lon],
                                popup=popup,
                                tooltip=f"[{brand}] {branch.get('target', brand)}",
                                icon=folium.Icon(
                                    color=icon_style["color"],
                                    icon=icon_style["icon"],
                                    icon_color=icon_style.get("icon_color", "white"),
                                    prefix=icon_style.get("prefix", "fa")
                                )
                            ).add_to(m)

        # 1. KakaoMap Clone: Top Search Bar (Floated over top of map)
        with st.container():
            st.markdown('<div class="kmap-search-anchor"></div>', unsafe_allow_html=True)
            
            search_event = kakao_search(
                key="kmap_searchbox"
            )
            
            if search_event:
                action = search_event.get("action")
                val = search_event.get("value")
                
                if action == "submit":
                    ts = search_event.get("ts")
                    if val and ts != st.session_state.get("_last_search_ts"):
                        st.session_state["_last_search_ts"] = ts
                        st.session_state["_last_searchbox_val"] = val
                        st.session_state["kmap_search"] = val
                        handle_search()
                elif action == "my_location":
                    ts = search_event.get("ts")
                    if ts != st.session_state.get("_last_myloc_ts"):
                        st.session_state["_last_myloc_ts"] = ts
                        m_lat = round(float(search_event.get("lat")), 6)
                        m_lon = round(float(search_event.get("lon")), 6)
                        logger.info(f"📍 Returning to My Device Location: ({m_lat}, {m_lon})")
                        st.session_state["map_lat"] = m_lat
                        st.session_state["map_lon"] = m_lon
                        st.session_state["map_key_id"] += 1
                        st.session_state["data_view"] = "내 주변 맞춤 혜택"
                        st.session_state.pop("local_results", None)
                        st.rerun()

        # 2. Folium Map rendering
        try:
            map_data = st_folium(
                m, 
                height=550, 
                use_container_width=True,
                key=map_key,
                returned_objects=["last_clicked"]
            )
        except Exception as e:
            logger.exception(f"Map rendering failed: {e}")
            st.error("지도 렌더링 중 오류가 발생했습니다.")
            map_data = None

        if map_data:
            last_clicked = map_data.get("last_clicked")
            if last_clicked:
                c_lat = round(last_clicked.get("lat", 0), 6)
                c_lon = round(last_clicked.get("lng", 0), 6)
                
                if st.session_state.get("map_lat") != c_lat or st.session_state.get("map_lon") != c_lon:
                    logger.info(f"[MAP_CLICK_PROCESS] Updating location base to ({c_lat}, {c_lon})")
                    st.session_state["map_lat"] = c_lat
                    st.session_state["map_lon"] = c_lon
                    st.session_state["map_key_id"] += 1
                    st.session_state["data_view"] = "내 주변 맞춤 혜택"
                    st.session_state.pop("local_results", None)
                    st.rerun()

        # 3. Search Button directly attached BELOW the map (not floated)
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 탐색", use_container_width=True, type="primary"):
            c_lat, c_lon = st.session_state["map_lat"], st.session_state["map_lon"]
            radius_km_val = st.session_state.get("radius_val", 3.0)
            searched_key = (round(float(c_lat), 5), round(float(c_lon), 5), round(float(radius_km_val), 2))
            
            with st.spinner(""):
                try:
                    st.cache_data.clear()
                    st.session_state["_last_searched_key"] = searched_key
                    st.session_state["local_results"] = fetch_local_alerts(c_lat, c_lon, global_results, radius_km_val)
                    st.session_state["_local_results_ver"] = st.session_state.get("_local_results_ver", 0) + 1
                except Exception as e:
                    st.error(f"주변 혜택 매핑 실패: {e}")
                
            st.session_state["last_searched_lat"] = c_lat
            st.session_state["last_searched_lon"] = c_lon
            st.session_state["data_view"] = "내 주변 맞춤 혜택"
            st.rerun()

        # 3. KakaoMap Clone: Right Floating Radius Control
        with st.container():
            st.markdown('<div class="kmap-radius-anchor"></div>', unsafe_allow_html=True)
            
            def sync_radius():
                st.session_state["radius_val"] = st.session_state["radius_slider_widget"]

            st.slider(
                "탐색 반경 (km)", 
                min_value=0.5,
                max_value=10.0,
                value=st.session_state.get("radius_val", 3.0),
                step=0.5,
                format="%.1fkm",
                key="radius_slider_widget", 
                on_change=sync_radius,
                label_visibility="collapsed"
            )

    with col_data:
        st.markdown("#### 🎯 내 주변 혜택 목록")
        if "local_results" in st.session_state:
            local_results = st.session_state["local_results"]
            has_local = False
            for cat, items in local_results.items():
                if not items or cat == "내 주변 매장 혜택": continue
                has_local = True
                
                grouped_items = {}
                for item in items:
                    key = (item.get("brand", "알 수 없음"), item.get("title", ""), item.get("details", ""))
                    if key not in grouped_items: grouped_items[key] = []
                    grouped_items[key].append(item)
                    
                is_expanded = True
                with st.expander(format_expander_title(cat, len(grouped_items)), expanded=is_expanded):
                    for (brand, title, link), branch_items in grouped_items.items():
                        card = generate_card_html(brand, title, link, branch_items)
                        st.markdown(card, unsafe_allow_html=True)
                        
            if not has_local:
                st.info("현재 지정한 위치 주변에 매칭되는 소식이 없습니다.")
        else:
            st.info("지도 하단에서 탐색 반경을 조절한 후 '탐색' 버튼을 눌러주세요.")
            
else:
    if not any(global_results.values()):
        st.info("현재 수집된 전국구 정보가 없습니다.")
    else:
        for category, items in global_results.items():
            if not items or any(k in category for k in ["거지맵", "커뮤니티", "루리웹", "에펨"]): continue
            is_expanded_g = ("팝업" in category or "편의점" in category)
            with st.expander(format_expander_title(category, len(items)), expanded=is_expanded_g):
                col1, col2, col3 = st.columns(3)
                for i, item in enumerate(items[:30]):
                    col = [col1, col2, col3][i % 3]
                    target = item.get("target", "알 수 없음")
                    title = item.get("title", "")
                    link = item.get("details", "")
                    card = generate_card_html(target, title, link)
                    col.markdown(card, unsafe_allow_html=True)
