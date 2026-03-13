import streamlit as st
import pandas as pd
import re
from datetime import datetime

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Gainesville Lead Auditor", page_icon="🧹")
st.title("Gainesville Lead Audit & Data Cleaning")

# --- 1. THE PRANK & PROFANITY BLACKLIST ---
# This catches partial matches like "Hugh Janus" or "Janus Roofing"
BAD_WORDS = [
    "fuck", "shit", "ass", "balls", "janus", "seymour", "butts", "dover", 
    "muncher", "penis", "vagina", "pussy", "dick", "cock", "anal", "weed", 
    "boner", "skeet", "jizz", "tits", "clit", "philo", "mycrack", "kock", "janis"
]

# Common phonetic prank combinations
PRANK_COMBOS = ["ben dover", "eileen ulick", "barry mc", "mike litoris", "hugh j"]

# --- 2. THE SCRUBBING ENGINE ---
def is_garbage_row(row):
    """Scans the entire row for pranks, gibberish, or bad formatting."""
    # Combine the whole row into one string for a deep scan
    full_row_text = " ".join(row.astype(str)).lower()
    
    # Check Blacklist
    if any(word in full_row_text for word in BAD_WORDS):
        return True
    
    # Check Prank Combos
    if any(combo in full_row_text for combo in PRANK_COMBOS):
        return True
        
    # Check for Gibberish (6+ consonants in a row like 'asdfghj')
    if re.search(r'[bcdfghjklmnpqrstvwxyz]{6,}', full_row_text):
        return True
        
    return False

def validate_phones(df):
    """Finds phone column and flags fakes like 123-456-7890."""
    phone_col = next((c for c in df.columns if 'phone' in c.lower() or 'cell' in c.lower()), None)
    if not phone_col:
        return pd.Series([False] * len(df))
    
    def is_bad_number(phone):
        digits = re.sub(r'\D', '', str(phone))
        if len(digits) == 11 and digits.startswith('1'): digits = digits[1:]
        if len(digits) != 10: return True
        # Area code check: Fakes often start with 0, 1, or 123
        if digits[0] in ['0', '1'] or digits.startswith('123'): return True
        return False
        
    return df[phone_col].apply(is_bad_number)

# --- 3. THE UI WORKFLOW ---
uploaded_file = st.file_uploader("Step 1: Upload Master Lead List (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Run the filters
    is_prank_row = df.apply(is_garbage_row, axis=1)
    is_bad_phone = validate_phones(df)
    
    # Combine masks: Row is garbage if it's a prank OR has a bad phone
    garbage_mask = is_prank_row | is_bad_phone
    gold_df = df[~garbage_mask].copy()

    # --- RESULTS DASHBOARD ---
    st.divider()
    st.subheader("📊 Audit Diagnostic Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Leads Scanned", len(df))
    col2.metric("Garbage Removed", garbage_mask.sum(), delta_color="inverse")
    col3.metric("Verified Gold", len(gold_df))

    st.success(f"Audit Complete! We protected your brand by removing {garbage_mask.sum()} risky or fake leads.")

    # --- THE DOWNLOAD BUTTON ---
    st.divider()
    st.subheader("Step 2: Download Your Gold List")
    
    # Convert Gold DF to CSV
    csv_data = gold_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download Cleaned CSV (All Columns Preserved)",
        data=csv_data,
        file_name=f"Gold_List_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

    st.write("### Data Preview (Top 10 Cleaned Leads):")
    st.dataframe(gold_df.head(10))
