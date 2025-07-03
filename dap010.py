import pandas as pd
import matplotlib.pyplot as plt

# Sample time series data
data = {
    'Date': [
        '2020-01-25', '2020-02-25', '2020-03-25', '2020-04-25',
        '2020-05-25', '2020-06-25', '2020-07-25', '2020-08-25',
        '2020-09-25', '2020-10-25', '2020-11-25', '2020-12-25',
        '2021-01-25', '2021-02-25', '2021-03-25', '2021-04-25'
    ],
    'A': [102, 114, 703, 547, 641, 669, 897, 994,
          1002, 974, 899, 954, 1105, 1189, 1100, 934],
    'B': [1029, 1178, 723, 558, 649, 669, 899, 1000,
          1012, 984, 918, 959, 1125, 1199, 1109, 954],
    'C': [634, 422, 152, 23, 294, 1452, 891, 990,
          924, 960, 874, 548, 174, 49, 655, 914],
    'D': [1296, 7074, 3853, 4151, 2061, 1478, 2061, 3853,
          6379, 2751, 1064, 6263, 2210, 6566, 3918, 1121],
    'E': [10, 17, 98, 96, 85, 89, 90, 92,
          86, 84, 78, 73, 71, 65, 70, 60]
}

# Create DataFrame and set 'Date' as datetime index
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Display the DataFrame
print("Time Series DataFrame:")
print(df)
#madhu
# Plotting the time series data
plt.figure(figsize=(12, 6))
for column in ['A', 'B', 'C', 'D']:
    plt.plot(df.index, df[column], label=column)
plt.xlabel("Date")
plt.ylabel("Values")
plt.title("Sample Time Series Data")
plt.show()
