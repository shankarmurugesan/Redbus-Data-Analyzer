import streamlit as st
from ScrapData import scrabdata
from filters import filterfunc

def main():
    st.header("West Bengal")
    # Add the content and logic for this page here
    st.subheader("Welcome to the West Bengal WBTC Page!")

    if st.button('Scrap Data'):
        # Call scrabdata only when the button is clicked
        scrabdata(unique_key="West_Bengal_WBTC")
        # Update session state to navigate to the filter page
        st.session_state.page = "filters"

    # If redirection to filter page is set
    if st.session_state.get('page') == "filters":
        filterfunc(unique_key="West_Bengal_WBTC")


if __name__ == "__main__":
    main()
