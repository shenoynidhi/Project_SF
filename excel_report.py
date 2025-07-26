import pandas as pd
import sys
import os
import re

###Renaming columns

input_file = pd.read_csv("./input.txt")
output_file = os.path.splitext(input_file)[0] + ".xlsx"

# Read the tab-separated file
df = pd.read_csv(input_file, sep="\t", na_values=["."])

# Load original sample names
with open('all_samples.txt') as f:
    sample_names = [line.strip() for line in f]

# Rename fixed columns
rename_dict = {
    "CLNALLELEID": "Allele_ID",
    "CLNDN": "Clinvar_Disease",
    "CLNDISDB": "Clinvar_DB",
    "CLNREVSTAT": "Clinvar_Status",
    "CLNSIG": "ClinVar_Classify",
    "Otherinfo1": "gnomad_v31_het",
    "Otherinfo11": "FILTER"
}
df.rename(columns=rename_dict, inplace=True)

# Rename OtherinfoXX columns to real sample names
sample_cols = [col for col in df.columns if col.startswith("Otherinfo") and col not in rename_dict]
sample_cols = sorted(sample_cols, key=lambda x: int(x.replace("Otherinfo", "")))  # Sort numerically
num_samples = min(len(sample_cols), len(sample_names))
sample_rename = {old: new for old, new in zip(sample_cols[:num_samples], sample_names[:num_samples])}
df.rename(columns=sample_rename, inplace=True)

# Save to Excel
df.to_excel(output_file, index=False, na_rep="NA")

###Column Structuring and Genotype Counting
# Load the renamed Excel file
df = pd.read_excel(output_file)

# Define metadata columns
metadata_cols = [
    'Chr', 'Start', 'End', 'Ref', 'Alt', 'FILTER'
]

db_cols = [
    'InterVar_automated', 'REVEL_score', 'PrimateAI_pred', 'ClinPred_pred', 'AlphaMissense_pred', 'CADD_phred', 'SpliceAI-acc-gain', 'SpliceAI-acc-loss',
    'SpliceAI-don-gain', 'SpliceAI-don-loss'
]

refgene_cols = [   
    'Func_refGene', 'Gene_refGene', 'GeneDetail_refGene', 'ExonicFunc_refGene', 'Gene_full_name_refGene', 'Variant_detail', 'Assembly'
]

clinvar_cols = [
    'Allele_ID', 'Clinvar_Disease', 'Clinvar_DB', 'Clinvar_Status', 'ClinVar_Classify', 'Assertion_criteria'
]

gnomad_cols = [
    'GnomAD_genome_V3_AF', 'gnomad_v4_AF'
]

# Identify sample columns
sample_cols = [col for col in df.columns if col not in metadata_cols + refgene_cols + db_cols + clinvar_cols + gnomad_cols + omim_cols]

# Genotype extraction function
def extract_gt_safe(genotype_info):
    if isinstance(genotype_info, str):
        if genotype_info == "./.:.:.:.:.":
            return "Masked"

        match = re.match(r'^(Ref|Het|Hom|No_GT)', genotype_info)
        if match:
            return match.group(1)

        return "Unknown"
    return "Unknown"
    # Initialize count columns
df['Ref_Count'] = 0
df['Het_Count'] = 0
df['Hom_Count'] = 0
df['Masked_Count'] = 0
df['No_GT_Count'] = 0
df['Unknown_Count'] = 0

# Initialize sample listing columns
het_samples_list = []
hom_samples_list = []
unknown_samples_list = []

# Process each row
for index, row in df.iterrows():
    het_samples = []
    hom_samples = []
    unknown_samples = []

    for col in sample_cols:
        gt_value = extract_gt_safe(row[col])
        if gt_value == "Ref":
            df.at[index, 'Ref_Count'] += 1
        elif gt_value == "Het":
            df.at[index, 'Het_Count'] += 1
            het_samples.append(col)
        elif gt_value == "Hom":
            df.at[index, 'Hom_Count'] += 1
            hom_samples.append(col)
        elif gt_value == "Masked":
            df.at[index, 'Masked_Count'] += 1
        elif gt_value == "No_GT":
            df.at[index, 'No_GT_Count'] += 1
        elif gt_value == "Unknown":
            df.at[index, 'Unknown_Count'] += 1
            unknown_samples.append(col)

    het_samples_list.append(",".join(het_samples))
    hom_samples_list.append(",".join(hom_samples))
    unknown_samples_list.append(",".join(unknown_samples))

# Add result columns
df['Het_Samples'] = het_samples_list
df['Hom_Samples'] = hom_samples_list
df['Unknown_Sample_Columns'] = unknown_samples_list

# Total sample count per row (now includes Unknown)
df['Total_Check'] = df[['Ref_Count', 'Het_Count', 'Hom_Count', 'Masked_Count', 'No_GT_Count', 'Unknown_Count']].sum(axis=1)

count_cols = [
    'Ref_Count', 'Het_Count', 'Hom_Count', 'Masked_Count', 'No_GT_Count', 'Unknown_Count', 'Total_Check'
]

sample_cols = [
    'Het_Samples', 'Hom_Samples', 'Unknown_Sample_Columns'
]

#Final desired column order
final_col_order = metadata_cols + refgene_cols + db_cols + clinvar_cols + gnomad_cols + omim_cols + count_cols + sample_cols + sample_cols

#Reorder Dataframe
df = df[final_col_order]

# Save final output
final_output = os.path.splitext(input_file)[0] + "_genotype_counts.xlsx"
df.to_excel(final_output, index=False)