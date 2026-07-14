from pathlib import Path
import pandas as pd

from discharge_queich.configs import settings
from discharge_queich.database.queries.dashboard import load_discharge_data
from discharge_queich.model.features import create_training_features
from discharge_queich.model.dataset import TimeSeriesDataset
from discharge_queich.model.build_model import model


# Load data
# df = load_discharge_data()
df = pd.read_csv(
    "discharge_siebeldingen_2026-0514.csv",
    decimal=",", 
    sep=";", 
    na_values="-"
    )

df = df.dropna()
df = df.set_index(keys=["timestamp"])
df.index = pd.to_datetime(df.index, format="%d.%m.%Y %H:%M")

df = create_training_features(df, horizon=settings.model.inference.steps)

# Create dataset
dataset = TimeSeriesDataset(df)

train_dataset, val_dataset, test_dataset = (
    dataset.create_datasets()
)


# Fit model
model.fit(
    train_dataset[0], 
    train_dataset[1],
    eval_set=[(val_dataset[0], val_dataset[1])],
)


# Save model
save_dir = Path("models")
model_name = "xgb_model.json"
save_path = save_dir / model_name

model.save_model(save_path)
print(f"Saved model '{model_name}' to {save_path}")