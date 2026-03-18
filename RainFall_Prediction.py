import pandas as pd
import numpy as np
import os
from xgboost import XGBRegressor
import matplotlib.pyplot as plt

if os.path.exists("Future_rainfall.csv"):
    future_df = pd.read_csv("Future_rainfall.csv")

else:
    df = pd.read_csv("Rainfall.csv")

    df = df.melt(id_vars="Year",
                value_vars=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                var_name="Month",
                value_name="Rainfall")

    month_map = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    df["Month"] = df['Month'].map(month_map)
    df["Date"] = pd.to_datetime(dict(year=df.Year,month=df.Month,day=1))

    df = df.sort_values("Date")
    df = df[["Month","Date","Rainfall"]]

    for i in [1,2,3,4,6,12]:
        df[f"lag_{i}"] = df["Rainfall"].shift(i)

    df = df.dropna()

    X = df.drop(["Date","Rainfall"],axis=1)
    y = df["Rainfall"]

    model = XGBRegressor(n_estimators=500,
                        learning_rate=0.05,
                        max_depth=4)

    model.fit(X,y)

    future_prediction = []

    last_values = df.iloc[-1][['Month','lag_1','lag_2','lag_3','lag_4','lag_6','lag_12']].values
    for i in range(60):
        pred = model.predict(last_values.reshape(1,-1))[0]
        future_prediction.append(pred)
        last_values = np.roll(last_values,1)
        last_values[0] = pred

    #Create Future Date table

    future_dates = pd.date_range(start=df['Date'].max(),periods=61,freq="MS")[1:]

    future_df = pd.DataFrame({"Date":future_dates,"Rainfall":future_prediction})
    future_df.to_csv("Future_rainfall.csv",index=False)

#print(future_df)
#calculate rainfall between the period

def Rainfall_Pred(start, end):
    start = pd.to_datetime(start,format="%Y-%m-%d")
    end = pd.to_datetime(end,format="%Y-%m-%d")

    future_df['Date'] = pd.to_datetime(future_df['Date'],format="%Y-%m-%d")
    return future_df[(future_df["Date"] >= start) & (future_df['Date'] <= end)]["Rainfall"].sum()

#print(Rainfall_Pred("2027-01-01","2028-12-01"))

def rainfall_chart(start_year,end_year):
    d = pd.read_csv("Rainfall.csv")
    x = d[(d["Year"] >= start_year) & (d['Year'] <= end_year)]["Year"]
    y = d[(d["Year"] >= start_year) & (d['Year'] <= end_year)]["Annual_rainfall"]
    plt.plot(x,y,marker='o')
    plt.xlabel("Year")
    plt.ylabel("Rainfall in mm")
    plt.xticks(np.arange(start_year,end_year+1,1),rotation=90)
    plt.grid(True)
    
    plt.show()
#rainfall_chart(1950,2025)

def predicted_rainfall_chart(start,end):
    d = future_df
    x = d[(d["Date"] >= start) & (d['Date'] <= end)]["Date"]
    y = d[(d["Date"] >= start) & (d['Date'] <= end)]["Rainfall"]
    plt.plot(x,y,marker='o')
    plt.xlabel("Year")
    plt.ylabel("Rainfall in mm")
    plt.grid(True)
    
    plt.show()
#predicted_rainfall_chart("2027-01-01","2027-12-01")
