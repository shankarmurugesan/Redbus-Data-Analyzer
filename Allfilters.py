import pandas as pd
import streamlit as st
import mysql.connector
from DataClean_DB_Insert import create_connection

def get_state_and_routes():
    """
    Fetch distinct routes for hardcoded states from the database.
    """
    # Hardcoded states
    state_list = ["Assam", "Bihar", "Goa", "Jammu", "Haryana", "North_Bengal", "South_Bengal", "Punjab", "Chandigarh", "West_Bengal"]

    # Establish a connection to the MySQL database
    mydb = create_connection()
    # Create a cursor object
    cursor = mydb.cursor()
    # Define the query to get routes for the hardcoded states
    query = "SELECT DISTINCT states, route_name FROM bus_routes WHERE states IN (%s)" % ','.join(['%s'] * len(state_list))
    # Execute the query with the hardcoded states
    cursor.execute(query, tuple(state_list))
    # Fetch all the results
    state_route = cursor.fetchall()
    # Close the cursor and connection
    cursor.close()
    mydb.close()

    # Separate routes by state
    route_dict = {}
    for state, route in state_route:
        if state not in route_dict:
            route_dict[state] = []
        route_dict[state].append(route)

    return state_list, route_dict

def get_operator():
    """
    Fetch distinct bus operators from the database.
    """
    # Establish a connection to the MySQL database
    mydb = create_connection()
    # Create a cursor object
    cursor = mydb.cursor()
    # Define the query to get distinct bus operators
    query = "SELECT DISTINCT operator FROM bus_routes"
    # Execute the query
    cursor.execute(query)
    # Fetch all the results
    operator = [row[0] for row in cursor.fetchall()]
    # Close the cursor and connection
    cursor.close()
    mydb.close()
    return operator

def get_filtered_data(statename=None, route=None, operator=None, departure_time=None, bus_type=None, ratings=None, seats=None, busfare=None):
    # Establish a connection to the MySQL database
    mydb = create_connection()
    # Create a cursor object
    cursor = mydb.cursor()
    # Define the base query
    query = "SELECT * FROM bus_routes WHERE states = %s"
    params = [statename]

    # Add filters to the query if they are selected
    if operator:
        query += " AND operator = %s"
        params.append(operator)
    if departure_time:
        query += " AND " + departure_time
    if bus_type:
        query += " AND bustype LIKE %s"
        params.append(bus_type)
    if ratings:
        query += " AND star_rating " + ratings
    if seats:
        query += " AND seats_available " + seats
    if route:
        query += " AND route_name = %s"
        params.append(route)
    if busfare:
        query += " AND " + busfare

    # Execute the query
    cursor.execute(query, tuple(params))
    # Fetch all the results
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    # Close the cursor and connection
    cursor.close()
    mydb.close()

    # If no results, return an empty DataFrame
    if not results:
        return pd.DataFrame(columns=columns)

    # Create DataFrame
    df = pd.DataFrame(results, columns=columns)

    # Check and process 'departing_time' and 'reaching_time' if they exist in the DataFrame
    for time_column in ['departing_time', 'reaching_time']:
        if time_column in df.columns:
            # Extract the time component from the Timedelta and convert it to a string
            df[time_column] = df[time_column].apply(
                lambda x: (pd.to_timedelta(x).components.hours, pd.to_timedelta(x).components.minutes))

            # Format the time as 'HH:MM:SS'
            df[time_column] = df[time_column].apply(lambda x: f"{x[0]:02}:{x[1]:02}:00")

    return df

