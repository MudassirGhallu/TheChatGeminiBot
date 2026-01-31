import streamlit as st
from groq import Groq
from markitdown import MarkItDown
import requests
import time
from PIL import Image  # Add this import

# Load the image file
try:
    img = Image.open("Ghallu.png")
except:
    img = "🛸" # Fallback to emoji if file is missing

# 1. Gemini Layout & Styling
st.set_page_config(
    page_title="TheGhalluBot", 
    page_icon=img,  # Pass the loaded image object here
    layout="wide"
)
