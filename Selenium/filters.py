import pandas as pd
import streamlit as st
import mysql.connector
from DataClean_DB_Insert import create_connection

def get_bus_routes(statename):
    # Establish a connection to the MySQL database
    mydb = create_connection()
    # Create a cursor object
    cursor = mydb.cursor()
    # Define the query to get bus routes
    query = f"SELECT DISTINCT route_name FROM bus_routes WHERE state = '{statename}'"
    # Execute the query
    cursor.execute(query)
    # Fetch all the results
    bus_routes = [row[0] for row in cursor.fetchall()]
    # Close the cursor and connection
    cursor.close()
    mydb.close()
    return bus_routes

def get_filtered_data(statename=None, route=None, operator=None, departure_time=None, bus_type=None, ratings=None,seats=None):
    # Establish a connection to the MySQL database
    mydb = create_connection()
    # Create a cursor object
    cursor = mydb.cursor()
    # Define the base query
    query = f"SELECT * FROM bus_routes WHERE state = %s and route_name=%s"
    params = [statename, route]

    # Add filters to the query if they are selected
    if operator:
        query += " AND operator=%s"
        params.append(operator)
    if departure_time:
        query += " AND  " + departure_time
    if bus_type:
        query += " AND bustype like %s"
        params.append(bus_type)
    if ratings:
        query += " AND star_rating " + ratings
    if seats:
        query += " AND seats_available " + seats

    # Execute the query
    cursor.execute(query, tuple(params))
    # Fetch all the results
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    # Close the cursor and connection
    cursor.close()
    mydb.close()
    # Create DataFrame
    df = pd.DataFrame(results, columns=columns)

    # Check and process 'departing_time' and 'reaching_time' if they exist in the DataFrame
    for time_column in ['departing_time', 'reaching_time']:
        if time_column in df.columns:
            # Debugging: Print raw time values
            print(f"Raw '{time_column}' values:", df[time_column].unique())

            # Extract the time component from the Timedelta and convert it to a string
            df[time_column] = df[time_column].apply(lambda x: (pd.to_timedelta(x).components.hours, pd.to_timedelta(x).components.minutes))

            # Format the time as 'HH:MM:SS'
            df[time_column] = df[time_column].apply(lambda x: f"{x[0]:02}:{x[1]:02}:00")

            # Debugging: Check DataFrame after conversion
            print(f"DataFrame after conversion to time format for '{time_column}':\n", df)
        else:
            print(f"Column '{time_column}' not found in DataFrame.")

    return df


def filterfunc(unique_key):
    state_map = {
        "Chandigarh_CTU": ("Chandigarh"),
        "Jammu_JKSRTC": ("Jammu"),
        "Bihar_BSRTC": ("Bihar"),
        "North_Bengal_NBSRTC": ("North_Bengal"),
        "Assam_KAAC": ("Assam"),
        "Goa_KTCL": ("Goa"),
        "South_Bengal_TSRTC": ("South_Bengal"),
        "West_Bengal_WBTC": ("West_Bengal"),
        "Haryana_HRTC": ("Haryana"),
    }
    statename = state_map.get(unique_key, ("Punjab"))

    st.write("Select Bus Routes and Operator from the Filter")

    # Mandatory fileter starts here
    col1, col2 = st.columns(2)
    with col1:
        bus_routes = get_bus_routes(statename)
        filter1 = st.selectbox("Bus Route", options=[""] + bus_routes, key=f"filter1_{unique_key}")
    with col2:
        # Static list for optional filter
        optional_filter = st.selectbox("Bus Operator Pvt/Govt", options=["", "Government", "Private"], key=f"optional_filter_{unique_key}")

    # Step 2: Display additional filters based on initial selection
    if filter1:
        st.write("Additional Filters")
        col3, col4 = st.columns(2)
        with col3:
            filter2 = st.selectbox("Departure Time", options=["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"], key=f"filter2_{unique_key}")
        with col4:
            filter3 = st.selectbox("Bus Type:", options=["", "Seater", "Sleeper", "AC", "NonAC"], key=f"filter3_{unique_key}")

        col5, col6 = st.columns(2)
        with col5:
            filter4 = st.selectbox("Travellers Ratings", options=["", "4 * & Above", "3 * To 4 *", "Below 3 *"], key=f"filter4_{unique_key}")
        with col6:
            filter5 = st.selectbox("Seats Availability", options=["", "Less than 4", "More than 4"], key=f"filter5_{unique_key}")

        # Mapping filter2 to corresponding SQL conditions
        DepartureCond = None
        if filter2 == "06:00 - 12:00 Morning":
            DepartureCond = "TIME(departing_time) BETWEEN '06:00:00' AND '12:00:00'"
        elif filter2 == "12:00 - 18:00 Afternoon":
            DepartureCond = "TIME(departing_time) BETWEEN '12:00:00' AND '18:00:00'"
        elif filter2 == "18:00 - 24:00 Evening":
            DepartureCond = "TIME(departing_time) BETWEEN '18:00:00' AND '24:00:00'"
        elif filter2 == "00:00 - 06:00 Night":
            DepartureCond = "TIME(departing_time) BETWEEN '00:00:00' AND '06:00:00'"

        # Mapping filter3 to corresponding SQL conditions
        BusTypeCond = None
        if filter3 == "Seater":
            BusTypeCond = "%Seater%"
        elif filter3 == "Sleeper":
            BusTypeCond = "%Sleeper%"
        elif filter3 == "AC":
            BusTypeCond = "%A/C%"
        elif filter3 == "NonAC":
            BusTypeCond = "%Non AC%"

        # Mapping filter4 to corresponding SQL conditions
        ratings_cond = None
        if filter4 == "4 * & Above":
            ratings_cond = ">= 4"
        elif filter4 == "3 * To 4 *":
            ratings_cond = "BETWEEN 3 AND 4"
        elif filter4 == "Below 3 *":
            ratings_cond = "< 3"

        # Mapping filter4 to corresponding SQL conditions
        Seats_avail = None
        if filter5 == "Less than 4":
            Seats_avail = "<= 4"
        elif filter5 == "More than 4":
            Seats_avail = "> 4"

        # Step 4: Display the "Search" button
        if st.button("Search", key=f"search_button_{unique_key}"):
            st.subheader("Filtered Results")
            filtered_df = get_filtered_data(statename=statename, route=filter1, operator=optional_filter,departure_time=DepartureCond, bus_type=BusTypeCond, ratings=ratings_cond, seats=Seats_avail)
            # Display the filtered DataFrame
            st.dataframe(filtered_df)
