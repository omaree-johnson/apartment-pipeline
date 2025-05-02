from utils import load_data, save_data
from pipeline import run_full_pipeline


def run_pipeline():
    data_path = "data/apartments_data_uncleaned.csv"
    raw_data = load_data(data_path)
    cleaned_data = run_full_pipeline(raw_data)
    save_data(cleaned_data, "data/apartments_data_cleaned.csv")
    print(f"Pipeline run successfully!, the data is available in {data_path.replace('uncleaned', 'cleaned')}")

if __name__ == "__main__":
    run_pipeline()


#add the currency converter to the pipeline environment