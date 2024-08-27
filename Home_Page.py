import streamlit as st
import pages.ZAll_State_Data as ZAll_State_Data

def main():
    st.title("Welcome to the Innovative Bus Data Solutions: ")
    st.header("Automated Data Scraping from RedBus using Selenium and Interactive Analysis with Streamlit")

    # Image path should be relative to the current working directory or an absolute path
    st.image("img/bus.JPG", caption="Bus Image", use_column_width=True)

    # Page titles and their corresponding functions
    pages = {
        "ZAll_State_Data": ZAll_State_Data.main
    }

if __name__ == "__main__":
    main()

