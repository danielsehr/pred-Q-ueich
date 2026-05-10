import pandas as pd

class Dataset:
    def __init__(self, data: pd.DataFrame):
        self.df = data

        assert not self.df.empty, "Empty dataframe provided"

    def split_data(
        self,
        train_size: float = 0.7,
        val_size: float = 0.2,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Performs sequential split of the time-series dataframe
        """
        train_idx = int(len(self.df) * train_size)
        val_idx = train_idx + int(len(self.df) * val_size)

        self.df_train = self.df.iloc[:train_idx]
        self.df_val = self.df.iloc[train_idx:val_idx]
        self.df_test = self.df.iloc[val_idx:]

        print(f"Train size: {len(self.df_train)}")
        print(f"Val size: {len(self.df_val)}")
        print(f"Test size: {len(self.df_test)}")

        return self.df_train, self.df_val, self.df_test


    def prepare_dataset(
        self,
        df: pd.DataFrame,
        skipcols: list[str],
        ):
        feature_cols = [col for col in df.columns if col not in skipcols]

        X_data = df[feature_cols]
        y_data = df["target"]

        return X_data, y_data


    def create_datasets(
        self,
        skipcols: list[str] | None = None,
        ):
        if skipcols is None:
            skipcols = ["target", "date", "Q"]

        self.split_data()

        train_dataset = self.prepare_dataset(self.df_train, skipcols)
        val_dataset = self.prepare_dataset(self.df_val, skipcols)
        test_dataset = self.prepare_dataset(self.df_test, skipcols)

        return train_dataset, val_dataset, test_dataset