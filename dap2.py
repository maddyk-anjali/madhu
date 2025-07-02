def insert_into_sorted_list(arr, element):
    arr.append(element)
    arr.sort()  # Ensuring the list remains sorted
    return arr

# Taking input from the user
arr = list(map(int, input("Enter the sorted list elements separated by space: ").split()))
element = int(input("Enter the element to insert: "))

# Inserting the element and displaying output
updated_list = insert_into_sorted_list(arr, element)
print("Updated sorted list:", updated_list)
