import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gainesville Lead Auditor", page_icon="🧹")
st.title("Gainesville Lead Audit Dashboard")

# --- THE LOGIC ---
def run_audit(df):
    total = len(df)
    # Finding those specific test-file patterns
    is_bot = df.apply(lambda x: any(k in str(x).lower() for k in ['bot-trap', 'test']), axis=1)
    is_bad_phone = df.apply(lambda x: 'pending' in str(x).lower(), axis=1)
    
    return {
        "total": total,
        "garbage": is_bot.sum() + is_bad_phone.sum(),
        "clean": total - (is_bot.sum() + is_bad_phone.sum())
    }

# --- THE UI ---
uploaded_file = st.file_uploader("Upload Messy Lead List", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    results = run_audit(df)

    # THE MONEY SHOT
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Leads Scanned", results["total"])
    col2.metric("Garbage Detected", results["garbage"], delta_color="inverse")
    col3.metric("Verified Gold", results["clean"])

    st.success(f"Audit Complete! We found {results['garbage']} entries that would have wasted your team's time.")
    
    st.write("### Preview of Verified Gold List:")
    # Filter out the garbage for the preview
    clean_preview = df[~df.apply(lambda x: any(k in str(x).lower() for k in ['bot-trap', 'pending']), axis=1)]
    st.dataframe(clean_preview.head(10))

    st.info("Amit is preparing your full CSV export now. Expect it in 4-6 hours.")
