import streamlit as st

# Set page config
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Updated CSS to match exactly
st.markdown("""
    <style>
    /* Main container */
    .stApp {
        background-color: #1A1A1A !important;
    }
    
    /* Left sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A !important;
        width: 60px !important;
        padding: 0 !important;
    }
    
    [data-testid="stSidebar"] > div {
        padding-top: 0 !important;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Top navigation bar */
    .top-nav {
        position: fixed;
        top: 0;
        left: 60px;
        right: 0;
        height: 40px;
        background-color: #1A1A1A;
        border-bottom: 1px solid #333;
        display: flex;
        align-items: center;
        padding: 0 20px;
        z-index: 1000;
        font-size: 14px;
    }
    
    /* URL bar */
    .url-bar {
        position: fixed;
        top: 40px;
        left: 60px;
        right: 0;
        height: 35px;
        background-color: #1A1A1A;
        border-bottom: 1px solid #333;
        display: flex;
        align-items: center;
        padding: 0 10px;
        z-index: 999;
    }
    
    /* Search options container */
    .search-options {
        background-color: #2D2D2D;
        border-radius: 8px;
        padding: 20px;
        margin-top: 20px;
        width: 100%;
    }
    
    /* Individual search option */
    .search-option {
        background-color: #F3E8FF;
        border-radius: 25px;
        padding: 8px 16px;
        margin: 12px 0;
        display: flex;
        align-items: center;
        color: #000;
    }
    
    /* Bottom search bar */
    .bottom-search {
        position: fixed;
        bottom: 20px;
        left: 80px;
        width: calc(40% - 40px);
        background-color: #2D2D2D;
        padding: 12px 20px;
        border-radius: 8px;
        color: #666;
    }
    
    /* Hide default Streamlit input styling */
    .stTextInput > div > div > input {
        background-color: #2D2D2D !important;
        color: #666 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 20px !important;
    }
    
    /* Content area adjustments */
    .content-area {
        margin-top: 100px;
        padding: 0 20px;
        color: white;
    }
    
    /* Sidebar icons */
    .sidebar-icons {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 10px;
        gap: 25px;
        color: #888;
    }
    
    .sidebar-icons div {
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Left sidebar
with st.sidebar:
    st.markdown("""
        <div class="sidebar-icons">
            <div>🅰️</div>
            <div>➕</div>
            <div>📖</div>
            <div>📁</div>
            <div>↩️</div>
            <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);">👤</div>
        </div>
    """, unsafe_allow_html=True)

# Top navigation and URL bar
st.markdown("""
    <div class="top-nav">
        <span style="color: #888; margin-right: 20px;">projects/ecommerce_site</span>
        <span style="margin-right: 15px;">🌐 Preview</span>
        <span style="margin-right: 15px;">&lt;/&gt; Code</span>
        <span>⌘ Console</span>
    </div>
    
    <div class="url-bar">
        <span style="margin-right: 15px;">←</span>
        <span style="margin-right: 15px;">→</span>
        <span style="margin-right: 15px;">↻</span>
        <span style="background: #2D2D2D; flex-grow: 1; padding: 4px 10px; border-radius: 4px; margin: 0 10px;">/</span>
        <span style="margin-left: 15px;">⚡</span>
        <span style="margin-left: 15px;">↗</span>
        <span style="margin-left: 15px;">⛶</span>
    </div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([0.4, 0.6])

with col1:
    st.markdown("""
        <div class="content-area">
            <div style="margin-bottom: 15px;">
                Can you show me a few kinds of<br>
                search bar that I can add to my website
            </div>
            
            <div style="color: #888; margin-bottom: 20px;">
                Sure, here are a few designs.<br>
                Click on the design that you want to add.
            </div>
            
            <div class="search-options">
                <div class="search-option">
                    <span style="margin-right: 15px;">1.</span>
                    <span style="margin-right: 10px;">≡</span>
                    <span style="flex-grow: 1;">Search</span>
                    <span>🔍</span>
                </div>
                
                <div class="search-option">
                    <span style="margin-right: 15px;">2.</span>
                    <span style="margin-right: 10px;">←</span>
                    <span style="flex-grow: 1;">Search</span>
                    <span>×</span>
                </div>
                
                <div class="search-option">
                    <span style="margin-right: 15px;">3.</span>
                    <span>🔍</span>
                    <span style="flex-grow: 1;"></span>
                    <span>+</span>
                </div>
            </div>
        </div>
        
        <div class="bottom-search">
            🔍 Type your requirements or Ask AI
        </div>
    """, unsafe_allow_html=True)

# Preview area
with col2:
    st.markdown("""
        <div style="background-color: #F5F5F5; height: calc(100vh - 75px); margin-top: 75px;"></div>
    """, unsafe_allow_html=True)