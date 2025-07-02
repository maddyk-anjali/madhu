import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='white')
rs=np.random.RandomState(10)
d=rs.normal(size=50)
sns.displot(d,kde=True,color="g")
plt.show()