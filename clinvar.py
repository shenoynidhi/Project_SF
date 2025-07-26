import pandas as pd

#Load input files
annovar_df = pd.read_csv("./input.txt", sep="\t", dtype=str)
clinvar_df = pd.read_csv("./variant_summary.txt", sep="\t", dtype=str, low_memory=False)

clinvar_df = clinvar_df[clinvar_df["Assembly"]=="GRCh38"]
#Ensure all relevant columns are present and in string format
for col in ["CLNALLELEID", "Start"]:
    annovar_df[col] = annovar_df[col].astype(str)
    clinvar_df[col] = clinvar_df[col].astype(str)

#Merge only on CLNALLELEID, Start, and End
merged_df = annovar_df.merge(
    clinvar_df[["CLNALLELEID", "Start", "Name", "Assembly"]],
    on=["CLNALLELEID", "Start"],
    how="left"
)

#Fill missing Name with "NA"
merged_df["Name"] = merged_df["Name"].fillna("NA")

#Save output
merged_df.to_csv("./output.txt", sep="\t", index=False)


