import streamlit as st
import pandas as pd
import subprocess
import os
import uuid

# Constants
DB_PATH = os.path.expanduser("~/Documents/ARG_db/amr_db")

st.title("🧬 ARG Detector Tool")
st.markdown("This tool detects Antibiotic Resistance Genes (ARGs) from DNA sequences using BLASTX.")

# --- INPUT METHOD ---
input_method = st.radio("Choose input method:", ["Upload FASTA file", "Paste DNA sequence"])

if input_method == "Upload FASTA file":
    uploaded_file = st.file_uploader("Upload your FASTA file", type=["fasta", "fa"])
    if uploaded_file:
        fasta_path = f"input_{uuid.uuid4().hex[:8]}.fasta"
        with open(fasta_path, "wb") as f:
            f.write(uploaded_file.read())

elif input_method == "Paste DNA sequence":
    sequence = st.text_area("Paste your DNA sequence here:")
    if sequence:
        fasta_path = f"input_{uuid.uuid4().hex[:8]}.fasta"
        with open(fasta_path, "w") as f:
            f.write(">pasted_sequence\n")
            f.write(sequence)

# --- RUN BLAST ---
if 'fasta_path' in locals() and st.button("🔍 Run ARG Detection"):
    result_file = fasta_path.replace(".fasta", "_results.txt")

    st.info("Running BLASTX... please wait")
    blast_command = [
        "blastx",
        "-query", fasta_path,
        "-db", DB_PATH,
        "-out", result_file,
        "-evalue", "1e-3",
        "-outfmt", "6",
        "-max_target_seqs", "20"
    ]
    try:
        subprocess.run(blast_command, check=True)
    except subprocess.CalledProcessError as e:
        st.error("BLASTX failed. Make sure NCBI BLAST+ is installed and configured.")
        st.stop()

    # --- READ RESULTS ---
    cols = ['query_id', 'subject_id', 'identity', 'length', 'mismatches', 'gap_opens',
            'q_start', 'q_end', 's_start', 's_end', 'evalue', 'bit_score']
    try:
        df = pd.read_csv(result_file, sep="\t", names=cols)
    except Exception as e:
        st.error("Failed to read BLAST result file.")
        st.stop()

    if df.empty:
        st.warning("No matches found.")
    else:
        # Ask for filtering thresholds
        st.subheader("📊 Filter Results")
        identity_thresh = st.slider("Minimum % Identity", 0, 100, 70)
        evalue_thresh = st.number_input("Maximum E-value", value=1e-5, format="%e")

        df_filtered = df[(df["identity"] >= identity_thresh) & (df["evalue"] <= evalue_thresh)].copy()

        # Parse gene/family name from subject_id
        df_filtered['gene'] = df_filtered['subject_id'].str.split('|').str[4]
        df_filtered['family'] = df_filtered['subject_id'].str.split('|').str[5]

        st.success(f"🔍 Found {len(df_filtered)} filtered matches")
        st.dataframe(df_filtered[['gene', 'family', 'identity', 'evalue']])

        # Save filtered results
        csv_output = fasta_path.replace(".fasta", "_filtered.csv")
        df_filtered.to_csv(csv_output, index=False)
        st.download_button("📥 Download CSV Results", data=open(csv_output, 'rb').read(), file_name=os.path.basename(csv_output))

        # Optional plots
        st.subheader("📈 Identity vs E-value")
        st.scatter_chart(df_filtered[['identity', 'evalue']])
