import streamlit as st
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["MYSQLHOST"],
        user=st.secrets["MYSQLUSER"],
        password=st.secrets["MYSQLPASSWORD"],
        database=st.secrets["MYSQLDATABASE"],
        port=int(st.secrets["MYSQLPORT"])
    )
