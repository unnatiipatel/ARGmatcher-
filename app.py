import streamlit as st
import pandas as pd

st.title("🧬 ARGmatcher - BLAST Results Viewer")

uploaded_file = st.file_uploader("📄 Upload your BLAST results file (.txt)", type="txt")

if uploaded_file:
    columns = ["query_id", "subject_id", "identity", "alignment_length", "mismatches", "gap_opens",
               "q_start", "q_end", "s_start", "s_end", "evalue", "bit_score"]

    df = pd.read_csv(uploaded_file, sep="\t", names=columns)

    st.subheader("📋 Raw BLAST Results")
    st.dataframe(df)

    st.subheader("🎯 Filter Options")
    identity_filter = st.slider("Minimum Identity (%)", 0, 100, 70)
    evalue_filter = st.number_input("Maximum e-value", value=1e-5, format="%.1e")

    filtered = df[(df['identity'] >= identity_filter) & (df['evalue'] <= evalue_filter)]

    st.subheader("✅ Filtered ARG Hits")
    st.dataframe(filtered)

    st.download_button("⬇️ Download Filtered Results",
                       filtered.to_csv(index=False), "filtered_results.csv", "text/csv")
