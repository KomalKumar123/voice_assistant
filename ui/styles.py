import streamlit as st


def inject_styles():
    """
    Injects the full custom CSS for the Road Asset Analytics Assistant.
    Dark theme, glassmorphism cards, gradient header, premium typography.
    """
    st.markdown(
        """
        <style>
        /* ============================================================
           IMPORT FONTS
        ============================================================ */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ============================================================
           ROOT VARIABLES
        ============================================================ */
        :root {
            --bg-primary:      #0d1117;
            --bg-secondary:    #161b22;
            --bg-card:         rgba(22, 27, 34, 0.85);
            --accent-primary:  #2ea043;
            --accent-secondary:#388bfd;
            --accent-warning:  #d29922;
            --accent-danger:   #f85149;
            --text-primary:    #e6edf3;
            --text-secondary:  #8b949e;
            --text-muted:      #484f58;
            --border-color:    rgba(48, 54, 61, 0.8);
            --glow-green:      rgba(46, 160, 67, 0.3);
            --glow-blue:       rgba(56, 139, 253, 0.3);
            --radius-sm:       8px;
            --radius-md:       12px;
            --radius-lg:       16px;
            --radius-xl:       24px;
            --shadow-sm:       0 1px 3px rgba(0,0,0,0.4);
            --shadow-md:       0 4px 16px rgba(0,0,0,0.5);
            --shadow-lg:       0 8px 32px rgba(0,0,0,0.6);
            --transition:      all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* ============================================================
           GLOBAL RESET & BODY
        ============================================================ */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Hide Streamlit branding */
        #MainMenu, footer, header { visibility: hidden; }
        [data-testid="stToolbar"] { display: none; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-secondary); }
        ::-webkit-scrollbar-thumb {
            background: var(--text-muted);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }

        /* ============================================================
           SIDEBAR
        ============================================================ */
        [data-testid="stSidebar"] {
            background: var(--bg-secondary) !important;
            border-right: 1px solid var(--border-color) !important;
        }

        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown li,
        [data-testid="stSidebar"] label {
            color: var(--text-secondary) !important;
            font-size: 0.85rem;
        }

        /* ============================================================
           HERO HEADER
        ============================================================ */
        .raa-hero {
            background: linear-gradient(135deg, #0d1117 0%, #0d2818 40%, #0a1628 100%);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-xl);
            padding: 2.5rem 2rem 2rem 2rem;
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
        }
        .raa-hero::before {
            content: '';
            position: absolute;
            top: -60px; right: -60px;
            width: 220px; height: 220px;
            background: radial-gradient(circle, var(--glow-green) 0%, transparent 70%);
            pointer-events: none;
        }
        .raa-hero::after {
            content: '';
            position: absolute;
            bottom: -40px; left: 30%;
            width: 180px; height: 180px;
            background: radial-gradient(circle, var(--glow-blue) 0%, transparent 70%);
            pointer-events: none;
        }
        .raa-hero h1 {
            font-size: 1.9rem !important;
            font-weight: 700 !important;
            background: linear-gradient(90deg, #2ea043, #388bfd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 0.4rem 0 !important;
            letter-spacing: -0.02em;
        }
        .raa-hero p {
            color: var(--text-secondary) !important;
            font-size: 0.95rem;
            margin: 0;
            font-weight: 400;
        }
        .raa-hero .badge {
            display: inline-block;
            background: rgba(46,160,67,0.15);
            border: 1px solid rgba(46,160,67,0.4);
            color: #2ea043;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 20px;
            margin-bottom: 0.8rem;
        }

        /* ============================================================
           GLASS CARDS
        ============================================================ */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-md);
            transition: var(--transition);
        }
        .glass-card:hover {
            border-color: rgba(46,160,67,0.4);
            box-shadow: var(--shadow-lg), 0 0 20px var(--glow-green);
            transform: translateY(-1px);
        }

        /* ============================================================
           DATASET CARDS (sidebar)
        ============================================================ */
        .dataset-card {
            background: rgba(46,160,67,0.08);
            border: 1px solid rgba(46,160,67,0.3);
            border-radius: var(--radius-md);
            padding: 0.9rem 1rem;
            margin-bottom: 0.6rem;
            transition: var(--transition);
        }
        .dataset-card:hover {
            background: rgba(46,160,67,0.14);
            border-color: rgba(46,160,67,0.6);
        }
        .dataset-card .ds-name {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        .dataset-card .ds-id {
            font-size: 0.72rem;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }
        .dataset-card .ds-sheet {
            font-size: 0.75rem;
            color: var(--text-secondary);
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            padding: 1px 6px;
            margin: 2px 2px 0 0;
            display: inline-block;
        }

        /* ============================================================
           QUERY INTENT CARD
        ============================================================ */
        .intent-card {
            background: rgba(56,139,253,0.08);
            border: 1px solid rgba(56,139,253,0.3);
            border-radius: var(--radius-md);
            padding: 0.9rem 1.1rem;
            font-size: 0.82rem;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }
        .intent-card .intent-label {
            font-size: 0.7rem;
            color: #388bfd;
            font-weight: 600;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        /* ============================================================
           CHAT BUBBLES
        ============================================================ */
        .chat-user-bubble {
            background: rgba(56,139,253,0.12);
            border: 1px solid rgba(56,139,253,0.3);
            border-radius: var(--radius-md) var(--radius-md) 4px var(--radius-md);
            padding: 0.85rem 1.1rem;
            margin: 0.5rem 0;
            font-size: 0.92rem;
            color: var(--text-primary);
            max-width: 85%;
            margin-left: auto;
        }
        .chat-assistant-bubble {
            background: rgba(46,160,67,0.08);
            border: 1px solid rgba(46,160,67,0.25);
            border-radius: var(--radius-md) var(--radius-md) var(--radius-md) 4px;
            padding: 0.85rem 1.1rem;
            margin: 0.5rem 0;
            font-size: 0.92rem;
            color: var(--text-primary);
            max-width: 85%;
        }
        .chat-timestamp {
            font-size: 0.68rem;
            color: var(--text-muted);
            margin-top: 4px;
            font-family: 'JetBrains Mono', monospace;
        }

        /* ============================================================
           STATUS BADGES
        ============================================================ */
        .status-online {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 0.75rem;
            color: #2ea043;
            font-weight: 500;
        }
        .status-online::before {
            content: '';
            width: 6px; height: 6px;
            border-radius: 50%;
            background: #2ea043;
            box-shadow: 0 0 6px #2ea043;
            animation: pulse-dot 2s infinite;
        }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50%       { opacity: 0.4; }
        }

        /* ============================================================
           BUTTONS
        ============================================================ */
        .stButton > button {
            background: linear-gradient(135deg, #238636, #2ea043) !important;
            color: #fff !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            padding: 0.55rem 1.2rem !important;
            transition: var(--transition) !important;
            box-shadow: 0 2px 8px rgba(46,160,67,0.35) !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #2ea043, #3fb950) !important;
            box-shadow: 0 4px 16px rgba(46,160,67,0.55) !important;
            transform: translateY(-1px) !important;
        }

        /* ============================================================
           INPUTS
        ============================================================ */
        .stTextInput > div > div > input,
        .stTextArea textarea {
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
            padding: 0.6rem 0.9rem !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {
            border-color: rgba(56,139,253,0.6) !important;
            box-shadow: 0 0 0 3px rgba(56,139,253,0.15) !important;
            outline: none !important;
        }

        /* ============================================================
           SLIDERS
        ============================================================ */
        .stSlider [data-baseweb="slider"] div[role="slider"] {
            background: var(--accent-primary) !important;
        }

        /* ============================================================
           FILE UPLOADER
        ============================================================ */
        [data-testid="stFileUploader"] {
            border: 2px dashed var(--border-color) !important;
            border-radius: var(--radius-lg) !important;
            background: var(--bg-secondary) !important;
            transition: var(--transition) !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: rgba(46,160,67,0.5) !important;
            background: rgba(46,160,67,0.05) !important;
        }

        /* ============================================================
           EXPANDERS
        ============================================================ */
        [data-testid="stExpander"] {
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            background: var(--bg-secondary) !important;
            margin-top: 0.5rem;
        }
        [data-testid="stExpander"] summary {
            color: var(--text-secondary) !important;
            font-size: 0.85rem !important;
        }

        /* ============================================================
           CODE BLOCKS
        ============================================================ */
        pre, code {
            font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
            background: #0d1117 !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-sm) !important;
            font-size: 0.82rem !important;
        }

        /* ============================================================
           METRICS / KPIs
        ============================================================ */
        .kpi-row {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }
        .kpi-card {
            flex: 1;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 0.9rem 1.1rem;
            text-align: center;
        }
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--accent-primary);
        }
        .kpi-label {
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-top: 2px;
        }

        /* ============================================================
           SECTION HEADERS
        ============================================================ */
        .section-header {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 1.2rem 0 0.6rem 0;
            padding-bottom: 0.4rem;
            border-bottom: 1px solid var(--border-color);
        }

        /* ============================================================
           DIVIDER
        ============================================================ */
        hr {
            border-color: var(--border-color) !important;
            margin: 1rem 0 !important;
        }

        /* ============================================================
           ALERTS
        ============================================================ */
        [data-testid="stAlert"] {
            border-radius: var(--radius-md) !important;
            border: none !important;
        }

        /* Audio player */
        audio {
            width: 100%;
            border-radius: var(--radius-sm);
            margin-top: 0.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
