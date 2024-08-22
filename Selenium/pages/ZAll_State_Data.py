import streamlit as st
from Allfilters import allfilterfunc

def main():
    st.header("All State Data")
    st.subheader("Welcome to the Dynamic Filtering page!")
    allfilterfunc()

if __name__ == "__main__":
    main()