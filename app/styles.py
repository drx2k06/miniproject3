"""Custom CSS styling and visual design components for QuantPulse."""
from __future__ import annotations

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg-main: #0B1118;
    --bg-card: #121B24;
    --bg-card-hover: #16222E;
    --border-color: #1F2E3D;
    --text-primary: #F1F5F9;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --accent-green: #10B981;
    --accent-red: #EF4444;
    --accent-amber: #F59E0B;
    --accent-blue: #3B82F6;
    --accent-purple: #8B5CF6;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}

.stApp {
    background-color: var(--bg-main);
    color: var(--text-primary);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #0E1620;
    border-right: 1px solid var(--border-color);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1440px;
}

/* Header brand mark */
.brand-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
}

.brand-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #10B981, #059669);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.brand-title {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--text-primary);
}

.brand-subtitle {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text-muted);
    font-weight: 700;
}

/* Metric Cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 20px;
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.metric-card:hover {
    border-color: #2D4257;
    transform: translateY(-2px);
}

.metric-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
}

.metric-value {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--text-primary);
    margin-top: 6px;
}

.metric-sub {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* Signal Hero Box */
.signal-hero {
    background: linear-gradient(145deg, #132220 0%, #0D1917 100%);
    border: 1px solid #1C3831;
    border-radius: 16px;
    padding: 24px 28px;
    position: relative;
    overflow: hidden;
}

.signal-hero::after {
    content: '';
    position: absolute;
    top: -50px;
    right: -50px;
    width: 160px;
    height: 160px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%);
    border-radius: 50%;
}

.signal-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.pill-green {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.pill-amber {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.pill-red {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Content Container Cards */
.panel-box {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
}

.panel-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
}

.panel-caption {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 16px;
}

/* Streamlit button customizations */
div[data-testid="stButton"] button {
    background: #10B981 !important;
    color: #062319 !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] button:hover {
    background: #059669 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
}

/* Tab styling */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 13px !important;
    color: var(--text-secondary) !important;
}

button[aria-selected="true"] {
    color: #10B981 !important;
    border-bottom-color: #10B981 !important;
}
</style>
"""
