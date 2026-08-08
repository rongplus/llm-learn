import matplotlib.pyplot as plt
import numpy as np

from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

def synthetic_data(w, b, num_examples):  #@save
    """生成y=Xw+b+噪声"""
    #X = np.random.normal(0, 1, (num_examples, len(w)))

    array = np.linspace(1, 20, num=num_examples*2)
    #print(array)
    X = array.reshape(num_examples, 2) # Reshapes into a 3x4 2D array

    y = np.dot(X, w) + b
    y += np.random.normal(0, 5, y.shape)
    return X, y.reshape((-1, 1))

true_w = np.array([-1.6, 3.4])
true_b = 4.2
#method 1: Generate synthetic data
#features, labels = synthetic_data(true_w, true_b, 500)
#method 2: Load diabetes dataset
features, labels = datasets.load_diabetes(return_X_y=True)
# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(features, labels)

# Make predictions using the testing set
diabetes_y_pred = regr.predict(features)
# Method 1 test
#testX = np.array([[6,9], [7,11], [16, 71]])
#testY = regr.predict(testX)
#print('testY: \n', testY)
# end method 1 test

first_column = features[:, 0]


plt.subplot(2, 2, 1)

# Plot outputs
plt.scatter(first_column, labels,  color='red')
plt.plot(first_column, labels, color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())

plt.subplot(2, 2, 2)

plt.scatter(features[:, 0], labels, 1)
plt.xticks(())
plt.yticks(())

plt.subplot(2, 2, 3)

# Plot outputs
plt.plot(features, diabetes_y_pred, color='yellow', linewidth=3)
plt.xticks(())
plt.yticks(())


# 画出通过三个点（[2,3]、[3,4]和[4,4]）直线
def Line_base_by_three_point():
    X = [[2],[3],[4]]
    y = [3,4,4]
    # 用线性模型拟合这；两个点
    lr =regr.fit(X,y)
    # 画出通过三个点（[2,3]、[3,4]和[4,4]）直线
    z = np.linspace(-5,5,20)
    plt.subplot(2, 2, 4)
    plt.scatter(X,y,s=80)
    plt.plot(z,lr.predict(z.reshape(-1,1)),c='k')
    plt.title('Straight Line')

# 显示这条线的斜率和截距 
    print('y={:.3f}'.format(lr.coef_[0]),'x','+{:.3f}'.format(lr.intercept_))
Line_base_by_three_point()
plt.show()