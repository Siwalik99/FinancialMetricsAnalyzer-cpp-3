import streamlit as st
import numpy as np
import pandas as pd
from components.calculator import render_calculator
from components.simulator import render_simulator
from components.education import render_education

# Configure page
st.set_page_config(
    page_title="Return vs Volatility Analysis Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    # Title and introduction
    st.title("📈 Return vs Volatility Analysis Tool")
    st.markdown("""
    **Explore the impact of volatility on investment returns**
    
    This interactive tool demonstrates key concepts from financial theory about how volatility affects 
    compounded investment returns over time. Based on insights from Kris Abdelmessih's analysis of 
    arithmetic vs geometric returns.
    """)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["📊 Interactive Calculator", "🎲 Monte Carlo Simulator", "📚 Educational Content"]
    )
    
    # Main content area
    if page == "📊 Interactive Calculator":
        render_calculator()
    elif page == "🎲 Monte Carlo Simulator":
        render_simulator()
    elif page == "📚 Educational Content":
        render_education()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666666; font-size: 0.9em;'>
        <p>This tool is for educational purposes only and does not constitute financial advice.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
