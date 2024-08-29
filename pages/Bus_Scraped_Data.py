import streamlit as st
from Allfilters import allfilterfunc

def main():
    # Custom CSS for header, subheader colors, and line block
    st.markdown(
        """
        <style>
        .header {
            color: green;
        }
        .subheader {
            color: green;
        }
        .line-block {
            background-color: green;
            height: 4px;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Applying custom classes to header and subheader
    st.markdown('<h1 class="header">Comprehensive Data from Red Bus</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">Welcome to the Dynamic Filtering page!</h2>', unsafe_allow_html=True)
    st.markdown('<div class="line-block"></div>', unsafe_allow_html=True)  # Line block after subheader

    allfilterfunc()

if __name__ == "__main__":
    main()