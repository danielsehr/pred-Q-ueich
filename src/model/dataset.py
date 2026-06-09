import pandas as pd

class TimeSeriesDataset:
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

        df_train = self.df.iloc[:train_idx]
        df_val = self.df.iloc[train_idx:val_idx]
        df_test = self.df.iloc[val_idx:]

        print(f"Train size: {len(df_train)}")
        print(f"Val size: {len(df_val)}")
        print(f"Test size: {len(df_test)}")

        return df_train, df_val, df_test


    def prepare_dataset(
        self,
        df: pd.DataFrame,
        skipcols: list[str],
        ) -> tuple[pd.DataFrame, pd.Series]:
        
        X_data = df.drop(columns=skipcols)
        y_data = df["target"]

        return X_data, y_data


    def create_datasets(
        self,
        skipcols: list[str] | None = None,
        ) -> tuple[
            tuple[pd.DataFrame, pd.Series],
            tuple[pd.DataFrame, pd.Series],
            tuple[pd.DataFrame, pd.Series],
            ]:
            
        if skipcols is None:
            skipcols = ["target"]

        df_train, df_val, df_test =  self.split_data()

        train_dataset = self.prepare_dataset(df_train, skipcols)
        val_dataset = self.prepare_dataset(df_val, skipcols)
        test_dataset = self.prepare_dataset(df_test, skipcols)

        return train_dataset, val_dataset, test_dataset