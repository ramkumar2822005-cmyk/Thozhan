import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
df = pd.read_csv('Population.csv')

x = df[['Year']]
y = df['Population_million']

x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.2,random_state=3)

model = LinearRegression()
model.fit(x_train,y_train)

def Population(year):
    year = pd.DataFrame([[year]],columns=['Year'])
    pop = model.predict(year)
    return round(pop[0],2)

"""print("population : ",Population(2026))
y_pred = model.predict(x_test)

print("r2_score : ",r2_score(y_test,y_pred))
print('MAE : ',mean_absolute_error(y_test,y_pred))
print('MSE : ',mean_squared_error(y_test,y_pred))"""