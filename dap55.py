import numpy as np

print("Create one dimensional array")
arr = np.array([1, 2, 3, 4, 5])

print(arr)

print(type(arr))

#Inserting element in specific index
print("Inteserting -1 at 3rd place")
arr1=np.insert(arr, 3, -1)
print(arr1)
print("Create two dimensional array")

print ("Appending 6 to the array arr")
print(np.append(arr,[6], axis=0))
print(arr)

print("creat 2 dimentional array")
arr = np.array([[10, 32, 30],[50, 20, 82], [91, 45, 91]])
print(arr)

print("insert a row to two dimensional")
arr1=np.insert(arr, 1, [2, 4, 3], axis=0)
print(arr1)

print("Append the row to array axis =0 for row")
arr1=(np.append(arr,[[18, 24, 36]], axis=0))
print(arr1)

print ("insert column at 1st column axis=1")
arr1=np.insert(arr, 0, [2, 4, 3], axis=1)
print(arr1)

print("Search in sigle dimension array")
arr=np.array([1, 2, 3, 4, 5, 4, 4])
x=np.where(arr==4)
print(x)

print("Search all even numbers")
arr=np.array([1, 2, 3, 4, 5, 4, 4])
x=np.where(arr%2==0)
print(x)

print("Search in two dimensional array")
arr = np.array([[10, 32, 30],[50, 20, 82], [91, 45, 91]])
x=np.where(arr==91)
print(x)
print(type(x))


print("Sorting the sigle dimension array")
arr= np.array([3, 2, 0, 1])
print(np.sort(arr))

tarr = np.array(['banana', 'cherry', 'apple'])
print(np.sort(tarr))

arr = np.array([[10, 32, 30],[50, 20, 82], [91, 45, 91]])
print (arr)
print("-------")
print("Sorts row wise")
print(np.sort(arr))

print("Split single dimension mention number of slices as 2nd arguments")
arr = np.array([1, 2, 3, 4, 5, 6])
newarr = np.array_split(arr, 3)
print(newarr)

print("Two dimensional array for row wise mention axis=0 ..by default axis will be 0")
arr = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
newarr = np.array_split(arr, 3, axis=0)
print(newarr)

print ('column split mention axis = 1')
newarr = np.array_split(arr, 2, axis=1)
print(newarr)

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

