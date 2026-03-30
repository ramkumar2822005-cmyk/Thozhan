import pandas as pd
pd.set_option("display.max_rows",None)
df = pd.read_csv("Crop_Duration_Prediction.csv")

def Duration(Crop,date):
    #try:
    hd = int(df.loc[df["Crop"] == Crop, "Duration_Period"].iat[0])

    date = pd.to_datetime(date,format="%Y-%m-%d")

    hd = date + pd.Timedelta(days=hd)
    hd = pd.to_datetime(hd,format="%Y-%m-%d").date()
    #return "Harvest perion : "+ str(hd)
    return hd
    #except Exception as e:
    #    return "Duration drop"

#print(Duration("Watermelon","2026-04-01"))
