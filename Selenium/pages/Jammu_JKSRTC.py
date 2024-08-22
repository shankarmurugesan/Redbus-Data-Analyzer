import streamlit as st
from ScrapData import scrabdata
from filters import filterfunc

def main():
    st.header("Jammu & Kashmir")
    # Add the content and logic for this page here
    st.subheader("Welcome to the Jammu & Kashmir Road Transport Corporation JKSRTC  page!")
    if st.button('Scrap Data'):
        # Call scrabdata only when the button is clicked
        scrabdata(unique_key="Jammu_JKSRTC")
        # Update session state to navigate to the filter page
        st.session_state.page = "filters"

    # If redirection to filter page is set
    if st.session_state.get('page') == "filters":
        filterfunc(unique_key="Jammu_JKSRTC")

if __name__ == "__main__":
    main()
