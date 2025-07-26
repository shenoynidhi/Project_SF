# Project_SF
Identification of secondary findings workflow developed as part of Thesis project

This repository contains **scripts** used for the identification and prioritization of **Secondary Findings (SFs)** in exome sequencing data, following the ACMG SF v3.2 gene list. The project was part of my MSc dissertation focusing on an Indian exome rare-disease cohort (n=3,549).

---

## **Contents**
- `variant_qual.sh` – Using GATK VariantFiltration tool to annotate and mask the low quality variants (GQ <= 20: LOWGQ, DP <= 15: LOWDP) without removal of entire variant lines
- `annotate_filter.sh` – Annotation of split VCF files parallely using ANNOVAR and GNU Parallel followed by variant filtering based on minor allele frequency (MAF), clinical significance and zygosity
- `clinvar.py` – Appending HGVS cDNA (c.) and protein (p.) notations from downloadable ClinVar variant_summary.txt
- `review_confidence.py` – Parsing the CLNREVSTAT field to assign ClinVar review confidence (0-4 stars) 
- `excel_report.py` – Generation of final excel report with prioritized variants

---

## **Data Privacy Note**
Due to ethical and data privacy concerns, raw data files, and unpublished result files are not shared in this repository.

---

## **Author**
- Nidhi Shenoy
