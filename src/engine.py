import pandas as pd
from scipy import stats


def analyse_properties(properties_list):
    """
    Takes a list of SQLAlchemy objects or dicts, turns it into a Pandas DataFrame,
    and cleans outliers using SciPy.
    """

    if not properties_list:
        return pd.DataFrame()

    # Convert to a list of Dicts (handling SQLAlchemy objects)
    data = []
    for prop in properties_list:
        if hasattr(prop, "__dict__"):
            # Extract dict, removing SQLAlchemy internal keys
            item = {k: v for k, v in vars(prop).items() if not k.startswith("_sa_")}
            data.append(item)
        else:
            data.append(prop)

    df = pd.DataFrame(data)

    # Basic Cleanup
    if "price" not in df.columns:
        return df

    df = df.dropna(subset=["price"])

    # Z-score outlier removal
    # If standard deviation is a 0 (all prices same), Z-score is invalid.
    if len(df) > 1 and df["price"].std() > 0:
        df["z_score"] = stats.zscore(df["price"])

        # Keep only values within 3 standard deviations
        df_clean = df[abs(df["z_score"]) < 3].copy()
        return df_clean

    return df
