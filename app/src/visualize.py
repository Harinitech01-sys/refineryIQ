import pandas as pd
import matplotlib.pyplot as plt

# load data
df = pd.read_csv("../data/cleaned_data.csv")

# count values
counts = df['Machine failure'].value_counts()

# plot graph
counts.plot(kind='bar')

plt.title("Failure vs Normal")
plt.xlabel("0 = Normal, 1 = Failure")
plt.ylabel("Count")

plt.show()