from discharge_queich.database.queries import load_discharge_data

from discharge_queich.model.features import create_features


df = load_discharge_data()

features = create_features(df)

print(features.head())

print(features.columns)