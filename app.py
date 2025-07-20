import streamlit as st
import subprocess
import pandas as pd
import uuid
import os

st.title("🧬 ARGmatcher: Detect ARGs from Protein Sequences")

# Input section
seq_input = st.text_area("Paste your protein sequence (FASTA format or raw sequence)", height=200)

# BLAST database path (ensure this matches your repo setup on Streamlit Cloud)
DB_PATH = "amr_db"  # Ensure the DB files (amr_db.*) are uploaded alongside app.py

if st.button("🔍 Run ARG Detection"):
    if not seq_input.strip():
        st.error("❗ Please enter a valid protein sequence.")
    else:
        # Ensure FASTA format
        if not seq_input.startswith(">"):
            seq_input = f">query\n{seq_input.strip()}"

        # Save input to a temp file
        input_id = str(uuid.uuid4())[:8]
        input_file = f"input_{input_id}.fasta"
        result_file = f"result_{input_id}.txt"

        with open(input_file, "w") as f:
            f.write(seq_input)

        # Run BLASTP
        blast_cmd = [
            "blastp",
            "-query", input_file,
            "-db", DB_PATH,
            "-out", result_file,
            "-evalue", "1e-3",
            "-outfmt", "6",
            "-max_target_seqs", "25"
        ]

        try:
            subprocess.run(blast_cmd, check=True)

            # Parse result
            columns = ["query_id", "subject_id", "identity", "alignment_length", "mismatches", "gap_opens",
                       "q_start", "q_end", "s_start", "s_end", "evalue", "bit_score"]
            df = pd.read_csv(result_file, sep="\t", names=columns)

            if df.empty:
                st.warning("⚠️ No significant matches found.")
            else:
                st.success("✅ Matches found! Showing top results:")

                # Extract gene name and family from subject_id
                df['gene'] = df['subject_id'].str.split("|").str[4]
                df['family'] = df['subject_id'].str.split("|").str[5]
                display_df = df[['gene', 'family', 'identity', 'evalue']].copy()

                st.dataframe(display_df)

                # Optional filters
                st.markdown("### 🔎 Optional: Filter your results")
                id_threshold = st.slider("Minimum % identity", 0, 100, 70)
                evalue_thresh = st.text_input("Maximum E-value", "1e-5")

                try:
                    filtered = display_df[
                        (display_df["identity"] >= id_threshold) &
                        (display_df["evalue"] <= float(evalue_thresh))
                    ]
                    st.markdown("### 🎯 Filtered Hits:")
                    st.dataframe(filtered)
                except ValueError:
                    st.warning("⚠️ Invalid E-value format.")

        except subprocess.CalledProcessError as e:
            st.error("❌ BLAST execution failed. Make sure `blastp` is available and database is correctly uploaded.")
            st.text(e)
        finally:
            # Cleanup
            os.remove(input_file)
            if os.path.exists(result_file):
                os.remove(result_file)
