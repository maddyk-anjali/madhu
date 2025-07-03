import numpy as np
import matplotlib.pyplot as plt

# ---------------- A) ARRAY MANIPULATION, SEARCHING, SORTING, SPLITTING ---------------- #
#1234
# Creating a NumPy array
arr = np.array([10, 50, 30, 20, 40])
print("Original Array:", arr)

# 1. Array Manipulation - Reshaping
reshaped_arr = arr.reshape(5, 1)
print("\nReshaped Array:\n", reshaped_arr)

# 2. Searching - Finding index of a specific value (e.g., 30)
index = np.where(arr == 30)
print("\nIndex of 30:", index[0][0])

# 3. Sorting the array
sorted_arr = np.sort(arr)
print("\nSorted Array:", sorted_arr)

# 4. Splitting the array into 2 parts
split_arr = np.array_split(arr, 2)
print("\nSplitted Arrays:", split_arr)

# ---------------- B) BROADCASTING AND PLOTTING NUMPY ARRAYS ---------------- #

# 5. Broadcasting - Performing operations on different-sized arrays
a = np.array([[1], [2], [3]])
b = np.array([10, 20, 30])
broadcasted_sum = a + b  # NumPy automatically matches shapes
print("\nBroadcasting Result:\n", broadcasted_sum)

# 6. Plotting NumPy Arrays
x = np.linspace(0, 10, 100)  # Generate 100 points between 0 and 10
y = np.sin(x)  # Apply sine function

plt.plot(x, y, label="Sine Wave", color='blue')
plt.title("Plot of Sine Function")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()
plt.grid()
plt.show()

import matplotlib.pyplot as plt
import numpy as np
x = np.array([1,2,3,4,5,6,7,8,9,10, 11])
print(x)
y = x * x
# plotting
plt.title("Line graph")
plt.xlabel("Number")
plt.ylabel("Square of Number")
plt.plot(x, y, color ="red")
plt.show()

x = np.array([1,2,3, 4, 5, 6, 7, 8, 9, 10])
y = np.array([100, 10, 300, 20, 500, 60, 700, 80, 900, 100])
 
# plotting
plt.title("Line graph")
plt.xlabel("X axis")
plt.ylabel("Y axis")
plt.plot(x, y, color ="green")
plt.show()

