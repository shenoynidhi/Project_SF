import pandas as pd

# Load input file (tab-separated .txt)
df = pd.read_csv("./input.txt", sep="\t")

# Define mapping function based on the CLNREVSTAT values
def map_review_status_to_stars(revstat):
    if pd.isnull(revstat):
        return pd.NA
    revstat = revstat.lower()

    if 'practice_guideline' in revstat:
        return 'four'
    elif 'reviewed_by_expert_panel' in revstat:
        return 'three'
    elif 'criteria_provided' in revstat and 'multiple_submitters' in revstat:
        return 'two'
    elif 'criteria_provided' in revstat and 'single_submitter' in revstat:
        return 'one'
    elif 'no_assertion_criteria_provided' in revstat:
        return 'none'
    elif 'no_classification_provided' in revstat:
        return 'none'
    else:
        return pd.NA  # if it doesn't match any expected value

# Apply the mapping to the CLNREVSTAT column
df['Gold_Stars'] = df['CLNREVSTAT'].apply(map_review_status_to_stars)

# Save the result to a new tab-separated .txt file, with all columns + new Gold_Stars column
df.to_csv("./output.txt", sep="\t", index=False)
