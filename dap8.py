# 8. Write a Python program to demonstrate the generation of linear regression models.

import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
x = np.array([[1,2],[2,4],[3,6],[4,8],[5,10],[6,12]])
y = np.array([2,4,6,8,10,12])
model = LinearRegression()
model.fit(x,y)
print("Coefficent: ",model.coef_)
print("Intercept: ",model.intercept_)
newdata = np.array([[7,14]])
prediction = model.predict(newdata)
print(prediction)
plt.scatter(x[:,0],y,color='blue')
plt.plot(x[:,0],model.predict(x),color='red')
plt.show()
