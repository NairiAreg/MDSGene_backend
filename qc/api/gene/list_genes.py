import os
from diseases import get_cached_dataframe
from utils import logger
from typing import List

def get_unique_genes(directory: str = "excel") -> List[str]:
    unique_genes = set()
    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)

                print(f"\nProcessing file: {filename}")
                print(f"Initial DataFrame shape: {df.shape}")

                df = df[df["ensemble_decision"] == "IN"]
                for gene_col in ["gene1", "gene2", "gene3"]:
                    unique_genes.update(df[gene_col].dropna().unique())

            except Exception as e:
                logger.error(f"❌ Error reading file {filename}: {str(e)}")
                logger.exception("Detailed error:")
                continue

    unique_genes_list = list(unique_genes)
    print(f"Total number of unique genes: {len(unique_genes_list)}")
    return unique_genes_list
