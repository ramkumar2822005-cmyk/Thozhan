import streamlit as st
import pandas as pd

import Crop_Duration_Prediction as cdp
import RainFall_Prediction as rp
import Crop_Yield_Prediction as cyp
import Crop_Production_Prediction as cpp
import Total_Demand_Prediction as tdp
import Price_Prediction as pp
import Population_Prediction as pop_predict

st.set_page_config(page_title="Crop Prediction Dashboard", layout="centered")

if "run_clicked" not in st.session_state:
    st.session_state.run_clicked = False

if "register_clicked" not in st.session_state:
    st.session_state.register_clicked = False

st.title("🌾 Crop Prediction Dashboard")

def registration(district,crop,area,sd,hd,production):
    r_df = pd.read_csv("Registered.csv")
    temp_df = pd.DataFrame({"State":['Tamil Nadu'],
                                'District':[district],
                                'Commodity':[crop],
                                'Area':[area],
                                'S_YM':[sd[:7]],
                                'H_YM':[pd.to_datetime(hd).strftime("%Y-%m")],
                                'Production_Tonnes':[f"{production:.2f}"]})
    r_df = pd.concat([r_df,temp_df],axis=0)
    r_df.to_csv("Registered.csv",index=False)

def estimated_sutitution(district,crop,hd,production,actual_demand):
    r_df = pd.read_csv("Registered.csv")
    hd = str(hd)

    if not r_df.empty:
        current_fullfill = r_df[(r_df['District']==district) & (r_df['Commodity']==crop) & (r_df['H_YM']==hd[:7])]
        #print("Df : \n",current_fullfill)
        if not current_fullfill.empty:
            current_fullfill = current_fullfill['Production_Tonnes'].sum()
            return tdp.demand_chart(crop,actual_demand,current_fullfill,production)
        else:
            return tdp.demand_chart(crop,actual_demand,0,production)
    else:
        return tdp.demand_chart(crop,actual_demand,0,production)
    
district_list = ['Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore', 'Dharmapuri', 'Dindigul', 'Erode', 
                 'Kallakuruchi', 'Kancheepuram', 'Karur', 'Krishnagiri', 'Madurai', 'Nagapattinam', 
                 'Nagercoil (Kannyiakumari)', 'Namakkal', 'Perambalur', 'Pudukkottai', 'Ramanathapuram', 'Ranipet', 
                 'Salem', 'Sivaganga', 'Tenkasi', 'Thanjavur', 'The Nilgiris', 'Theni', 'Thiruchirappalli', 'Thirunelveli', 
                 'Thirupathur', 'Thirupur', 'Thiruvannamalai', 'Thiruvarur', 'Thiruvellore', 'Tuticorin', 'Vellore', 
                 'Villupuram', 'Virudhunagar']
crop_list = ['Alasande Gram', 'Amaranthus', 'Ambada Seed', 'Areca nut', 'Ash Gourd', 'Avarai', 'Banana', 'Barley', 
             'Beans', 'Beetroot', 'Bengal Gram', 'Betal Leaves', 'Big Gram', 'Bitter Gourd', 'Black Gram', 'Black pepper', 
             'Bottle Gourd', 'Brinjal', 'Cabbage', 'Capsicum', 'Cardamoms', 'Carrot', 'Cashewnuts', 'Castor Oil', 
             'Castor Seed', 'Cauliflower', 'Chickpeas White', 'Chilli', 'Chow Chow', 'Chrysanthemum', 'Cluster beans', 
             'Coconut', 'Coffee', 'Colacasia', 'Copra', 'Coriander', 'Cotton', 'Cucumber', 'Cumbu', 'Custard Apple', 
             'Drumstick', 'Elephant Foot Yam', 'Fig', 'Foxtail Millet', 'Garlic', 'Ginger', 'Grapes', 'Green Gram', 
             'Green Peas', 'Ground Nut', 'Guar', 'Guava', 'Horse Gram', 'Indian Gooseberry', 'Ivy Gourd', 'Jack Fruit', 
             'Jamun', 'Jasmine', 'Kakada', 'Kanakambaram', 'Karamani', 'Kodo Millet', 'Ladies Finger', 'Leaf Vegetable', 
             'Lemon', 'Lime', 'Maize', 'Mango', 'Marigold', 'Millet', 'Mint', 'Moth Dal', 'Mushrooms', 'Musk Melon', 
             'Mustard', 'Neem Seed', 'Niger', 'Onion', 'Orange', 'Paddy', 'Papaya', 'Pea', 'Pear', 'Pepper', 'Pineapple', 
             'Pomegranate', 'Potato', 'Pulses', 'Pumpkin', 'Radish', 'Ragi', 'Red Gram', 'Ridge gourd', 'Rose', 'Rubber', 
             'Safflower', 'Sapota', 'Sesamum', 'Snake Gourd', 'Sorghum', 'Soya Bean', 'Spinach', 'Sugarcane', 
             'Sunflower Seed', 'Sweet Lime', 'Sweet Potato', 'Tamarind Fruit', 'Tamarind Seed', 'Tapioca', 'Tea', 
             'Tobacco', 'Tomato', 'Tube Flower', 'Tuberose', 'Turmeric', 'Turnip', 'Watermelon', 'Wheat', 'White Pumpkin', 
             'Wild Cabbage', 'Yam', 'Zizyphus']
