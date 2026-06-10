from pathlib import Path

from discharge_queich.configs import settings
from discharge_queich.database.queries import load_discharge_data

from discharge_queich.model.features import create_training_features
from discharge_queich.model.dataset import TimeSeriesDataset
from discharge_queich.model.build_model import model
from discharge_queich.model.evaluation import evaluate_model


# Eval dir
eval_dir = Path("model/evaluation")
model_dir = Path("models/xgb_model_discharge_precip.json")

# Load data
df = load_discharge_data()

df = create_training_features(df, horizon=settings.model.inference.steps)

# Create dataset
dataset = TimeSeriesDataset(df)

train_dataset, val_dataset, test_dataset = (
    dataset.create_datasets()
)
# print(test_dataset[0])

# Predict & evaluate
model.load_model(model_dir)
y_pred = model.predict(test_dataset[0])
# print(y_pred)

evaluate_model(
    model=model,
    dataset=test_dataset, 
    pred=y_pred,
    save_dir=eval_dir,
    )