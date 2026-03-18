import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import Population_Prediction as pp

if os.path.exists("Total_Demand_Prediction_Trained_Model.pkl"):
    pipeline = joblib.load("Total_Demand_Prediction_Trained_Model.pkl")
else:
    df = pd.read_csv("total_demand.csv")

    """print("Dataset Preview")
    print(df.head())"""

    df["YM"] = pd.to_datetime(df["YM"])

    df["Month"] = df["YM"].dt.month
    df["Year"] = df["YM"].dt.year

    df["sin_month"] = np.sin(2 * np.pi * df["Month"] / 12)
    df["cos_month"] = np.cos(2 * np.pi * df["Month"] / 12)

    df = df.drop(columns=["YM"])

    X = df.drop(columns=["Production_Tonnes"],axis=1)
    y = df["Production_Tonnes"]

    categorical_features = ["District", "Commodity"]
    numerical_features = ["Population_million", "Month", "Year", "sin_month", "cos_month"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numerical_features)
        ]
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=15,
        random_state=42
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\nModel Evaluation")
    print("MAE:", mae)
    print("R2 Score:", r2)

    #saving the trained model
    joblib.dump(pipeline,"Total_Demand_Prediction_Trained_Model.pkl")


def predict_production(district, commodity, ym, population):

    ym = pd.to_datetime(ym)

    month = ym.month
    year = ym.year

    sin_month = np.sin(2 * np.pi * month / 12)
    cos_month = np.cos(2 * np.pi * month / 12)

    input_df = pd.DataFrame({
        "District": [district],
        "Commodity": [commodity],
        "Population_million": [population],
        "Month": [month],
        "Year": [year],
        "sin_month": [sin_month],
        "cos_month": [cos_month]
    })

    prediction = pipeline.predict(input_df)
    #print(input_df)
    #print(pipeline.named_steps["preprocessor"].transform(input_df))
    return round(prediction[0],2)


def demand(district,commodity,date):
    result = predict_production(
        district=district,
        commodity=commodity,
        ym=date,
        population=pp.Population(pd.to_datetime(date).year)
    )
    return result

"""print(predict_production("Madurai","Mango","2024-01-01",3.2))
print(predict_production("Salem","Mango","2024-01-01",3.2))
print(predict_production("Madurai","Wheat","2024-01-01",3.2))
print(predict_production("Madurai","Mango","2025-05-01",3.5))"""

def demand_chart(crop,actual_demand,current_fullfill,predicted_production_tonnes):
    width = 0.05
    need = actual_demand - current_fullfill
    plt.bar(1,actual_demand,width,label = "Actual Demand",color = "blue")
    plt.bar(1.15,current_fullfill,width,label = "Currently registered",color = 'orange')
    plt.bar(1.30,need,width,label = "Need to be fill",color = 'red')

    plt.xlabel(crop,labelpad=None)
    plt.ylabel("Tonnes")
    plt.title("Demand Chart")
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    plt.ylim(0,actual_demand+1000000)
    plt.legend()
    plt.grid(True)
    try:
        return plt
    except Exception as e:
        plt.show()