year_crops = ['Areca nut', 'Betal Leaves', 'Black pepper', 'Cardamoms', 'Cashewnuts', 
              'Coconut', 'Coffee', 'Drumstick', 'Grapes', 'Guava', 'Jasmine', 'Lemon', 
              'Mango', 'Orange', 'Pepper', 'Pomegranate', 'Rose', 'Rubber', 'Sapota', 
              'Tea', 'Copra', 'Lime', 'Tamarind Fruit', 'Kanakambaram', 'Tamarind Seed',
              'Neem Seed', 'Sweet Lime', 'Zizyphus', 'Custard Apple', 'Indian Gooseberry', 
              'Ivy Gourd', 'Jack Fruit', 'Jamun', 'Tuberose', 'Tube Flower', 'Fig', 'Pear','Pineapple']

# ---------------- INPUTS ---------------- #
st.sidebar.header("Enter Details")

district = st.sidebar.selectbox("District",district_list)
crop = st.sidebar.selectbox("Crop", crop_list)

if crop in year_crops:
    sd = st.sidebar.date_input("Planting Date")
else:
    sd = st.sidebar.date_input("Sowing Date")

area = st.sidebar.number_input("Area (Hectares)", min_value=0.1, step=0.1)

run_btn = st.sidebar.button("Run Prediction")

# Button
if run_btn:
    st.session_state.run_clicked = True
    st.session_state.register_clicked = False
# ---------------- OUTPUT ---------------- #
if st.session_state.run_clicked:
    try:
        sd = str(sd)

        hd = cdp.Duration(crop, sd)
        rainfall = rp.Rainfall_Pred(sd, hd)
        yld = cyp.pred(crop, rainfall)
        production = cpp.production(yld, area)

        actual_demand = tdp.demand(district, crop, hd)
        population = pop_predict.Population(pd.to_datetime(hd).year)
        price = pp.Price_prediction(district, crop, population, production)

        total_price = round(production * (price * 10), 2)

        # -------- Display -------- #
        st.subheader("📊 Results")

        col1, col2 = st.columns(2)

        col1.metric("Harvest Date", str(hd))
        col1.metric("Rainfall", rainfall)
        col1.metric("Yield", yld)

        col2.metric("Production", production)
        col2.metric("Demand", actual_demand)
        col2.metric("Price / Quintal", f"₹ {price}")

        st.success(f"💰 Estimated Total Price: ₹ {total_price}")

        st.pyplot(estimated_sutitution(district,crop,hd,production,actual_demand))

        st.markdown("**Do you want to register?**")
        
        # Show button ONLY if not clicked yet
        if not st.session_state.register_clicked:
            if st.button("Yes"):
                st.session_state.register_clicked = True
                registration(district, crop, area, sd, hd, production)
                st.success("Successfully registered!!!")
        else:
            st.success("✅ Already registered!")

        

    except Exception as e:
        st.error(f"Error: {e}")