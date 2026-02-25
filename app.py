import streamlit as st
import pandas as pd
import re
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import io

st.title("🌴 Florida Real Estate Lead Auditor")

# 1. Clear Instructions
st.markdown("""
### 🚀 How to use this tool:
1. Export your leads from your CRM as a **CSV** or **Excel** file.
2. Ensure your file has these 3 column headers: **Name**, **Email**, and **Phone**.
3. Drag and drop the file below to start the AI Audit.
""")

# 2. Add a Sample Template (so they can't fail)
sample_data = pd.DataFrame({
    'Name': ['Jane Smith', 'ALACHUA_BOT'],
    'Email': ['jane@gmail.com', 'bot@test.ru'],
    'Phone': ['352-555-0199', '0000000000']
})
st.download_button(
    label="📥 Download Example Format",
    data=sample_data.to_csv(index=False).encode('utf-8'),
    file_name="lead_audit_template.csv",
    mime="text/csv",
)

st.divider() # Visual separator

# 3. File Uploader with Error Handling
uploaded_file = st.file_uploader("Upload Lead List", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    # --- SAFETY CHECK ---
    required = ['Name', 'Email', 'Phone']
    missing = [c for c in required if c not in df.columns]
    
    if missing:
        st.error(f"❌ **Upload Failed:** Your file is missing these columns: {', '.join(missing)}")
        st.info("Please rename your columns to match the template and try again.")
        st.stop() # Prevents the AI model from running and crashing
    
    # ... rest of your AI logic continues here ...

# 1. PAGE SETUP
st.set_page_config(page_title="Florida Lead Auditor", page_icon="🌴")
st.title("🌴 Florida Real Estate Lead Auditor")
st.markdown("Upload your messy CSV/Excel and let the AI find the junk.")

# 2. FILE UPLOADER
uploaded_file = st.file_uploader("Upload Lead List", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write(f"Loaded {len(df)} records.")

    # 3. CLEANING ENGINE (Your Step 2/4)
    df['Phone_Cleaned'] = df['Phone'].astype(str).apply(lambda x: re.sub(r'\D', '', x))
    df['name_len'] = df['Name'].astype(str).apply(len)
    df['phone_len'] = df['Phone_Cleaned'].apply(len)
    
    le = LabelEncoder()
    df['domain_id'] = le.fit_transform(df['Email'].astype(str).str.split('@').str[-1].fillna('none'))

    # 4. AI MODEL (Your Step 5/6)
    features = ['name_len', 'phone_len', 'domain_id']
    model = IsolationForest(contamination=0.20, random_state=42)
    df['anomaly_score'] = model.fit_predict(df[features])
    df['Quality_Label'] = df['anomaly_score'].map({1: '✅ Good', -1: '🚩 Junk/Bot'})

    # Hard Rules & Blacklist
    blacklist = ['BOT', 'TEST', 'FAKE']
    df.loc[df['Name'].str.contains('|'.join(blacklist), case=False, na=False), 'Quality_Label'] = '🚩 Junk/Bot'
    df.loc[df['phone_len'] < 10, 'Quality_Label'] = '🚩 Junk/Bot'

    # Force-flag known bot signatures or bad phone lengths
    blacklist = ['BOT', 'TEST', 'FAKE']
    is_bot = df['Name'].str.contains('|'.join(blacklist), case=False, na=False)
    is_bad_phone = df['phone_len'] < 10

    # This override ensures they NEVER end up in the 'Good' pile
    df.loc[is_bot | is_bad_phone, 'Quality_Label'] = '🚩 Junk/Bot'

    # 5. DISPLAY RESULTS
    st.subheader("Audit Preview")
    st.dataframe(df[['Name', 'Email', 'Phone', 'Quality_Label']].head(10))

    # 6. EXPORT TO EXCEL (Your Step 8)
    # We use a buffer to allow the user to download the file directly
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df[df['Quality_Label'] == '✅ Good'].to_excel(writer, sheet_name='READY_TO_CALL', index=False)
        df[df['Quality_Label'] == '🚩 Junk/Bot'].to_excel(writer, sheet_name='REVIEW_REQUIRED', index=False)
    
    st.download_button(
        label="📥 Download Cleaned Audit (.xlsx)",
        data=output.getvalue(),
        file_name="Lead_Audit_Results.xlsx",
        mime="application/vnd.ms-excel"

    )


