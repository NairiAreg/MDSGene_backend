import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os


def aao_to_value(aao):
    """Convert age at onset (aao) to categorical value"""
    try:
        if pd.isna(aao) or aao == -99:
            return 2
        aao = float(aao)
        if aao <= 10:
            return 1
        elif 10 < aao <= 20:
            return 3
        elif 20 < aao <= 30:
            return 4
        elif 30 < aao <= 40:
            return 5
        elif 40 < aao <= 50:
            return 6
        elif 50 < aao <= 60:
            return 7
        elif 60 < aao <= 70:
            return 8
        elif 70 < aao <= 80:
            return 9
        elif 80 < aao <= 90:
            return 10
        else:
            return 11
    except (ValueError, TypeError):
        return 2


def read_and_preprocess_data(excel_path, feature_columns):
    """Read and preprocess the data from Excel file"""
    # Read Excel file
    raw_data = pd.read_excel(excel_path, sheet_name=0).values

    # Initialize array for processed data
    data_array = np.zeros((raw_data.shape[0], len(feature_columns)))

    # Dictionary for string to integer conversion
    strings_to_int_dict = {  # genes (classes)
        "CACNA1A": 1,
        "LRRK2": 2,
        "KCNA1": 3,
        "PDHA1": 4,
        "SLC1A3": 5,
        "GBA1": 6,
        # unknown value
        "-99": 0,
        # ethnicity
        "African ancestry": 1,
        "Arab": 2,
        "Asian": 3,
        "Brazilian": 4,
        "Caucasian": 5,
        "Hispanic": 6,
        "Indian ancestry": 7,
        "Jewish (Ashkenazi)": 8,
        "Jewish (non-Ashkenazi/undefined)": 9,
        "kurdish": 10,
        "other": 0,
        # sex
        "male": 1,
        "female": 2,
        # signs/symptoms
        "yes": 1,
        "no": 2,
        "not treated": 3,
        # countries
        "ARG": 1,
        "AUS": 3,
        "AUT": 5,
        "BEL": 6,
        "BOL": 7,
        "BRA": 8,
        "CAN": 9,
        "CHE": 10,
        "CHL": 11,
        "CHN": 12,
        "COL": 13,
        "CUB": 14,
        "CZE": 15,
        "DEU": 16,
        "DNK": 17,
        "DZA": 18,
        "EGY": 19,
        "ESP": 20,
        "FIN": 21,
        "FRA": 22,
        "FSM": 24,
        "GBR": 25,
        "GER": 26,
        "GRC": 27,
        "IND": 28,
        "IRL": 29,
        "IRN": 30,
        "IRQ": 31,
        "ISR": 32,
        "ITA": 33,
        "JAP": 34,
        "JOR": 35,
        "JPN": 36,
        "KOR": 37,
        "LKA": 38,
        "LTU": 39,
        "MAR": 40,
        "MEX": 41,
        "Mixed/other": 2,
        "NLD": 43,
        "NOR": 44,
        "PAK": 45,
        "PER": 46,
        "PHL": 47,
        "PHP": 48,
        "POL": 49,
        "PRI": 50,
        "PRT": 51,
        "QAT": 52,
        "RUS": 53,
        "SAU": 54,
        "SDN": 55,
        "SGP": 56,
        "SPA": 57,
        "SRB": 58,
        "SVK": 59,
        "SWE": 60,
        "TUN": 61,
        "TUR": 62,
        "TWN": 63,
        "UKR/POL": 64,
        "USA": 23,
        "ZAF": 42,
        "ZMB": 65
    }

    # Process each feature
    for f, feature in enumerate(feature_columns):
        for p in range(data_array.shape[0]):
            value = raw_data[p][feature]

            # Special handling for age at onset
            if feature == 5:  # If this is the AAO column
                data_array[p][f] = aao_to_value(value)
                # If AAO is unknown, check age at diagnosis
                if data_array[p][f] == 2:
                    data_array[p][f] = aao_to_value(raw_data[p][7])
            else:
                # Convert string values to integers using dictionary
                data_array[p][f] = strings_to_int_dict.get(str(value), -999)

    return data_array


def train_random_forest(data_array, model_save_path='random_forest_model.pkl'):
    """Train Random Forest model and save it"""
    # Split features and target
    X = np.delete(data_array, 0, axis=1)  # Remove first column (target)
    y = data_array[:, 0]  # First column is target

    # Initialize and train Random Forest with balanced class weights
    rf_model = RandomForestClassifier(
        n_estimators=150,
        criterion='gini',
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features='sqrt',
        max_leaf_nodes=None,
        min_impurity_decrease=0.0,
        bootstrap=True,
        oob_score=False,
        n_jobs=-1,
        random_state=42,
        verbose=0,
        warm_start=False,
        class_weight='balanced'  # Изменено здесь для обработки несбалансированных данных
    )

    # Fit the model
    rf_model.fit(X, y)

    # Save the model
    joblib.dump(rf_model, model_save_path)
    print(f"Model saved to: {model_save_path}")

    return rf_model


def main():
    # Set paths
    EXCEL_PATH = r'Data/ZUSM.xlsx'  # Update this path
    MODEL_SAVE_PATH = r'Model/RF_model.pkl'  # Update this path

    # Define feature columns to use
    # First column (index 1) should be the target variable (gene)
    # Add or remove features as needed
    FEATURE_COLUMNS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
        30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
        57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
        84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108,
        109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
        130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,
        151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171,
        172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192,
        193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213,
        214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232]

    # Create model directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

    try:
        # Read and preprocess data
        print("Reading and preprocessing data...")
        data_array = read_and_preprocess_data(EXCEL_PATH, FEATURE_COLUMNS)

        # Train and save model
        print("Training Random Forest model...")
        model = train_random_forest(data_array, MODEL_SAVE_PATH)

        print("Training completed successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()