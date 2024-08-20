import pandas as pd

df = pd.read_csv("../consumption.csv")


def info(df):
    print(df.head())
    print(df.tail())
    print(df.info())
    print(df.describe())
    print(len(df.columns))
    for i in df.columns:
        print(i)
    print(len(df))


info(df)

profile_id = 5
df.insert(2, "profile_id", profile_id)
info(df)
assert len(df.columns) >= 2
print(df.columns, len(df.columns))
n = len(df.columns) - 3
if n > 0:
    df.drop(columns=df.columns[-n:], axis=1, inplace=True)
print(df.columns)
assert len(df.columns) == 3

df.rename(
    columns={df.columns[0]: "timestamp", df.columns[1]: "consumption_kwh"}, inplace=True
)

df["timestamp"] = pd.to_datetime(
    df["timestamp"], dayfirst=True, format="%m/%d/%Y %H:%M"
)  # TODO: Support many date formats
print("New data: \n")
info(df)
min_date = df.iat[0, 0]
max_date = df.iat[-1, 0]
assert min_date < max_date
print(min_date, max_date)
print((max_date - min_date).days)
"""
records = df.to_dict(orient="records")
for i in records:
    print(i)
"""
info(df)
print(isinstance(df.iat[0, 0], pd.Timestamp))
df.to_csv("../load_consumption_15mins.csv", index=False, date_format="%d/%m/%Y %H:%M")
