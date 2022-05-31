import pandas as pd
from pathlib import Path

__all__ = (
    "DATA_PATH",
    "load_csv",
)

DATA_PATH = Path(__file__).parent


def load_csv(file_name: str) -> pd.DataFrame:
    file_path = DATA_PATH.joinpath(file_name)
    return pd.read_csv(file_path, delimiter=",", index_col=0, na_values="")
