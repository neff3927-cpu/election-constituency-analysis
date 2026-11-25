from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_constituencies():
    return pd.read_csv(DATA_DIR / "demo_constituencies.csv")

def load_history():
    return pd.read_csv(DATA_DIR / "demo_history.csv")

def load_regions():
    return pd.read_csv(DATA_DIR / "demo_region_seats.csv")
