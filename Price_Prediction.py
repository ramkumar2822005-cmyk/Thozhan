import pandas as pd
import joblib
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

if os.path.exists('Price_Prediiction_Trained_model.pkl'):
    pipeline = joblib.load('Price_Prediiction_Trained_model.pkl')
else:
    df = pd.read_csv('Price_Analysis.csv')

    X = df.drop(columns=['Avg_Price'])
    y = df['Avg_Price']

    obj_column = ['District','Commodity']
    num_column = ['Population_million','Production_Tonnes']

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), obj_column),
            ("num", "passthrough", num_column)
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    model = RandomForestRegressor()

    pipeline = Pipeline(steps=[
        ('preprocessor',preprocessor),
        ('model',model)
    ])

    pipeline.fit(X_train,y_train)

    y_pred = pipeline.predict(X_test)

    print("r2 Score : ",r2_score(y_test,y_pred))
    print('mean square error : ',mean_squared_error(y_test,y_pred))
    print('mean absolute error : ',mean_absolute_error(y_test,y_pred))

    joblib.dump(pipeline,'Price_Prediiction_Trained_model.pkl')

def Price_prediction(District,Commodity,Population_million,Production_Tonnes):
    input_df = pd.DataFrame({"District":[District],
                             "Commodity": [Commodity],
                             "Population_million": [Population_million],
                             "Production_Tonnes":[Production_Tonnes]})
    result = pipeline.predict(input_df)
    return round(result[0],2)

print(Price_prediction("Theni","Ground Nut",85.3,1200))