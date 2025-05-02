import polars as pl
import pandas as pd
from currency_converter import CurrencyConverter


# Initialize the CurrencyConverter
c = CurrencyConverter()




def clean_price_column(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (
            pl.col("price")
            .cast(pl.Utf8, strict=False)  # Ensure the column is treated as string
            .str.replace_all("₹", "")  # Remove currency symbol
            .str.replace_all("â‚¹", "")  # Remove commas
            .str.replace_all("Lac", "")  # Remove "Lac"
            .str.strip_chars()  # Remove extra spaces
            .cast(pl.Float64, strict=False)  # Convert to float
            * 100000  # Convert "Lac" to actual value
        ).alias("price")
    )


conversion_rate = c.convert(1, 'INR', 'USD')

def convert_to_usd(df: pl.DataFrame) -> pl.DataFrame:
      # Get conversion rate from Rupees to US Dollars
    # Ensure price is cleaned before conversion
    df = df.with_columns(
        (pl.col("price").cast(pl.Float64) * conversion_rate).alias("price_usd") # Ensure the price column is in float format
    )

    # Need to ensure the price_usd column is in a decimal format and is to 2 decimal places
    df = df.with_columns(
        (pl.col("price_usd").cast(pl.Decimal(10, 2))).alias("price_usd")
    )
    
    return df.drop("price")  # Drop the original price column


