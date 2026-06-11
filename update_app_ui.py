import os

filepath = r'c:\Users\USER\Desktop\Final Year Project\timetable_project\app_ui.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Unhide MainMenu to restore settings dots
old_hidden = '''#MainMenu, footer {
    visibility: hidden !important;
}'''
new_hidden = '''footer {
    visibility: hidden !important;
}
/* Ensure the toolbar/MainMenu stays visible for settings icon */
[data-testid="stToolbar"], #MainMenu {
    visibility: visible !important;
}'''
content = content.replace(old_hidden, new_hidden)

# 2. Upgrade the sidebar buttons to look professional (SaaS-style edge highlight)
old_sidebar_css = '''section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding-left: 16px !important;
    border-radius: var(--radius-md) !important;
    height: 44px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: var(--transition) !important;
    margin-bottom: 2px !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: var(--accent-subtle) !important;
    border-color: var(--border-accent) !important;
    color: var(--accent-hover) !important;
}'''

new_sidebar_css = '''section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    color: var(--text-secondary) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding-left: 20px !important;
    border-radius: 0 !important;
    height: 42px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
    margin-bottom: 4px !important;
    width: 100% !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: linear-gradient(90deg, rgba(20,184,166,0.1) 0%, transparent 100%) !important;
    border-left: 3px solid var(--accent) !important;
    color: var(--text-primary) !important;
}
/* Specifically for disabled buttons in sidebar to look faded but consistent */
section[data-testid="stSidebar"] .stButton button:disabled {
    opacity: 0.4 !important;
    cursor: not-allowed !important;
}'''

content = content.replace(old_sidebar_css, new_sidebar_css)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated sidebar CSS and unhid MainMenu.')
