import streamlit as st
import base64

def set_background(image_path:str):
    with open(image_path,'rb') as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)