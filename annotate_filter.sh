#!/usr/bin/bash 
# Define variables
VCF_FILE="./final_filtered.vcf"
OUT="./annotation"
SPLIT_DIR="./temp_split"
MERGED_FILE="$OUT/final_annotated.txt"
mkdir -p SF
mkdir -p "$SPLIT_DIR" "$OUT"

# Split the VCF into 40 parts with equal number of lines
echo -e "\nSplitting main VCF file..."
split -n l/40 "$VCF_FILE" "$SPLIT_DIR/split_"
echo -e "\nDone Splitting."

# Function to annotate using ANNOVAR   
annotate_var() {
    in="$1"

     perl ./annovar/table_annovar.pl \
       "$in" ./annovar_new/humandb_hg38/ \
       -buildver hg38 -out "$in"_anno -protocol refGene,clinvar,SpliceAI,generic \
       -operation gx,f,f,f -nastring . -remove -vcfinput \
       -xref ./annovar_new/example/gene_fullxref.txt \
       -otherinfo -dot2underline -arg "-splicing_threshold 20 -hgvs -exonsort -infosep -separate",,, \
       -genericdbfile gnomad_v4_af

    # Decompress annotation file
    [ -f "$in"_anno.hg38_multianno.txt.gz" ] && pigz -k -d "$in"_anno.hg38_multianno.txt.gz"
}
export -f annotate_var

# Annotate in parallel
echo -e "\nAnnotating VCF splits..."
ls "$SPLIT_DIR"/split_* | parallel -j 10 annotate_var "{}"
echo "Annotation completed for all split files"

# Merge all annotation outputs while deleting them after merging
echo -e "\nMerging annotation results..."
head -1 "$(ls $SPLIT_DIR/*_anno.hg38_multianno.txt | head -1)" > "$MERGED_FILE"

for file in $SPLIT_DIR/*_anno.hg38_multianno.txt; do
    tail -n +2 "$file" >> "$MERGED_FILE"
    if [ $? -eq 0 ]; then
        echo "Merged: $file. Deleting it..."
        rm "$file"
    else
        echo "Warning: Merge failed for $file. Keeping it for debugging."
    fi
done

echo "Merging complete. Final annotated file: $MERGED_FILE"

#Modifications for zygosity clarity
echo "Modifying the zygosity fields"
sed 's#0[/|]1#Het#g; s#1[/|]0#Het#g; s#1[/|]1#Hom#g; s#0[/|]0#Ref#g' "$MERGED_FILE" > ./zygosity.txt
awk 'BEGIN {OFS=FS="\t"} {for (i=<samplestart_column>; i<=<sampleend_column>; i++) if ($i ~ /^\.:/) sub(/^\./, "No_GT", $i)} 1' ./zygosity.txt > ./temp && mv ./temp ./zygosity.txt
echo "Zygosity modifications completed!"

#SpliceAI column modification
sed -i '0,/generic/s//mirSVR-Score,mirSVR-E,SpliceAI-acc-gain,SpliceAI-acc-loss,SpliceAI-don-gain,SpliceAI-don-loss,MMSp_acceptorIntron,MMSp_acceptor,MMSp_exon,MMSp_donor,MMSp_donorIntron,EnsembleRegulatoryFeature,PHRED/' ./zygosity.txt
#split spliceai column
awk 'BEGIN {OFS=FS="\t"};{gsub(/\,/,"\t",$184);gsub(/^.$/,".\t.\t.\t.\t.\t.\t.\t.\t.\t.\t.\t.\t.",$184);print}' ./zygosity.txt > ./spliceai.txt
echo "Finished the modifications"
#Removal of unnecessary columns
echo "Removing the unnecessary columns"
cut --complement -f<columns_to_exclude> ./spliceai.txt > ./final_sf_annotated.txt
echo "Final_sf_annotated.txt file created"
#Filtering MAF
echo "Filtering MAF"
awk -F"\t" 'NR==1 || ($<column1> <0.02 && $<column2> <0.02)' ./final_sf_annotated.txt > ./filtered_maf.txt
echo "MAF filtering done"
#Retain only P/LP
echo "Retaining P/LP variants"
awk -F'\t' 'NR==1 || $<column_no> ~ /^(Pathogenic|Likely_pathogenic|Pathogenic\/Likely_pathogenic)$/' ./filtered_maf.txt > ./filtered_pathogenic.txt
echo "All P/LP variants retained!"
#Exclude Het variants for autosomal recessive and x-linked recessive genes
echo "Excluding Het variants for autosomal recessive and x-linked recessive genes"
awk -F'\t' 'NR == 1 || ((tolower($<column1>) ~ /autosomal recessive|x-linked recessive/ || tolower($<column2>) ~ /autosomal recessive|x-linked recessive/) && !all_het()) { print } 
function all_het(_, i) { 
  for (i = <samplestart_column>; i <= <sampleend_column>; i++) 
    if ($i !~ /^Het/) return 0; 
  return 1;
}' ./filtered_pathogenic.txt > ./no_het.txt
echo "Het variants for autosomal recessive and x-linked recessive genes excluded!"