def allfilterfunc():
    # Initialize session state defaults before creating widgets
    if 'filter1' not in st.session_state:
        st.session_state['filter1'] = ""
    if 'filter6' not in st.session_state:
        st.session_state['filter6'] = ""
    if 'optional_filter' not in st.session_state:
        st.session_state['optional_filter'] = ""
    if 'filter2' not in st.session_state:
        st.session_state['filter2'] = ""
    if 'filter3' not in st.session_state:
        st.session_state['filter3'] = ""
    if 'filter4' not in st.session_state:
        st.session_state['filter4'] = ""
    if 'filter5' not in st.session_state:
        st.session_state['filter5'] = ""
    if 'filter7' not in st.session_state:
        st.session_state['filter7'] = ""

    # Mandatory filter starts here
    col1, col2 = st.columns(2)
    with col1:
        state_list, route_dict = get_state_and_routes()
        selected_state = st.selectbox("State Name", options=[""] + state_list, key='filter1')

    # Update bus routes based on the selected state
    with col2:
        bus_route_options = route_dict.get(st.session_state['filter1'], [])
        selected_route = st.selectbox("Bus Route", options=[""] + bus_route_options, key='filter6')

    st.write("Additional Filters")

    col7, col8 = st.columns(2)
    with col7:
        operator_list = get_operator()
        optional_filter = st.selectbox("Bus Operator Pvt/Govt", options=[""] + operator_list, key='optional_filter')
    with col8:
        filter7 = st.selectbox("Bus Fare", options=["", "< 500", "500 - 1000", "> 1000"], key='filter7')

    col3, col4 = st.columns(2)
    with col3:
        filter2 = st.selectbox("Departure Time", options=["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"], key='filter2')
    with col4:
        filter3 = st.selectbox("Bus Type:", options=["", "Seater", "Sleeper", "AC", "NonAC"], key='filter3')

    col5, col6 = st.columns(2)
    with col5:
        filter4 = st.selectbox("Travellers Ratings", options=["", "4 * & Above", "3 * To 4 *", "Below 3 *"], key='filter4')
    with col6:
        filter5 = st.selectbox("Seats Availability", options=["", "Less than 4", "More than 4"], key='filter5')

    # Mapping filter7 to corresponding SQL conditions
    bus_fare = None
    if st.session_state.get('filter7') == "< 500":
        bus_fare = "price < 500"
    elif st.session_state.get('filter7') == "500 - 1000":
        bus_fare = "price BETWEEN '500' AND '1000'"
    elif st.session_state.get('filter7') == "> 1000":
        bus_fare = "price > 1000"

    # Mapping filter2 to corresponding SQL conditions
    DepartureCond = None
    if st.session_state.get('filter2') == "06:00 - 12:00 Morning":
        DepartureCond = "TIME(departing_time) BETWEEN '06:00:00' AND '12:00:00'"
    elif st.session_state.get('filter2') == "12:00 - 18:00 Afternoon":
        DepartureCond = "TIME(departing_time) BETWEEN '12:00:00' AND '18:00:00'"
    elif st.session_state.get('filter2') == "18:00 - 24:00 Evening":
        DepartureCond = "TIME(departing_time) BETWEEN '18:00:00' AND '24:00:00'"
    elif st.session_state.get('filter2') == "00:00 - 06:00 Night":
        DepartureCond = "TIME(departing_time) BETWEEN '00:00:00' AND '06:00:00'"

    # Mapping filter3 to corresponding SQL conditions
    BusTypeCond = None
    if st.session_state.get('filter3') == "Seater":
        BusTypeCond = "%Seater%"
    elif st.session_state.get('filter3') == "Sleeper":
        BusTypeCond = "%Sleeper%"
    elif st.session_state.get('filter3') == "AC":
        BusTypeCond = "%A/C%"
    elif st.session_state.get('filter3') == "NonAC":
        BusTypeCond = "%Non AC%"

    # Mapping filter4 to corresponding SQL conditions
    ratings_cond = None
    if st.session_state.get('filter4') == "4 * & Above":
        ratings_cond = ">= 4"
    elif st.session_state.get('filter4') == "3 * To 4 *":
        ratings_cond = "BETWEEN 3 AND 4"
    elif st.session_state.get('filter4') == "Below 3 *":
        ratings_cond = "< 3"

    # Mapping filter5 to corresponding SQL conditions
    seats_cond = None
    if st.session_state.get('filter5') == "Less than 4":
        seats_cond = "< 4"
    elif st.session_state.get('filter5') == "More than 4":
        seats_cond = ">= 4"

    # Trigger search button
    search_button = st.button("Search")
    if search_button:
        df = get_filtered_data(
            statename=st.session_state.get('filter1'),
            route=st.session_state.get('filter6'),
            operator=st.session_state.get('optional_filter'),
            departure_time=DepartureCond,
            bus_type=BusTypeCond,
            ratings=ratings_cond,
            seats=seats_cond,
            busfare=bus_fare
        )
        if df.empty:
            st.write("No data available for the selected filters.")
        else:
            st.write(df)

