# import pandas as pd
# #importing module

# # load iris dataset
# data = pd.read_csv("C:\Users\madhu\Desktop\dap\iris.csv") 

# #displaying the first five rows of dataset 
# print(data.head())

# #displaying the last five rows of dataset 
# print(data.tail())

# #Displaying the number of columns and names of the columns. 
# data.columns 

# #Displaying the shape of the dataset.
# data.shape

# #Display the whole dataset
# print(data) 

# #Slicing the rows.
# sliced_data=data[10:21] 
# print(sliced_data) 

# #Displaying only specific columns.here in the case of Iris dataset. 
# #we will save it in a another variable named "specific_data" 
# specific_data=data[["Id","Species"]] 

# #now we will print the first 10 columns of the specific_data dataframe. 
# print(specific_data.head(10)) 

# #Displaying the specific rows using “iloc” and “loc” functions. 
# data.iloc[5] 
# #it will display records only with species "Iris-setosa". 
# #data.loc[data["Species"] == "Iris-setosa"]
import pandas as pd

# Taking user input for the dataset file path
file_path = input("Enter the CSV file path: ")

# Load the dataset
try:
    data = pd.read_csv("C:\Users\madhu\Desktop\dap\iris.csv")

    # Displaying the first and last five rows
    print("\nFirst 5 Rows of the Dataset:")
    print(data.head())

    print("\nLast 5 Rows of the Dataset:")
    print(data.tail())

    # Displaying column names
    print("\nColumn Names:", data.columns.tolist())

    # Displaying shape of the dataset
    print("\nShape of Dataset (Rows, Columns):", data.shape)

    # Displaying the whole dataset (Optional, can be large)
    # print("\nComplete Dataset:\n", data)

    # Slicing rows from 10 to 20
    print("\nSliced Rows (10-20):")
    print(data.iloc[10:21])

    # Displaying specific columns (Id & Species)
    specific_data = data[["Id", "Species"]]
    print("\nFirst 10 Rows of Specific Columns (Id & Species):")
    print(specific_data.head(10))

    # Displaying specific row using iloc
    print("\nDisplaying 5th Row using iloc:")
    print(data.iloc[5])

    # Filtering records where Species is "Iris-setosa"
    setosa_data = data.loc[data["Species"] == "Iris-setosa"]
    print("\nRecords where Species is 'Iris-setosa':")
    print(setosa_data.head())

except FileNotFoundError:
    print("\nError: The file path is incorrect. Please provide a valid CSV file path.")
except Exception as e:
    print("\nAn error occurred:", e)
