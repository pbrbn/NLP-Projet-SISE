import pandas as pd
import numpy as np


# import le fichier data
def load_data():
    data = pd.read_csv("data.csv")
    return data

df = load_data()

# selectonnner les 100 premières lignes et sauvergarder dans un fichier csv
df.head(100).to_csv("data_100.csv", index=False)