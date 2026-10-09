"""storage.py - saves and loads rainfall records in a CSV file (Pandas)."""
import os
import pandas as pd

FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "data", "rainfall.csv")


def empty_table():
    """An empty table with the three columns."""
    return pd.DataFrame({"date": pd.to_datetime([]),
                         "location": pd.Series(dtype="object"),
                         "rainfall_mm": pd.Series(dtype="float64")})


def load_records(path=FILE_PATH):
    """Read the CSV file. Missing or empty file gives an empty table."""
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        return empty_table()
    except pd.errors.EmptyDataError:
        return empty_table()
    except Exception as error:
        raise Exception(f"Could not read the data file: {error}")

    if not {"date", "location", "rainfall_mm"}.issubset(df.columns):
        raise Exception("Data file must have columns: date, location, rainfall_mm")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["rainfall_mm"] = pd.to_numeric(df["rainfall_mm"], errors="coerce")
    df = df.dropna()                                  # skip bad rows
    df = df.sort_values("date").reset_index(drop=True)
    return df[["date", "location", "rainfall_mm"]]


def save_records(df, path=FILE_PATH):
    """Write the table to the CSV file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out = df.copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(path, index=False)


def add_record(df, date, location, rainfall):
    """Return a new table with one more record. Same date+location is not allowed."""
    same = (df["date"] == pd.Timestamp(date)) & (df["location"] == location)
    if same.any():
        raise ValueError(f"A record for {location} on {date} already exists")
    new_row = pd.DataFrame({"date": [pd.Timestamp(date)],
                            "location": [location],
                            "rainfall_mm": [rainfall]})
    df = pd.concat([df, new_row], ignore_index=True)
    return df.sort_values("date").reset_index(drop=True)


def delete_record(df, index):
    """Return a new table without the row number `index`."""
    if index not in df.index:
        raise ValueError("Record not found")
    return df.drop(index=index).reset_index(drop=True)
