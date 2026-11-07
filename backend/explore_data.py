import pandas as pd

df = pd.read_csv("../data/customer_feedback.csv")

print("Dataset Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nUnique Customers/Reviews:")
print(df["uuid"].nunique())

print("\nFeedback Sources:")
print(df["data_source_type"].value_counts())

print("\nSentiment Distribution:")
print(df["sentiment"].value_counts())

print("\nBrand Distribution:")
print(df["brand_name"].value_counts())

print("\nDate Range:")
print(df["engagement_date"].min())
print(df["engagement_date"].max())