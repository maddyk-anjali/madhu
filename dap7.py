#7. Write a Python program that creates a mxn integer array and Prints its attributes using matplotlib

# import numpy as np
# import matplotlib.pyplot as plt
# m = 5
# n = 7
# arr = np.random.randint(100,size=(m,n))
# print(arr)
# print(arr.shape)
# print(arr.size)
# print(arr.T)
# print(arr.dtype)
# print(arr.ndim)
# print(arr.itemsize)
# print(arr.data)
# plt.imshow(arr)
# plt.show()
import matplotlib.pyplot as plt
import numpy as np
x=np.array([-5,-4,-3,-2,-1,0,1,2,3,4,5])
y=[]
for i in range(len(x)):
    y.append(max(0,x[i]))
plt.plot(x,y,color="green")
plt.title(label="ReLU fuction Graph",fontsize=40,color="green")
plt.xlabel("x axis")
plt.ylabel("y axis")
plt.show()
