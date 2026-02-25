import streamlit as st
import pandas as pd
import re
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import io

# 1. PAGE SETUP - This must be the very first Streamlit command
st.set_page_config(page_title="Florida Lead Auditor", page_icon="🌴")

st.title("🌴 Florida Real Estate Lead Auditor")

# 2. CLEAR INSTRUCTIONS
st.markdown("""
### 🚀 How to use this tool:
1. Export your leads from your CRM as a **CSV** or **Excel** file.
2. Ensure your file has these 3 column headers: **Name**, **Email**, and **Phone**.
3. Drag and drop the file below to start the AI Audit.
""")

# 3. SAMPLE TEMPLATE
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

st.divider()

# 4. FILE UPLOADER
uploaded_file = st.file_uploader("Upload Lead List", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # --- SAFETY CHECK ---
    required = ['Name', 'Email', 'Phone']
    missing = [c for c in required if c not in df.columns]
    
    if missing:
        st.error(f"❌ **Upload Failed:** Your file is missing these columns: {', '.join(missing)}")
        st.info("Please rename your columns to match the template and try again.")
        st.stop() 

    st.write(f"✅ Successfully loaded {len(df)} records.")

    # 5. CLEANING ENGINE
    df['Phone_Cleaned'] = df['Phone'].astype(str).apply(lambda x: re.sub(r'\D', '', x))
    df['name_len'] = df['Name'].astype(str).apply(len)
    df['phone_len'] = df['Phone_Cleaned'].apply(len)
    
    le = LabelEncoder()
    df['domain_id'] = le.fit_transform(df['Email'].astype(str).str.split('@').str[-1].fillna('none'))

    # 6. AI MODEL (Isolation Forest)
    features = ['name_len', 'phone_len', 'domain_id']
    model = IsolationForest(contamination=0.20, random_state=42)
    df['anomaly_score'] = model.fit_predict(df[features])
    df['Quality_Label'] = df['anomaly_score'].map({1: '✅ Good', -1: '🚩 Junk/Bot'})

    # 7. HARD RULES & BLACKLIST OVERRIDE
    blacklist = ['BOT', 'TEST', 'FAKE']
    is_bot = df['Name'].str.contains('|'.join(blacklist), case=False, na=False)
    is_bad_phone = df['phone_len'] < 10

    # This override ensures bots and bad phones never end up in the 'Good' pile
    df.loc[is_bot | is_bad_phone, 'Quality_Label'] = '🚩 Junk/Bot'

    # 8. DISPLAY RESULTS
    st.subheader("Audit Preview")
    st.dataframe(df[['Name', 'Email', 'Phone', 'Quality_Label']].head(10))

    # 9. EXPORT TO EXCEL
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
