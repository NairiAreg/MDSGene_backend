import json
from typing import List, Dict, Any

from utils import logger

# Predefined list of categories
PREDEFINED_CATEGORIES = {
    "Development in childhood/adolescence": [],
    "Imaging features": [],
    "Laboratory results": [],
    "Motor ictal": [],
    "Motor interictal": [],
    "Motor signs and symptoms": [],
    "Non-motor ictal": [],
    "Non-motor interictal": [],
    "Non-motor signs and symptoms": [],
    "Other ictal": [],
    "Other interictal": [],
    "Other signs and symptoms": [],
    "Paroxysmal movements": [],
    "Therapy": [],
    "Triggers": [],
    "Unknown": []  # For any uncategorized symptoms
}


def get_symptoms_for_gene(gene_id: str, json_file: str = "categories\\symptom_order.json") -> Dict[str, List[Any]]:
    try:
        # Load symptoms from the JSON file
        with open(json_file, "r", encoding="utf-8") as f:
            symptoms_data = json.load(f)

        # Initialize categories with predefined categories
        categorized_symptoms = {category: [] for category in PREDEFINED_CATEGORIES}

        # Iterate through the symptoms in the JSON file and categorize them
        for symptom in symptoms_data:
            category = symptom.get("categoryName", "Unknown")
            symptom_name = symptom.get("symptomName")

            # Add symptom to the relevant category list
            if category in categorized_symptoms:
                categorized_symptoms[category].append(symptom_name)
            else:
                # If the category is not predefined, add it under "Unknown"
                categorized_symptoms["Unknown"].append(symptom_name)

        print(f"Symptoms loaded and categorized from {json_file}")
        return categorized_symptoms

    except Exception as e:
        logger.error(f"❌ Error reading {json_file}: {str(e)}")
        logger.exception("Detailed error:")
        return PREDEFINED_CATEGORIES  # Return empty categories if there's an error

# Usage example:
# categorized_symptoms = get_symptoms_for_gene("GBA")
