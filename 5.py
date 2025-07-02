import numpy as np
# Creating an initial array
arr = np.array([[1, 2, 3], [4, 5, 6]])
print("Original Array:\n", arr)
# **Array Manipulation**
reshaped_arr = arr.reshape(3, 2)
print("\nReshaped Array (3x2):\n", reshaped_arr)
# **Array Searching**
search_element = 5
indices = np.where(arr == search_element)
print(f"\nElement {search_element} found at indices: {indices}")
# **Array Sorting**
unsorted_arr = np.array([3, 1, 5, 2, 4])
sorted_arr = np.sort(unsorted_arr)
print("\nSorted Array:\n", sorted_arr)
# **Array Splitting (Equal Parts)**
split_arrays = np.array_split(arr, 2) # Splitting into 2 parts
print("\nSplit Arrays:")
for i, subarray in enumerate(split_arrays):
print(f"Part {i+1}:\n{subarray}")