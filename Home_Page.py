import streamlit as st
import pages.Bus_Scraped_Data as Bus_Scraped_Data
from ScrapData import scrabdata

def main():
    st.title("Welcome to the Innovative Bus Data Solutions: ")
    st.header("Automated Data Scraping from RedBus using Selenium and Interactive Analysis with Streamlit")

    # Image path should be relative to the current working directory or an absolute path
    st.image("img/bus.JPG", caption="Bus Image", use_column_width=True)

    # Page titles and their corresponding functions
    pages = {
        "ZAll_State_Data": Bus_Scraped_Data.main
    }

    # Define the mapping of unique keys to display names
    state_keys = {
        "Chandigarh_CTU": "Chandigarh CTU",
        "Jammu_JKSRTC": "Jammu JKSRTC",
        "Bihar_BSRTC": "Bihar BSRTC",
        "North_Bengal_NBSRTC": "North Bengal NBSRTC",
        "Assam_KAAC": "Assam KAAC",
        "Goa_KTCL": "Goa KTCL",
        "South_Bengal_SBSTC": "South Bengal SBSTC",
        "West_Bengal_WBTC": "West Bengal WBTC",
        "Haryana_HRTC": "Haryana HRTC",
        "pepsu": "Punjab PEPSU",
    }

    # Track the state key index in session state
    if 'state_index' not in st.session_state:
        st.session_state.state_index = 0

    # Single button to initiate data scraping
    if st.button('Scrap Data'):
        if st.session_state.state_index < len(state_keys):
            # Get the current unique key and state name
            unique_key = list(state_keys.keys())[st.session_state.state_index]
            state_name = state_keys[unique_key]

            # Call the scraping function with the current unique key
            scrabdata(unique_key=unique_key)
            st.write(f"Button pressed for {state_name}. Starting data scraping...")

            # Increment the state index for the next button press
            st.session_state.state_index += 1
        else:
            st.write("All states have been processed.")

    # Reset button to restart the process
    if st.button('Reset'):
        st.session_state.state_index = 0
        st.write("State index reset. You can start again.")

if __name__ == "__main__":
    main()

