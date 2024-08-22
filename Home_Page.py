import streamlit as st
import pages.Assam_KAAC as Assam_KAAC
import pages.Bihar_BSRTC as Bihar_BSRTC
import pages.South_Bengal_SBSTC as South_Bengal_SBSTC
import pages.North_Bengal_NBSRTC as North_Bengal_NBSRTC
import pages.Jammu_JKSRTC as Jammu_JKSRTC
import pages.Goa_KTCL as Goa_KTCL
import pages.Chandigarh_CTU as Chandigarh_CTU
import pages.West_Bengal_WBTC as West_Bengal_WBTC
import pages.Haryana_HRTC as Haryana_HRTC
import pages.Punjab_PEPSU as Punjab_PEPSU
import pages.ZAll_State_Data as ZAll_State_Data


# Initialize session state for page selection
# if 'page' not in st.session_state:
#     st.session_state.page = "Assam KAAC"

def main():
    st.title("Welcome to the Innovative Bus Data Solutions: ")
    st.header("Automated Data Scraping from RedBus using Selenium and Interactive Analysis with Streamlit")

    # Image path should be relative to the current working directory or an absolute path
    st.image("img/bus.JPG", caption="Bus Image", use_column_width=True)

    # Page titles and their corresponding functions
    pages = {
        "Assam KAAC": Assam_KAAC.main,
        "Chandigarh CTU": Chandigarh_CTU.main,
        "Goa KTCL": Goa_KTCL.main,
        "Haryana HRTC": Haryana_HRTC.main,
        "Jammu JKSRTC": Jammu_JKSRTC.main,
        "Bihar_BSRTC": Bihar_BSRTC.main,
        "Punjab PEPSU": Punjab_PEPSU.main,
        "South Bengal SBSTC": South_Bengal_SBSTC.main,
        "North Bengal NBSRTC": North_Bengal_NBSRTC.main,
        "West Bengal WBTC": West_Bengal_WBTC.main,
        "ZAll_State_Data": ZAll_State_Data.main
    }

    # Sidebar for page selection
    # page = st.sidebar.selectbox(".", options=list(pages.keys()), key="page_selection")
    #
    # # Call the selected page's function
    # pages[page]()





if __name__ == "__main__":
    main()

