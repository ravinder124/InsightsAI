import os
os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "2000"
import streamlit as st
import time
from Pages.auth_utils import create_user, user_exists, authenticate_user, save_contact_query
import json
from dotenv import load_dotenv
load_dotenv()
import os

api_key = os.getenv("OPENAI_API_KEY")
st.info(f"[DEBUG] OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
# Monochromatic Color Palette
PRIMARY = "#25282b"   # Main dark background
SECONDARY = "#f8f8f8" # Off-white for contrast
TEXT_DARK = "#FFFFFF" # White text everywhere
BACKGROUND = PRIMARY   # Main background
CARD = "#2d3035"      # Slightly lighter than PRIMARY for cards/sections
ACCENT = "#35373b"    # For subtle accents, buttons, etc.
BORDER = "#3a3d42"    # For borders and dividers

# Custom CSS for monochromatic theme
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND} !important;
        color: {TEXT_DARK} !important;
    }}
    /* Header full-width, dark background */
    .main-header {{
        background: {PRIMARY};
        width: 100vw;
        margin: 0 calc(-50vw + 50%);
        padding: 1rem 0.5rem 0.5rem 0.5rem;
        border-radius: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        left: 0;
        right: 0;
        z-index: 100;
        box-shadow: 0 4px 24px rgba(37,40,43,0.24);
    }}
    .main-header .logo {{
        display: flex;
        align-items: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: {TEXT_DARK} !important;
        gap: 0.7rem;
        letter-spacing: 1px;
        margin-left: 1rem;
    }}
    .main-header .logo span {{
        font-size: 2.5rem;
    }}
    .main-header .nav {{
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }}
    .main-header .nav a {{
        color: {TEXT_DARK} !important;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.4rem 1.1rem;
        border-radius: 8px;
        transition: background 0.2s, color 0.2s;
        background: transparent;
        margin-left: 0.2rem;
        margin-right: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}
    .main-header .nav a:hover {{
        background: {ACCENT};
        color: {SECONDARY} !important;
        text-decoration: none !important;
    }}
    .main-header .nav .signup {{
        background: {ACCENT};
        color: {TEXT_DARK} !important;
        border-radius: 8px;
        font-weight: 700;
        padding: 0.4rem 1.2rem;
        border: none;
        transition: all 0.3s ease;
        margin-left: 0.5rem;
    }}
    .main-header .nav .signup:hover {{
        background: {SECONDARY};
        color: {PRIMARY} !important;
    }}
    /* Hero section full width, slightly lighter dark */
    .hero-section {{
        width: 100vw;
        margin: 0 calc(-50vw + 50%);
        padding: 3rem 0 2.5rem 0;
        border-radius: 0;
        background: {CARD};
        color: {TEXT_DARK};
        text-align: center;
        box-shadow: 0 4px 24px rgba(37,40,43,0.08);
        border: none;
        max-width: 100vw;
    }}
    .hero-section h1, .hero-section p {{
        color: {TEXT_DARK};
    }}
    .hero-section h1 {{
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 1rem;
        margin-top: 0;
        background: none;
        -webkit-text-fill-color: unset;
    }}
    .hero-section p {{
        font-size: 1.25rem;
        font-weight: 400;
        margin-bottom: 0;
        margin-top: 0;
        line-height: 1.6;
    }}
    /* All cards, tables, preview, chat, etc. use CARD color */
    .stDataFrame, .stTable, .stMetric, .stFileUploader, .stJson, .themed-card, .whats-happening-card, .element-container, .block-container, .stMarkdown, .stText, .stExpander, .stButton, .stSelectbox, .stTextInput, .stSlider, .stRadio, .stCheckbox, .stNumberInput, .stDateInput, .stTimeInput, .stColorPicker, .stForm {{
        background-color: {CARD} !important;
        color: {TEXT_DARK} !important;
        border-radius: 8px;
        border: none !important;
        box-shadow: none !important;
    }}
    /* Remove white backgrounds and shadows from all containers, cards, and boxes */
    .stMarkdown, .stText, .stExpander, .stButton, .stSelectbox, .stTextInput, .stSlider, .stRadio, .stCheckbox, .stNumberInput, .stDateInput, .stTimeInput, .stColorPicker, .stForm {{
        background: {CARD} !important;
        box-shadow: none !important;
        border: none !important;
        color: {TEXT_DARK} !important;
    }}
    .block-container {{
        width: 100vw !important;
        max-width: 100vw !important;
        margin: 0 calc(-50vw + 50%);
        background: {BACKGROUND} !important;
        padding-left: 2vw !important;
        padding-right: 2vw !important;
    }}
    /* Sidebar styling */
    .stApp [data-testid="stSidebar"] > div:first-child {{
        background-color: {ACCENT};
        border-right: 1px solid {BORDER};
        color: {TEXT_DARK};
    }}
    /* Button styling */
    .stButton > button {{
        background: {ACCENT};
        color: {TEXT_DARK};
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        background: {SECONDARY};
        color: {PRIMARY};
    }}
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {CARD};
        border-radius: 8px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(37,40,43,0.08);
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: {SECONDARY};
        border-radius: 6px;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {ACCENT} !important;
        color: {TEXT_DARK} !important;
    }}
    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div > div > select {{
        background-color: {CARD};
        color: {TEXT_DARK};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {{
        border-color: {SECONDARY};
        box-shadow: 0 0 0 2px rgba(248,248,248,0.2);
    }}
    /* Chat message styling */
    .stChatMessage, .stChatInput > div > div > input {{
        background-color: {CARD} !important;
        color: {TEXT_DARK} !important;
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    .stChatMessage[data-testid="chat-message-user"] {{
        background-color: {ACCENT};
        color: {TEXT_DARK};
    }}
    .stChatMessage[data-testid="chat-message-assistant"] {{
        background-color: {CARD};
        color: {TEXT_DARK};
        border-left: 4px solid {SECONDARY};
    }}
    /* Expander styling */
    .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {CARD};
        color: {TEXT_DARK};
        border-radius: 8px;
        border: 1px solid {BORDER};
    }}
    /* Code block styling */
    .stCode {{
        background-color: {ACCENT};
        border: 1px solid {BORDER};
        border-radius: 8px;
        color: {TEXT_DARK};
    }}
    /* Plotly chart container */
    .js-plotly-plot {{
        background-color: {CARD};
        border-radius: 8px;
        border: 1px solid {BORDER};
    }}
    /* Update Data Management and Chat Interface icons to match theme */
    .themed-icon {{
        color: {SECONDARY} !important;
        font-size: 2.1rem;
        vertical-align: middle;
        margin-right: 0.5rem;
    }}
    /* Add a small gap between Data Management and Chat Interface columns */
    .stHorizontalBlock {{
        gap: 1.5rem !important;
    }}
    /* Center the Debug tab and its content */
    .stTabs, .whats-happening-card {{
        margin-left: auto !important;
        margin-right: auto !important;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .whats-happening-card {{
        width: 60vw !important;
        min-width: 350px;
        max-width: 900px;
    }}
    </style>
""", unsafe_allow_html=True)

# Set Streamlit to wide mode
st.set_page_config(layout="wide", page_title="Main Dashboard", page_icon="🤖")

# --- HEADER WITH LOGO USING st.image ---
header_col1, header_col2 = st.columns([0.13, 0.87])
with header_col1:
    st.image('images/logo.png', width=70, output_format='PNG', use_container_width=False)
    st.markdown('<div style="font-size:2.2rem;font-weight:800;color:#fff;letter-spacing:1px;margin-top:-0.5rem;">Insights AI</div>', unsafe_allow_html=True)
with header_col2:
    st.markdown(f'''
        <div class="main-header" style="background:{PRIMARY};width:95vw;margin:0 calc(-50vw + 50%);padding:1rem 0.5rem 0.5rem 0.5rem;border-radius:0;display:flex;align-items:center;justify-content:flex-end;position:sticky;top:0;left:0;right:0;z-index:100;box-shadow:0 4px 24px rgba(37,40,43,0.24);">
            <div class="nav" style="display:flex;gap:1.5rem;align-items:center;">
                <a href="#" style="color:{TEXT_DARK};text-decoration:none;font-weight:600;font-size:1.1rem;padding:0.4rem 1.1rem;border-radius:8px;background:transparent;margin-left:0.2rem;margin-right:0.2rem;display:flex;align-items:center;gap:0.4rem;"><span>📊</span>Dashboard</a>
                <a href="#about-us" onclick="document.getElementById('about-us').scrollIntoView({{behavior: 'smooth'}});" style="color:{TEXT_DARK};text-decoration:none;font-weight:600;font-size:1.1rem;padding:0.4rem 1.1rem;border-radius:8px;background:transparent;margin-left:0.2rem;margin-right:0.2rem;display:flex;align-items:center;gap:0.4rem;"><span>👥</span>About Us</a>
                <a href="#pricing" onclick="document.getElementById('pricing').scrollIntoView({{behavior: 'smooth'}});" style="color:{TEXT_DARK};text-decoration:none;font-weight:600;font-size:1.1rem;padding:0.4rem 1.1rem;border-radius:8px;background:transparent;margin-left:0.2rem;margin-right:0.2rem;display:flex;align-items:center;gap:0.4rem;"><span>💲</span>Pricing</a>
                <a href="#contact" onclick="document.getElementById('contact').scrollIntoView({{behavior: 'smooth'}});" style="color:{TEXT_DARK};text-decoration:none;font-weight:600;font-size:1.1rem;padding:0.4rem 1.1rem;border-radius:8px;background:transparent;margin-left:0.2rem;margin-right:0.2rem;display:flex;align-items:center;gap:0.4rem;"><span>📞</span>Contact Us</a>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# HERO SECTION (NEW COMBINED IMAGE)
st.markdown('''
<div style="position:relative; width:100vw; left:50%; right:50%; margin-left:-50vw; margin-right:-50vw; background: radial-gradient(ellipse at 60% 40%, #232a36 60%, #1a1e23 100%); border-radius: 0 0 24px 24px; padding: 3.5rem 2rem 2.5rem 2rem; margin-bottom: 0; box-shadow: none; min-height: 540px; overflow: hidden;">
    <!-- Enlarged Background icons -->
    <div style="position:absolute; top:1.5rem; left:1.5rem; opacity:0.18; font-size:4.2rem;">📄</div>
    <div style="position:absolute; top:1.5rem; right:1.5rem; opacity:0.18; font-size:4.2rem;">📈</div>
    <div style="position:absolute; bottom:2rem; left:1.5rem; opacity:0.18; font-size:3.7rem;">📄</div>
    <div style="position:absolute; bottom:2rem; right:1.5rem; opacity:0.18; font-size:3.7rem;">📊</div>
    <div style="position:absolute; top:1.5rem; right:8rem; opacity:0.18; font-size:3.2rem;">⚡</div>
    <div style="position:absolute; bottom:2rem; right:8rem; opacity:0.18; font-size:3.7rem;">✔️</div>
    <!-- Main content -->
    <div style="text-align:center; max-width:1200px; margin:0 auto;">
        <h1 style="font-size:3.6rem; font-weight:900; color:#e6eaf3; margin-bottom:0.7rem; margin-top:0; letter-spacing:-2px; line-height:1.1;">
            Transform Data Into Insights
        </h1>
        <div style="display: flex; justify-content: center; align-items: stretch; gap: 2.5rem; margin: 2.5rem 0 2.5rem 0;">
            <!-- Left: Excel to Charts -->
            <div style="flex:1; min-width:220px; max-width:320px; background:rgba(53,55,59,0.7); border-radius:16px; padding:2rem 1.2rem; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <div style="font-size:2.7rem;">📊 ➡️ 📈 📉 📊</div>
                <div style="margin-top:1.2rem; color:#b6f5c1; font-size:1.15rem; font-weight:600;">Upload Excel, Get Interactive Charts</div>
                <div style="margin-top:0.7rem; color:#e6eaf3; font-size:1.02rem; opacity:0.7;">Seamlessly turn spreadsheets into beautiful, interactive visualizations.</div>
            </div>
            <!-- Center: Drive Sales Boost Performance -->
            <div style="flex:2; display:flex; flex-direction:column; align-items:center; justify-content:center; min-width:320px;">
                <h1 style="font-size:2.7rem; font-weight:900; color:#6fffa1; margin-bottom:0.5rem; margin-top:0.5rem; letter-spacing:-1px; line-height:1.15;">
                    Drive Sales <br>Boost Performance
                </h1>
            </div>
            <!-- Right: Charts to Growth -->
            <div style="flex:1; min-width:220px; max-width:320px; background:rgba(53,55,59,0.7); border-radius:16px; padding:2rem 1.2rem; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <div style="font-size:2.7rem;">📈 ➡️ 🚀 💸 📈</div>
                <div style="margin-top:1.2rem; color:#6fffa1; font-size:1.15rem; font-weight:600;">Insights that Drive Growth</div>
                <div style="margin-top:0.7rem; color:#e6eaf3; font-size:1.02rem; opacity:0.7;">Visual insights that boost sales, revenue, and team performance.</div>
            </div>
        </div>
        <div style="display:flex; justify-content:center; gap:1.2rem; margin-bottom:2.5rem;">
            <!-- Buttons removed as per user request -->
        </div>
        <div style="display:flex; justify-content:center; gap:3.5rem; margin-top:2.5rem;">
            <div style="text-align:center;">
                <span style="font-size:1.5rem; font-weight:700; color:#fff;">99.9%</span><br>
                <span style="color:#b6bfc9; font-size:1rem;">Accuracy Rate</span>
            </div>
            <div style="text-align:center;">
                <span style="font-size:1.5rem; font-weight:700; color:#6fffa1;">+45%</span><br>
                <span style="color:#b6bfc9; font-size:1rem;">Sales Growth</span>
            </div>
            <div style="text-align:center;">
                <span style="font-size:1.5rem; font-weight:700; color:#6fffa1;">+60%</span><br>
                <span style="color:#b6bfc9; font-size:1rem;">Team Efficiency</span>
            </div>
            <div style="text-align:center;">
                <span style="font-size:1.5rem; font-weight:700; color:#6fffa1;">+35%</span><br>
                <span style="color:#b6bfc9; font-size:1rem;">Revenue Increase</span>
            </div>
        </div>
    </div>
    <div style="position:absolute; left:50%; bottom:1.2rem; transform:translateX(-50%); opacity:0.25;">
        <svg width="32" height="32" viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" stroke="#b6f5c1" stroke-width="2" fill="none"/><rect x="15" y="10" width="2" height="10" rx="1" fill="#b6f5c1"/><circle cx="16" cy="23" r="1.5" fill="#b6f5c1"/></svg>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)

# JavaScript for button navigation
st.markdown("""
<script>
function scrollToDashboard() {
    // Scroll to the sign-up/login section (dashboard area)
    const dashboardSection = document.querySelector('.stExpander');
    if (dashboardSection) {
        dashboardSection.scrollIntoView({behavior: 'smooth'});
    }
}

function scrollToDemo() {
    // Scroll to the demo video section
    const demoSection = document.getElementById('demo-video');
    if (demoSection) {
        demoSection.scrollIntoView({behavior: 'smooth'});
    }
}
</script>
""", unsafe_allow_html=True)

# SIGN UP and LOG IN EXPANDERS SIDE BY SIDE
col_signup, col_login = st.columns(2)
with col_signup:
    with st.expander("📊 Sign Up", expanded=st.session_state.get('show_signup', False)):
        col_left, col_right = st.columns([1,1])
        with col_left:
            st.markdown(f"""
                <div style='background:{ACCENT};color:{TEXT_DARK};border-radius:12px;padding:2rem 1rem;text-align:center;height:100%;display:flex;flex-direction:column;justify-content:center;'>
                    <h2 style='margin-bottom:1rem;'>Come join us!</h2>
                    <p style='font-size:1.1rem;'>We are so excited to have you here.<br>If you haven't already, create an account to get access to exclusive features and insights.</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='display:flex;justify-content:center;margin-top:0.3rem;'>", unsafe_allow_html=True)
            if st.button('Already have an account? Sign in.', key='switch_to_login'):
                st.session_state['show_signup'] = False
                st.session_state['show_login'] = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with col_right:
            st.markdown("<h2 style='color:#fff; font-weight:800; margin-bottom:1.5rem;'>Signup</h2>", unsafe_allow_html=True)
            username = st.text_input('Username', key='signup_username')
            email = st.text_input('Email', key='signup_email')
            password = st.text_input('Password', type='password', key='signup_password')
            confirm_password = st.text_input('Confirm Password', type='password', key='signup_confirm')
            if st.button('Signup', key='signup_submit'):
                if user_exists(username, email):
                    st.error('Username or email already exists.')
                elif password != confirm_password:
                    st.error('Passwords do not match.')
                else:
                    if create_user(username, email, password):
                        st.success('Account created! Please log in.')
                        st.session_state['show_signup'] = False
                    else:
                        st.error('Error creating account. Try a different username/email.')
with col_login:
    with st.expander("🔑 Log In", expanded=st.session_state.get('show_login', False)):
        col_left, col_right = st.columns([1,1])
        with col_left:
            st.markdown(f"""
                <div style='background:{ACCENT};color:{TEXT_DARK};border-radius:12px;padding:2rem 1rem;text-align:center;height:100%;display:flex;flex-direction:column;justify-content:center;'>
                    <h2 style='margin-bottom:1rem;'>Welcome back!</h2>
                    <p style='font-size:1.1rem;'>Log in to access your personalized dashboard and insights.</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='display:flex;justify-content:center;margin-top:0.3rem;'>", unsafe_allow_html=True)
            if st.button("Don't have an account? Sign up.", key='switch_to_signup'):
                st.session_state['show_login'] = False
                st.session_state['show_signup'] = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with col_right:
            st.markdown("<h2 style='color:#fff; font-weight:800; margin-bottom:1.5rem;'>Log In</h2>", unsafe_allow_html=True)
            login_username = st.text_input('Username', key='login_username')
            login_password = st.text_input('Password', type='password', key='login_password')
            if st.button('Log In', key='login_submit'):
                if authenticate_user(login_username, login_password):
                    st.success('Logged in successfully!')
                    st.session_state['show_login'] = False
                    st.session_state['user'] = login_username  # Store username as string
                else:
                    st.error('Invalid username or password.')

# Add session state for expander visibility
if 'show_login' not in st.session_state:
    st.session_state['show_login'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False
if 'scroll_to_contact' not in st.session_state:
    st.session_state['scroll_to_contact'] = False

# Handle scroll to contact
if st.session_state.get('scroll_to_contact', False):
    st.markdown("""
        <script>
            setTimeout(function() {
                document.getElementById('contact').scrollIntoView({behavior: 'smooth'});
            }, 300);
        </script>
    """, unsafe_allow_html=True)
    st.session_state['scroll_to_contact'] = False

def open_login():
    st.session_state['show_login'] = True
    st.session_state['show_signup'] = False

def open_signup():
    st.session_state['show_signup'] = True
    st.session_state['show_login'] = False

# Helper to get logged-in username
user_logged_in = st.session_state.get('user')
username = user_logged_in if isinstance(user_logged_in, str) else None

# Set up user-specific upload and data dictionary paths
if username:
    user_upload_dir = os.path.join('uploads', username)
    os.makedirs(user_upload_dir, exist_ok=True)
    user_data_dict_path = os.path.join(user_upload_dir, 'data_dictionary.json')
    if os.path.exists(user_data_dict_path):
        with open(user_data_dict_path, 'r') as f:
            data_dictionary = json.load(f)
    else:
        data_dictionary = {}
else:
    # Fallback for not logged in: use session state
    if 'user_files' not in st.session_state:
        st.session_state['user_files'] = []
    user_upload_dir = 'uploads'
    user_data_dict_path = 'data_dictionary.json'
    if os.path.exists(user_data_dict_path):
        with open(user_data_dict_path, 'r') as f:
            data_dictionary = json.load(f)
    else:
        data_dictionary = {}

data_visualisation_page = st.Page(
    "./Pages/python_visualisation_agent.py", title="Data Visualisation", icon="📈"
)

pg = st.navigation(
    {
        "Visualisation Agent": [data_visualisation_page]
    }
)

pg.run()

# ============================================================================
# DEMO VIDEO SECTION
# ============================================================================
st.markdown('''
<div id="demo-video" style="padding: 3rem 0; background: #25282b; margin: 0 calc(-50vw + 50%); width: 100vw;">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem; text-align: center;">
        <h2 style="color: #FFFFFF; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">See It In Action</h2>
        <p style="color: #f8f8f8; font-size: 1.2rem; margin-bottom: 2.5rem;">Watch how easy it is to transform your data into insights</p>
        <div style="background: #35373b; border-radius: 16px; padding: 2.5rem; max-width: 900px; margin: 0 auto;">
            <iframe width="100%" height="400" src="https://www.youtube.com/embed/AhWr2V-ihkc" frameborder="0" allowfullscreen style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);"></iframe>
            <p style="color: #f8f8f8; font-size: 1rem; margin-top: 1.5rem; opacity: 0.8;">Demo: Complete Data Analysis Workflow - From Upload to Insights</p>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

# ============================================================================
# PRICING SECTION
# ============================================================================
st.markdown('<div id="pricing" style="padding: 4rem 0; background: #2d3035; margin: 0 calc(-50vw + 50%); width: 100vw;"><div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem;"><div style="text-align: center; margin-bottom: 3rem;"><h1 style="color: #FFFFFF; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">Choose Your Plan</h1><p style="color: #f8f8f8; font-size: 1.2rem; max-width: 600px; margin: 0 auto;">Start with our free tier and scale up as your data analysis needs grow</p></div></div></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div style="background: #35373b; border-radius: 16px; padding: 2.5rem; border: 2px solid #3a3d42; position: relative; display: flex; flex-direction: column; align-items: center;">'
        '<h3 style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">Free</h3>'
        '<div style="display: flex; align-items: baseline; justify-content: center; margin-bottom: 1rem;"><span style="color: #FFFFFF; font-size: 3rem; font-weight: 800;">$0</span><span style="color: #f8f8f8; font-size: 1.1rem; margin-left: 0.5rem;">/month</span></div>'
        '<p style="color: #f8f8f8; font-size: 0.9rem;">Perfect for getting started</p>'
        '<ul style="list-style: none; padding: 0; margin-bottom: 2rem;">'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Up to 5 file uploads per month</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Basic AI analysis (10 queries/day)</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Standard visualizations</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Community support</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Sample datasets access</li>'
        '</ul>'
        , unsafe_allow_html=True)
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    if st.button("Get Started Free", key="free_btn", use_container_width=True):
        st.session_state['show_signup'] = True
        st.session_state['show_login'] = False
        st.session_state['scroll_to_signup'] = True
        st.rerun()
with col2:
    st.markdown('<div style="background: linear-gradient(135deg, #35373b 0%, #2d3035 100%); border-radius: 16px; padding: 2.5rem; border: 2px solid #f8f8f8; position: relative; transform: scale(1.05); display: flex; flex-direction: column; align-items: center;">'
        '<div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #f8f8f8; color: #25282b; padding: 0.5rem 1.5rem; border-radius: 20px; font-weight: 700; font-size: 0.9rem;">MOST POPULAR</div>'
        '<h3 style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">Pro</h3>'
        '<div style="display: flex; align-items: baseline; justify-content: center; margin-bottom: 1rem;"><span style="color: #FFFFFF; font-size: 3rem; font-weight: 800;">$10</span><span style="color: #f8f8f8; font-size: 1.1rem; margin-left: 0.5rem;">/month</span></div>'
        '<p style="color: #f8f8f8; font-size: 0.9rem;">For professionals and small teams</p>'
        '<ul style="list-style: none; padding: 0; margin-bottom: 2rem;">'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Unlimited file uploads</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Advanced AI analysis (100 queries/day)</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Custom visualizations & charts</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Export reports (PDF, Excel)</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Priority email support</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Data dictionary management</li>'
        '</ul>'
        , unsafe_allow_html=True)
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    if st.button("Join Waitlist", key="pro_btn", use_container_width=True):
        st.session_state['scroll_to_contact'] = True
        st.rerun()
with col3:
    st.markdown('<div style="background: #35373b; border-radius: 16px; padding: 2.5rem; border: 2px solid #3a3d42; position: relative; display: flex; flex-direction: column; align-items: center;">'
        '<h3 style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">Enterprise</h3>'
        '<div style="display: flex; align-items: baseline; justify-content: center; margin-bottom: 1rem;"><span style="color: #FFFFFF; font-size: 3rem; font-weight: 800;">$99</span><span style="color: #f8f8f8; font-size: 1.1rem; margin-left: 0.5rem;">/month</span></div>'
        '<p style="color: #f8f8f8; font-size: 0.9rem;">For large organizations</p>'
        '<ul style="list-style: none; padding: 0; margin-bottom: 2rem;">'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Everything in Pro</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Unlimited AI queries</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Team collaboration features</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>API access & integrations</li>'
        '<li style="color: #f8f8f8; margin-bottom: 1rem; display: flex; align-items: center;"><span style="color: #4CAF50; margin-right: 0.5rem;">✓</span>Custom AI model training</li>'
        '<li style="color: #4CAF50; margin-right: 0.5rem;">✓</span>24/7 dedicated support</li>'
        '</ul>'
        , unsafe_allow_html=True)
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    if st.button("Contact Sales", key="enterprise_btn", use_container_width=True):
        st.session_state['scroll_to_contact'] = True
        st.rerun()

# --- Scroll handlers (run only if flag is set, then immediately reset) ---
if st.session_state.get('scroll_to_signup', False):
    st.session_state['scroll_to_signup'] = False
    st.markdown("""
        <script>
            setTimeout(function() {
                var expander = Array.from(document.querySelectorAll('.streamlit-expanderHeader')).find(e => e.textContent.includes('Sign Up'));
                if(expander){
                    expander.scrollIntoView({behavior: 'smooth'});
                }
            }, 300);
        </script>
    """, unsafe_allow_html=True)

if st.session_state.get('scroll_to_contact', False):
    st.session_state['scroll_to_contact'] = False
    st.markdown("""
        <script>
            setTimeout(function() {
                document.getElementById('contact').scrollIntoView({behavior: 'smooth'});
            }, 300);
        </script>
    """, unsafe_allow_html=True)

# ============================================================================
# CONTACT US SECTION
# ============================================================================
st.markdown('<div id="contact" style="padding: 4rem 0; background: #25282b; margin: 0 calc(-50vw + 50%); width: 100vw;"><div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem;"><div style="text-align: center; margin-bottom: 3rem;"><h1 style="color: #FFFFFF; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">Contact Us</h1><p style="color: #f8f8f8; font-size: 1.2rem; max-width: 600px; margin: 0 auto;">Get in touch with our team for support, questions, or partnership opportunities</p></div></div></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Send us a message")
    contact_form = st.form("contact_form")
    with contact_form:
        name = st.text_input("Full Name", key="contact_name")
        email = st.text_input("Email Address", key="contact_email")
        phone = st.text_input("Phone Number", key="contact_phone")
        subject = st.text_input("Subject", key="contact_subject")
        message = st.text_area("Message", height=150, key="contact_message")
        if st.form_submit_button("Send Message", use_container_width=True):
            if name and email and message:
                save_contact_query(name, email, phone, subject, message)
                st.success("Thank you for your message! We'll get back to you soon.")
            else:
                st.error("Please fill in all required fields (Name, Email, and Message).")
with col2:
    st.markdown('<div style="background: #35373b; border-radius: 16px; padding: 2.5rem; height: 100%;"><h3 style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin-bottom: 2rem;">Get in Touch</h3><div style="margin-bottom: 2rem;"><h4 style="color: #f8f8f8; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">📍 Address</h4><p style="color: #f8f8f8; line-height: 1.6;">New Delhi</p></div><div style="margin-bottom: 2rem;"><h4 style="color: #f8f8f8; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">📞 Phone</h4><p style="color: #f8f8f8; line-height: 1.6;">+91 9958929886</p></div><div style="margin-bottom: 2rem;"><h4 style="color: #f8f8f8; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">✉️ Email</h4><p style="color: #f8f8f8; line-height: 1.6;">insightsaisupport@circlebunch.com<br>chat@circlebunch.com</p></div><div><h4 style="color: #f8f8f8; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">🕒 Business Hours</h4><p style="color: #f8f8f8; line-height: 1.6;">Monday - Friday: 9:00 AM - 6:00 PM<br>Saturday: 10:00 AM - 4:00 PM<br>Sunday: Closed</p></div></div>', unsafe_allow_html=True)

# ============================================================================
# ABOUT US SECTION
# ============================================================================
st.markdown('<div id="about-us" style="padding: 4rem 0; background: #2d3035; margin: 0 calc(-50vw + 50%); width: 100vw;"><div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem;"><div style="text-align: center; margin-bottom: 4rem;"><h1 style="color: #FFFFFF; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">About Insights AI</h1><p style="color: #f8f8f8; font-size: 1.2rem; max-width: 800px; margin: 0 auto; line-height: 1.6;">We\'re revolutionizing how businesses and individuals interact with their data through the power of artificial intelligence.</p></div><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; margin-bottom: 4rem;"><div><h2 style="color: #FFFFFF; font-size: 2rem; font-weight: 700; margin-bottom: 1.5rem;">Our Mission</h2><p style="color: #f8f8f8; font-size: 1.1rem; line-height: 1.7; margin-bottom: 1.5rem;">At Insights AI, we believe that data analysis should be accessible to everyone, not just data scientists. Our mission is to democratize data insights by providing an intuitive, AI-powered platform that transforms complex data into clear, actionable intelligence.</p><p style="color: #f8f8f8; font-size: 1.1rem; line-height: 1.7;">Whether you\'re a business analyst, researcher, student, or entrepreneur, our platform empowers you to unlock the hidden patterns in your data and make informed decisions with confidence.</p></div><div style="background: #35373b; border-radius: 16px; padding: 2rem; text-align: center;"><div style="font-size: 4rem; margin-bottom: 1rem;">🎯</div><h3 style="color: #FFFFFF; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Data Democratization</h3><p style="color: #f8f8f8; font-size: 1rem; line-height: 1.6;">Making advanced data analysis accessible to everyone, regardless of technical background.</p></div></div><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 4rem;"><div style="background: #35373b; border-radius: 16px; padding: 2rem;"><div style="font-size: 2.5rem; margin-bottom: 1rem;">🤖</div><h3 style="color: #FFFFFF; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Advanced AI Technology</h3><p style="color: #f8f8f8; font-size: 1rem; line-height: 1.6;">Powered by cutting-edge machine learning algorithms and natural language processing, our AI understands your data context and provides intelligent analysis.</p></div><div style="background: #35373b; border-radius: 16px; padding: 2rem;"><div style="color: #FFFFFF; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">📊</div><h3 style="color: #FFFFFF; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Interactive Visualizations</h3><p style="color: #f8f8f8; font-size: 1rem; line-height: 1.6;">Create stunning, interactive charts and graphs that bring your data to life. Export and share insights with your team effortlessly.</p></div><div style="background: #35373b; border-radius: 16px; padding: 2rem;"><div style="font-size: 2.5rem; margin-bottom: 1rem;">🔒</div><h3 style="color: #FFFFFF; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Secure & Private</h3><p style="color: #f8f8f8; font-size: 1rem; line-height: 1.6;">Your data security is our top priority. All data is encrypted, processed securely, and never shared with third parties.</p></div></div><div style="background: #35373b; border-radius: 16px; padding: 3rem; text-align: center;"><h2 style="color: #FFFFFF; font-size: 2rem; font-weight: 700; margin-bottom: 1.5rem;">What Makes Us Different</h2><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-top: 2rem;"><div><h4 style="color: #FFFFFF; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Natural Language Interface</h4><p style="color: #f8f8f8; font-size: 0.95rem;">Ask questions about your data in plain English and get intelligent responses</p></div><div><h4 style="color: #f8f8f8; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Smart Data Dictionary</h4><p style="color: #f8f8f8; font-size: 0.95rem;">Automatically understand your data structure and context</p></div><div><h4 style="color: #FFFFFF; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Real-time Collaboration</h4><p style="color: #f8f8f8; font-size: 0.95rem;">Share insights and collaborate with your team in real-time</p></div><div><h4 style="color: #FFFFFF; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Custom AI Training</h4><p style="color: #f8f8f8; font-size: 0.95rem;">Train AI models on your specific domain and use cases</p></div></div></div><div style="text-align: center; margin-top: 4rem;"><h2 style="color: #FFFFFF; font-size: 2rem; font-weight: 700; margin-bottom: 1rem;">Join Thousands of Users</h2><p style="color: #f8f8f8; font-size: 1.1rem; margin-bottom: 2rem;">From startups to Fortune 500 companies, organizations worldwide trust Insights AI to transform their data into actionable insights.</p><button style="background: #f8f8f8; color: #25282b; border: none; border-radius: 8px; padding: 1rem 2rem; font-weight: 600; font-size: 1.1rem; cursor: pointer; transition: all 0.3s ease;">Start Your Free Trial</button></div></div></div>', unsafe_allow_html=True)

# Example: Only show debug section if debug_info exists and is not empty
if 'debug_info' in st.session_state and st.session_state['debug_info']:
    st.markdown("""
        <div style='text-align:center; margin:2rem 0;'>
            <h2 style='font-size:2rem; font-weight:800; color:#e6eaf3; margin-bottom:1rem;'>Debug</h2>
            <div style='background:#2d3035; color:#f8f8f8; border-radius:12px; padding:1.5rem; display:inline-block; min-width:300px;'>
                {} 
            </div>
        </div>
    """.format(st.session_state['debug_info']), unsafe_allow_html=True)