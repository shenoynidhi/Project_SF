#!/usr/bin/bash 
echo "Running Variant Filtration"
gatk VariantFiltration \
    -V ./input.vcf \
    --genotype-filter-expression "GQ <= 20" --genotype-filter-name "LowGQ" \
    --genotype-filter-expression "DP <= 15" --genotype-filter-name "LowDP" \
    -O ./filtered.vcf
echo "Variant Quality annotation completed!"
#Masking the LowDP and LowGQ sites
echo "Masking the LowDP and LowGQ sites"
bcftools view -H ./filtered.vcf | awk -F'\t' '{
    for (i=10; i<=NF; i++) {
        if ($i ~ /LowGQ/ || $i ~ /LowDP/)
            $i = "./.:.:.:.:.";  # Mask only affected samples
    }
    print $0;
}' OFS='\t' > ./masked.vcf
echo "Masking the LowDP and LowGQ sites completed!"
#Add header to the masked VCF
bcftools view -h ./filtered.vcf > ./final_filtered.vcf
cat ./masked.vcf >> ./final_filtered.vcf
echo "Variant Filtration completed successfully!"
