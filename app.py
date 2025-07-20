import pandas as pd

# Ask user for the results file name
file_name = input("📂 Enter your BLAST results file name (e.g., results.txt): ").strip()

# BLAST outfmt 6 columns
columns = [
    'query_id', 'subject_id', 'identity', 'length', 'mismatches', 'gap_opens',
    'q_start', 'q_end', 's_start', 's_end', 'evalue', 'bit_score'
]

try:
    # Read and parse the results
    df = pd.read_csv(file_name, sep="\t", names=columns)

    # Filter hits
    df_filtered = df[(df["identity"] > 70) & (df["evalue"] < 1e-5)]

    # Extract ARG gene and family from subject_id
    df_filtered["gene"] = df_filtered["subject_id"].str.split("|").str[4]
    df_filtered["family"] = df_filtered["subject_id"].str.split("|").str[5]

    # Save filtered results to CSV
    df_filtered.to_csv("filtered_" + file_name.replace(".txt", ".csv"), index=False)

    # Print summary
    print("\n🎯 Top ARG hits:")
    print(df_filtered[["gene", "family", "identity", "evalue"]])

except FileNotFoundError:
    print(f"❌ File '{file_name}' not found. Please check the name and try again.")
except Exception as e:
    print(f"⚠️ An error occurred: {e}")
