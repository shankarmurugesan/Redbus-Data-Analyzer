import streamlit as st
from ScrapData import scrabdata
from filters import filterfunc

def main():
    st.header("Assam")
    st.subheader("Welcome to the Karbi Anglong Autonomous Council (Assam) page!")

    if st.button('Scrap Data'):
        # Call scrabdata only when the button is clicked
        scrabdata(unique_key="Assam_KAAC")
        # Update session state to navigate to the filter page
        st.session_state.page = "filters"

    # If redirection to filter page is set
    if st.session_state.get('page') == "filters":
        filterfunc(unique_key="Assam_KAAC")  # Show the filters for Assam KAAC

if __name__ == "__main__":
    main()