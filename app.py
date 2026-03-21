import streamlit as st
import pandas as pd
import os
import re
import bcrypt
import plotly.express as px
import Crop_Duration_Prediction as cdp
import RainFall_Prediction as rp
import Crop_Yield_Prediction as cyp
import Crop_Production_Prediction as cpp
import Total_Demand_Prediction as tdp
import Price_Prediction as pp
import Population_Prediction as pop_predict
st.write("connecting to db")
from db import get_connection

st.write("🚀 App started")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username, password):
    st.write("inside register_user")
    conn = get_connection()
    st.write("connected")
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE username=%s",(username,))
    result = cursor.fetchone()
    

    if result:
        conn.close()
        return False
    else:
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",(username, hashed_pw))
        conn.commit()
        conn.close()
        return True

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username=%s",(username,))

    result = cursor.fetchone()
    conn.close()

    if result:
        stored_password = result[0]
        return check_password(password, stored_password)

    return False

def get_all_data():
    conn = get_connection()
    query = "SELECT * FROM registrations"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def registration(username, district, farmer_name, farmer_ph, crop, area, sd, hd, production):
    conn = get_connection()
    cursor = conn.cursor()

    hd = str(hd)
    area = float(f'{area:.2f}')
    production = float(f'{production:.2f}')
    cursor.execute("""
        INSERT INTO registrations 
        (username, district, farmer_name, farmer_ph_no, crop, area, sowing_date, harvest_date, production)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (username, district, farmer_name, farmer_ph, crop, area, sd[:7], hd[:7], production))

    conn.commit()
    conn.close()

def estimated_sutitution(district, crop, hd, production, actual_demand):
    conn = get_connection()
    cursor = conn.cursor()

    hd_month = str(hd)[:7]
    cursor.execute("""
        SELECT SUM(production) 
        FROM registrations
        WHERE district = %s 
        AND crop = %s 
        AND harvest_date = %s
    """, (district, crop, hd_month))
    result = cursor.fetchone()
    conn.close()

    current_fullfill = float(result[0]) if result[0] is not None else 0
    st.write("Already registered production:", round(current_fullfill,2)," tonnes")
    # Call existing chart function
    st.plotly_chart(tdp.demand_chart(crop=crop,demand=actual_demand,current=current_fullfill,new_prod=production), use_container_width=True)
    #return tdp.demand_chart(crop, actual_demand, current_fullfill, production)

if not st.session_state.logged_in:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        st.subheader("Create Account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("Account created!")
            else:
                st.error("Account already exist...")

    elif choice == "Login":
        st.subheader("Login")
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if login_user(user, password):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials")

if st.session_state.logged_in:
    st.set_page_config(page_title="Crop AI Dashboard",layout="wide")
    st.sidebar.success(f"🌾 Thozhan {st.session_state.username}")
    st.sidebar.title("Navigation bar")
    if "pred_reg" not in st.session_state:
        st.session_state.pred_reg = False
    if "analysis" not in st.session_state:
        st.session_state.analysis = False
    if st.session_state.username == "admin":
        if "admin_panel" not in st.session_state:
            st.session_state.admin_panel = False
    else:
        if "my_activity" not in st.session_state:
            st.session_state.my_activity = False
    if "run_clicked" not in st.session_state:
        st.session_state.run_clicked = False
    if "register_clicked" not in st.session_state:
        st.session_state.register_clicked = False
    if "ch" not in st.session_state:
        st.session_state.ch = False
    
    if st.sidebar.button("Prediction / Registration"):
        st.session_state.pred_reg = True
        st.session_state.analysis = False
        if (st.session_state.username == "admin"):
            st.session_state.admin_panel = False
        else:
            st.session_state.my_activity = False
    
    if st.sidebar.button("Analysis dashboard"):
        st.session_state.pred_reg = False
        st.session_state.analysis = True
        if (st.session_state.username == "admin"):
            st.session_state.admin_panel = False
        else:
            st.session_state.my_activity = False
    
    if st.session_state.username == "admin":
        if st.sidebar.button("Admin panel"):
            st.session_state.pred_reg = False
            st.session_state.analysis = False
            st.session_state.admin_panel = True

    else:
        if st.sidebar.button("My Activity"):
            st.session_state.pred_reg = False
            st.session_state.analysis = False
            st.session_state.my_activity = True

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    df = get_all_data()    
    
    if st.session_state.pred_reg:
        st.header("Crop Production prediction and Registration")

        district_list = ['Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore', 'Dharmapuri', 'Dindigul', 'Erode', 
                        'Kallakuruchi', 'Kancheepuram', 'Karur', 'Krishnagiri', 'Madurai', 'Nagapattinam', 
                        'Nagercoil (Kannyiakumari)', 'Namakkal', 'Perambalur', 'Pudukkottai', 'Ramanathapuram', 'Ranipet', 
                        'Salem', 'Sivaganga', 'Tenkasi', 'Thanjavur', 'The Nilgiris', 'Theni', 'Thiruchirappalli', 'Thirunelveli', 
                        'Thirupathur', 'Thirupur', 'Thiruvannamalai', 'Thiruvarur', 'Thiruvellore', 'Tuticorin', 'Vellore', 
                        'Villupuram', 'Virudhunagar']
        crop_list = ['Alasande Gram', 'Amaranthus', 'Ambada Seed', 'Areca Nut', 'Ash Gourd', 'Avarai', 'Banana', 'Barley', 
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
        year_crops = ['Areca Nut', 'Betal Leaves', 'Black pepper', 'Cardamoms', 'Cashewnuts', 
                'Coconut', 'Coffee', 'Drumstick', 'Grapes', 'Guava', 'Jasmine', 'Lemon', 
                'Mango', 'Orange', 'Pepper', 'Pomegranate', 'Rose', 'Rubber', 'Sapota', 
                'Tea', 'Copra', 'Lime', 'Tamarind Fruit', 'Kanakambaram', 'Tamarind Seed',
                'Neem Seed', 'Sweet Lime', 'Zizyphus', 'Custard Apple', 'Indian Gooseberry', 
                'Ivy Gourd', 'Jack Fruit', 'Jamun', 'Tuberose', 'Tube Flower', 'Fig', 'Pear','Pineapple']
        
        # ---------------- INPUTS ---------------- #
        st.subheader("Enter Details")
        col1, col2 = st.columns(2)
        district = col1.selectbox("District",district_list)
        crop = col2.selectbox("Crop", crop_list)

        if crop in year_crops:
            sd = col1.date_input("Planting Date")
        else:
            sd = col1.date_input("Sowing Date")

        area = col2.number_input("Area (Hectares)", min_value=0.1, step=0.1)
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            run_btn = st.button("Run Prediction",use_container_width=True)

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
                production = round(cpp.production(yld, area),2)

                actual_demand = tdp.demand(district, crop, hd)
                population = pop_predict.Population(pd.to_datetime(hd).year)
                price = pp.Price_prediction(district, crop, population, production)

                total_price = round(production * (price * 10), 2)

                # -------- Display -------- #
                st.subheader("📊 Results")

                col1, col2 = st.columns(2)

                col1.metric("Harvest Date", str(hd))
                col1.metric("Rainfall (in mm)", round(rainfall,2))
                col1.metric("Yield (in Tonnes)", yld)

                col2.metric("Production (in Tonnes)", production)
                col2.metric("Demand (in Tonnes)", actual_demand)
                col2.metric("Price / Quintal", f"₹ {price}")

                st.success(f"💰 Estimated Total Price: ₹ {total_price}")

                #st.pyplot(estimated_sutitution(district,crop,hd,production,actual_demand))
                
                estimated_sutitution(district,crop,hd,production,actual_demand)
                
                st.subheader("**Do you want to register?**")
                
                # Show button ONLY if not clicked yet
                if not st.session_state.register_clicked:
                    if (st.session_state.ch or st.button("Yes")):
                        st.session_state.ch = True
                        col1 , col2 = st.columns(2)
                        farmer_name = col1.text_input("Farmer name")
                        farmer_ph = col2.text_input("Phone Number", placeholder="e.g., 9876543210")
                        
                        # Optional: Basic validation using regex (this is a simple example)
                        if re.fullmatch(r"\d{9,10}$", farmer_ph):
                            c1, c2, c3 = st.columns([1,2,1])
                            if c2.button("Submit",use_container_width=True):
                                st.session_state.register_clicked = True
                                registration(st.session_state.username, district, farmer_name, farmer_ph, crop, area, sd, hd, production)
                                st.session_state.ch = False
                                st.success("Successfully registered!!!")
                        else:
                            st.error("Invalid format.")
                        
                else:
                    st.success("✅ Already registered!")

            except Exception as e:
                st.error(f"Error: {e}")
    
    if st.session_state.analysis:
        st.header("📊 Analysis Dashboard")
        if st.session_state.username != 'admin':
            df = df[df['username']==st.session_state.username]
        
        col1, col2 = st.columns(2)
        hd = col1.date_input("Month and year to analysis")
        hd = str(hd)[:7]
        df = df[df['harvest_date']==hd]
        crop_data = df.groupby('crop')['production'].sum().reset_index()
        crop_t = col2.selectbox("Crop",['over all']+crop_data['crop'].unique().tolist())
        
        if crop_t == 'over all':
            st.subheader("Overall analysis")
            col1.metric("Total Registrations", len(df))
            col2.metric("Total Farmers registered", df["farmer_ph_no"].nunique())
            
            crop_data = df.groupby('crop')['production'].sum().reset_index()
            col1.dataframe(crop_data)

            farmer_data = df[['farmer_name','farmer_ph_no']]
            farmer_data = farmer_data.drop_duplicates().reset_index()
            col2.dataframe(farmer_data)

            # Crop wise Production Chart
            fig = px.bar(crop_data, x="crop", y="production", title=f"{crop_t} Production (During {hd})")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader(f"Analysis of {crop_t}")
            df = df[df['crop']==crop_t]
            col1.metric("Total Registrations", len(df))
            col2.metric("Total Farmers registered", df["farmer_ph_no"].nunique())
            
            crop_data = df.groupby(['farmer_name','farmer_ph_no'])['production'].sum().reset_index()
            col1.dataframe(crop_data)

            farmer_data = df[['farmer_name','farmer_ph_no']]
            farmer_data = farmer_data.drop_duplicates().reset_index()
            col2.dataframe(farmer_data)

            # Crop wise Production Chart
            fig = px.bar(crop_data, x="farmer_name", y="production", title=f"{crop_t} Production (During {hd})")
            st.plotly_chart(fig, use_container_width=True)

        # District wise Production Chart 
        if st.session_state.username == 'admin':
            st.subheader("District wise analysis")
            district_ = st.selectbox("District",df['district'].unique())
            district_data = df.groupby(["district","crop"])["production"].sum().reset_index()
            district_data = df[df['district']==district_]
            fig = px.bar(district_data, x="crop", y="production", title="District Distribution")
            st.plotly_chart(fig)
    
    if st.session_state.username == "admin":
        if st.session_state.admin_panel:
            st.header("🛠 Admin Panel")
            st.subheader("Database")
            st.dataframe(df)  # all users data

    else:
        if st.session_state.my_activity:
            st.subheader("👤 My Activity")
            user_df = df[df["username"] == st.session_state.username]
            st.dataframe(user_df)

            # User-wise Production chart
            fig = px.bar(user_df, x="crop", y="production", title="My Crop Production")
            st.plotly_chart(fig)

else:
    st.warning("Please login to continue")
