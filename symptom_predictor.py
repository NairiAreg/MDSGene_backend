import json
from typing import List, Dict
import numpy as np
import joblib
from pydantic import BaseModel

# List of all features (used during model training)
ALL_FEATURES = [
    "ethnicity", "country", "sex", "aao", "duration", "age_dx",
    # ... (весь список признаков остается тем же)
]

# Default value for missing symptoms
DEFAULT_VALUE = 0


def load_symptom_categories(file_paths: List[str]) -> Dict[str, List[str]]:
    """
    Load and merge symptom categories from multiple JSON files.

    Args:
        file_paths: List of paths to JSON files containing symptom categories

    Returns:
        Dictionary with categories as keys and lists of symptoms as values
    """
    all_symptoms = {}

    for file_path in file_paths:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for category, symptoms in data.items():
                if category not in all_symptoms:
                    all_symptoms[category] = []
                for symptom_key in symptoms.keys():
                    all_symptoms[category].append(symptom_key)

    # Remove duplicates and sort symptoms in each category
    all_symptoms_cleaned = {
        category: sorted(list(set(symptoms)))
        for category, symptoms in all_symptoms.items()
    }
    return all_symptoms_cleaned


def group_age(age: int) -> int:
    """
    Group age into predefined categories.

    Args:
        age: Age in years

    Returns:
        Category number from 1 to 11
    """
    if age == -99 or age <= 0:
        return 2
    if age <= 10:
        return 1
    if age <= 20:
        return 3
    if age <= 30:
        return 4
    if age <= 40:
        return 5
    if age <= 50:
        return 6
    if age <= 60:
        return 7
    if age <= 70:
        return 8
    if age <= 80:
        return 9
    if age <= 90:
        return 10
    return 11


def generate_full_feature_array(
        input_data: Dict[str, int],
        all_features: List[str],
        default_value: int
) -> List[int]:
    """
    Generate a feature array for model prediction.

    Args:
        input_data: Dictionary of feature names and values
        all_features: List of all possible feature names
        default_value: Default value for missing features

    Returns:
        List of feature values in the order expected by the model
    """
    feature_array = [default_value] * len(all_features)

    for feature, value in input_data.items():
        normalized_feature = feature.replace(" ", "_")

        # Match feature by prefix in all_features
        matching_indices = [
            i for i, f in enumerate(all_features)
            if f.startswith(normalized_feature)
        ]

        for index in matching_indices:
            feature_array[index] = value

    return feature_array


def RF_load_and_predict(model_path: str, one_subject: List[int]) -> int:
    """
    Load a trained Random Forest model and make a prediction.

    Args:
        model_path: Path to the saved model file
        one_subject: Feature array for prediction

    Returns:
        Predicted class (integer)
    """
    clf = joblib.load(model_path)
    one_subject = np.array(one_subject).reshape(1, -1)
    return clf.predict(one_subject)[0]


def get_prediction_result(prediction: int) -> str:
    """
    Convert numeric prediction to gene name.

    Args:
        prediction: Numeric prediction from the model

    Returns:
        Gene name or "Unknown"
    """
    prediction_map = {
        1: "CACNA1A",
        2: "LRRK2",
        3: "KCNA1",
        4: "PDHA1",
        5: "SLC1A3",
        6: "GBA1"
    }
    return prediction_map.get(prediction, "Unknown")


def process_symptoms_submission(data_dict: Dict, model_path: str) -> Dict:
    """
    Process submitted symptoms and return prediction.

    Args:
        data_dict: Dictionary with age and symptoms
        model_path: Path to the trained model

    Returns:
        Dictionary with prediction results
    """
    # Convert incoming data to a dictionary
    input_data = {"age": group_age(data_dict["age"])}

    # Mark selected symptoms
    for symptom in data_dict["symptoms"]:
        normalized_symptom = symptom.replace(" ", "_")
        input_data[normalized_symptom] = 1

    # Generate the full feature array
    full_feature_array = generate_full_feature_array(
        input_data,
        ALL_FEATURES,
        DEFAULT_VALUE
    )

    # Make prediction
    prediction = RF_load_and_predict(model_path, full_feature_array)
    prediction_result = get_prediction_result(prediction)

    return {
        "message": f"Predicted diagnosis based on symptoms submitted is {prediction_result}",
        "full_feature_array": full_feature_array,
        "prediction": prediction_result
    }