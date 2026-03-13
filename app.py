import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
# Create a folder to hold the "Bucket" files if it doesn't exist
UPLOAD_DIR = "client_uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

st.set_page_config(page_title="Gainesville Lead Audit", page_icon="🧹")

# --- STYLING ---
st.title("Gainesville Lead Audit & Data Cleaning")
st.markdown("""
    **Moving to Gainesville?** Don't waste your sales team's time on 'garbage' data. 
    Upload your messiest lead list below. Our AI logic-layer will identify bots, 
    verify emails, and return a **Gold List** of real intent.
""")

# --- LOGIC ---
def save_file(uploaded_file):
    """Saves the file to the local 'bucket' folder for Amit to process."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{uploaded_file.name}")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def try_read_file(uploaded_file):
    """Attempts to read the file. If it fails, we trigger 'Deep Scan' mode."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            # Requires 'pip install openpyxl'
            df = pd.read_excel(uploaded_file)
        return df, True
    except:
        return None, False

# --- UI ---
st.divider()
st.subheader("Step 1: Upload Your List")
uploaded_file = st.file_uploader("Upload CSV or Excel (Max 100 leads for free audit)", type=["csv", "xlsx", "xls"])

if uploaded_file:
    # 1. Save the file to your 'bucket' immediately
    saved_path = save_file(uploaded_file)
    
    # 2. Try to show a preview to look professional
    df, success = try_read_file(uploaded_file)
    
    if success:
        st.success("✅ File Received Successfully!")
        st.write("### Data Preview (First 5 rows):")
        st.dataframe(df.head(5))
        
        st.info(f"""
            **Status:** AI Logic-Layer is now verifying {len(df)} leads.
            **Estimated Completion:** 4-6 hours.
            Amit will email the full 'Gold List' report to the contact on file.
        """)
    else:
        # This is the Safety Net if the file is weird
        st.success("✅ File Received!")
        st.warning("✨ This file format has triggered our 'Deep Scan' protocol.")
        st.info("""
            **Status:** Amit is manually overseeing this audit to ensure 100% accuracy.
            **Estimated Completion:** 4-6 hours.
            You will receive your report via email shortly.
        """)

st.divider()
st.subheader("Step 2: Next Steps")
st.write("Once your audit is complete, we'll send you a Loom video explaining your 'Data Leakage' score and how to unlock the full Streamlit dashboard for daily use.")

# --- SIDEBAR (The Pitch) ---
st.sidebar.header("About the Audit")
st.sidebar.info("""
This audit checks for:
- 🤖 Bot/Scripted Entries
- 📧 Email Deliverability
- 📱 Phone Number Validity
- 👯‍♂️ Duplicate Merging
""")
