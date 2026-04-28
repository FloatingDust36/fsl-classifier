import pandas as pd

df = pd.read_csv("data/dataset.csv")
df = df[df["label"] != "R"]
df.to_csv("data/dataset.csv", index=False)
print(df["label"].value_counts().sort_index())
