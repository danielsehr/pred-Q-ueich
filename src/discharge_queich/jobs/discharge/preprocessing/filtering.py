import pandas as pd


def hampel_filter(
    series: pd.DataFrame,
    window: int = 7,
    n_sigmas: int = 3,
    ) -> pd.DataFrame:

    rolling_median = (
        series
        .rolling(window, center=True)
        .median()
    )

    mad = (
        (series - rolling_median)
        .abs()
        .rolling(window, center=True)
        .median()
    )

    threshold = n_sigmas * 1.4826 * mad

    outliers = (
        (series - rolling_median).abs() > threshold
    )

    return series.mask(outliers, rolling_median)