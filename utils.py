import polars as pl

def load_data(filepath):
    return pl.read_csv(filepath)

def save_data(df, filepath):
    df.write_csv(filepath)
