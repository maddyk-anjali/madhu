def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i  # Return the index where the target is found
    return -1  # Return -1 if the target is not found

#madhu
arr = list(map(int, input("Enter the elements of the list separated by space: ").split()))
target = int(input("Enter the element to search for: "))

# Performing linear search
result = linear_search(arr, target)

# Displaying output
if result != -1:
    print(f"Element {target} found at index {result}")
else:
    print(f"Element {target} not found in the list")