def convert_area_to_sqft(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns([
        # Clean and cast to float
        pl.col('price_per_sqft')
            .str.replace_all("per sqft", "")
            .str.replace_all("₹", "")
            .str.replace_all("â‚¹", "")
            .str.replace_all(",", "")
            .str.replace_all(" ", "")
            .cast(pl.Float64)
            .alias("price_per_sqft_clean")
        ])
    
        # Convert to USD
    df = df.with_columns((pl.col("price_per_sqft_clean") * conversion_rate).alias("price_per_sqft ($)"))
        # Format to 2 decimal places

    df = df.with_columns(pl.col("price_per_sqft ($)").cast(pl.Decimal(10, 2)))
    return df.drop("price_per_sqft_clean", "price_per_sqft")  # Drop the original price column



def furnishing(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns(
        pl.when(pl.col("furnishing").is_not_null())
            .then(
                pl.when(pl.col("furnishing").str.to_lowercase().str.contains("unfurnished"))
                    .then(pl.lit("Unfurnished"))
                    .when(pl.col("furnishing").str.to_lowercase().str.contains("semi"))
                    .then(pl.lit("Semi-Furnished"))
                    .when(pl.col("furnishing").str.to_lowercase().str.contains("furnished"))
                    .then(pl.lit("Furnished"))
                    .otherwise(pl.lit("N/A"))
            )
            .otherwise(pl.lit("N/A"))
            .alias("furnishing_type")
    )

    return df.drop("furnishing")  # Drop the original furnishing column


def status_pl(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns(
        pl.when(pl.col("status").is_null())
        .then(pl.lit("N/A"))
        .when(pl.col("status").str.contains("Poss.", literal=True))
        .then(pl.lit("Not Ready"))
        .when(pl.col("status").str.contains("Ready to Move", literal=True))
        .then(pl.lit("Available now"))
        .otherwise(pl.lit("N/A"))
        .alias("status"),
        pl.when(pl.col("status").str.contains(r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"))
        .then(
            pl.when(pl.col("status").str.contains("Jan")).then(pl.lit("1"))
            .when(pl.col("status").str.contains("Feb")).then(pl.lit("2"))
            .when(pl.col("status").str.contains("Mar")).then(pl.lit("3"))
            .when(pl.col("status").str.contains("Apr")).then(pl.lit("4"))
            .when(pl.col("status").str.contains("May")).then(pl.lit("5"))
            .when(pl.col("status").str.contains("Jun")).then(pl.lit("6"))
            .when(pl.col("status").str.contains("Jul")).then(pl.lit("7"))
            .when(pl.col("status").str.contains("Aug")).then(pl.lit("8"))
            .when(pl.col("status").str.contains("Sep")).then(pl.lit("9"))
            .when(pl.col("status").str.contains("Oct")).then(pl.lit("10"))
            .when(pl.col("status").str.contains("Nov")).then(pl.lit("11"))
            .when(pl.col("status").str.contains("Dec")).then(pl.lit("12"))
            .otherwise(pl.lit(None))
        )
        .alias("month"),
        pl.when(pl.col("status").str.contains(r"23|24|25|26"))
        .then(
            pl.when(pl.col("status").str.contains("23")).then(pl.lit("2023"))
            .when(pl.col("status").str.contains("24")).then(pl.lit("2024"))
            .when(pl.col("status").str.contains("25")).then(pl.lit("2025"))
            .when(pl.col("status").str.contains("26")).then(pl.lit("2026"))
            .otherwise(pl.lit(None))
        )
        .alias("year")
    ).with_columns(
        (pl.col("month").fill_null("") + pl.lit("/") + pl.col("year").fill_null("")).alias("move_in_date")
    ).drop(["month", "year"])

    df = df.with_columns(
        pl.when(pl.col("move_in_date").str.strip_chars() == "/")
        .then(pl.lit(None))
        .otherwise(pl.col("move_in_date"))
        .alias("move_in_date"),
    )

    #df = df.with_columns(
    #    pl.col("move_in_date").str.strptime(pl.Date, "%m/%Y", strict=False).dt.strftime("%m%Y").alias("move_in_date")

    #)

    return df 






def property_type(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.when(pl.col('property_name').is_null())
        .then(pl.lit("N/A"))
        .when(pl.col('property_name').str.contains("Builder Floor", literal=True)).then(pl.lit("Builder Floor"))
        .when(pl.col('property_name').str.contains("Apartment", literal=True)).then(pl.lit("Apartment"))
        .when(pl.col('property_name').str.contains("Office", literal=True)).then(pl.lit("Office"))
        .when(pl.col('property_name').str.contains("House", literal=True)).then(pl.lit("House"))
        .when(pl.col('property_name').str.contains("Shop", literal=True)).then(pl.lit("Shop"))
        .when(pl.col('property_name').str.contains("Plot", literal=True)).then(pl.lit("Plot"))
        .otherwise(pl.lit("N/A"))
        .alias("property_type")
    )

def bedroom(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.when(pl.col("property_name").is_null())
        .then(pl.lit("N/A"))
        .when(pl.col("property_name").str.contains("1 BHK", literal=True))
        .then(pl.lit("1 BHK"))
        .when(pl.col("property_name").str.contains("2 BHK", literal=True))
        .then(pl.lit("2 BHK"))
        .when(pl.col("property_name").str.contains("3 BHK", literal=True))
        .then(pl.lit("3 BHK"))
        .when(pl.col("property_name").str.contains("4 BHK", literal=True))
        .then(pl.lit("4 BHK"))
        .otherwise(pl.lit("N/A"))
        .alias("no_of_bedrooms")
    )

def floor(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns(
        pl.when(~pl.col("floor").fill_null("").str.contains("out of", literal=True))
        .then(pl.lit(None))
        .otherwise(pl.col("floor"))
        .alias("floor")
    )

    df = df.with_columns(
        pl.col("floor")
        .str.replace_all("out of", "/")  # Replace "out of" with "/"
    )

    return df

def square_feet(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col('square_feet')
        .str.replace_all("sqft", "")  # Remove "sq ft" from the string
        .alias("area (sq ft)")
    )



def column_names(df: pl.DataFrame) -> pl.DataFrame:
      
      df = df.rename(
          {
            'areaWithType' : 'area_type',
          }
      )

      return df


def facing(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.when(pl.col("facing").is_null())
        .then(pl.lit("N/A"))
        .when(pl.col("facing").str.contains("North", literal=True)).then(pl.lit("North"))
        .when(pl.col("facing").str.contains("South", literal=True)).then(pl.lit("South"))
        .when(pl.col("facing").str.contains("East", literal=True)).then(pl.lit("East"))
        .when(pl.col("facing").str.contains("West", literal=True)).then(pl.lit("West"))
        .otherwise(pl.lit("N/A"))
        .alias("facing")
    )









# Main function to run the full pipeline
# This function will be called in the main script to run the entire pipeline
def run_full_pipeline(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .pipe(furnishing)  # Clean furnishing type
        .pipe(clean_price_column)  # Ensure price is cleaned before conversion
        .pipe(convert_to_usd)  # Convert price to USD
        .pipe(status_pl)  # Clean status column
        .pipe(property_type)  # Clean property tyepe column
        .pipe(bedroom)  # Clean bedroom column
        .pipe(floor) # Clean floor column
        .pipe(square_feet)  # Clean square feet column
        .pipe(column_names)  # Clean column names
        .pipe(facing)  # Clean facing column
        .pipe(convert_area_to_sqft)  # Convert area to square feet
        .drop('description')
    )






