import streamlit as st
from ScrapData import scrabdata
from filters import filterfunc

def main():
    st.header("Goa")
    # Add the content and logic for this page here
    st.subheader("Welcome to the Goa KTCL page!")

    if st.button('Scrap Data'):
        # Call scrabdata only when the button is clicked
        scrabdata(unique_key="Goa_KTCL")
        # Update session state to navigate to the filter page
        st.session_state.page = "filters"

    # If redirection to filter page is set
    if st.session_state.get('page') == "filters":
        filterfunc(unique_key="Goa_KTCL")  # Show the filters for Assam KAAC

if __name__ == "__main__":
    main()