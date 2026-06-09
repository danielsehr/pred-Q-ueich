from src.database.queries import load_discharge_data

from src.model.features import create_features


df = load_discharge_data()

features = create_features(df)

print(features.head())

print(features.columns)