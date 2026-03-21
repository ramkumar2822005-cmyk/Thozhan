import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

df = pd.read_csv("Crop_Yield_Prediction.csv")

le = LabelEncoder()
df['Crop_encoded'] = le.fit_transform(df["Commodity"])

X = df[["Crop_encoded","Rainfall_mm"]]
y = df["Yield_t_ha"]

model = XGBRegressor()

model.fit(X,y)

def pred(crop,rainfall):
    crop = le.transform([crop])[0]
    pre_yield = model.predict([[crop,rainfall]])
    return round(pre_yield[0],2)

#print(pred('Mustard',445.7))