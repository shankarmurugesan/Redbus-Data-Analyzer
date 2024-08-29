import pandas as pd
import streamlit as st
import mysql.connector
from DataClean_DB_Insert import create_connection

def get_state():
    mydb = create_connection()
    cursor = mydb.cursor()
    query = "SELECT DISTINCT states FROM bus_routes"
    cursor.execute(query)
    states = [row[0] for row in cursor.fetchall()]
    cursor.close()
    mydb.close()
    return states

def get_route(state=None):
    if state is None:
        return []
    mydb = create_connection()
    cursor = mydb.cursor()
    query = "SELECT DISTINCT route_name FROM bus_routes WHERE states = %s"
    params = [state]
    cursor.execute(query, tuple(params))
    bus_route = [row[0] for row in cursor.fetchall()]
    cursor.close()
    mydb.close()
    return bus_route

def get_min_max_fare(state):
    mydb = create_connection()
    cursor = mydb.cursor()
    query = "SELECT MIN(price), MAX(price) FROM bus_routes WHERE states = %s"
    params = [state]
    cursor.execute(query, tuple(params))
    min_fare, max_fare = cursor.fetchone()
    cursor.close()
    mydb.close()

    # Convert to float if not None
    if min_fare is not None:
        min_fare = float(min_fare)
    if max_fare is not None:
        max_fare = float(max_fare)

    return min_fare, max_fare

def get_min_max_seats(state):
    mydb = create_connection()
    cursor = mydb.cursor()
    query = "SELECT MIN(seats_available), MAX(seats_available) FROM bus_routes WHERE states = %s"
    params = [state]
    cursor.execute(query, tuple(params))
    min_seats, max_seats = cursor.fetchone()
    cursor.close()
    mydb.close()

    return min_seats, max_seats

def get_filtered_data(statename=None, route=None, operator=None, departure_time=None, bus_type=None, ratings=None, min_seats=None, max_seats=None, min_fare=None, max_fare=None):
    mydb = create_connection()
    cursor = mydb.cursor()
    query = "SELECT * FROM bus_routes WHERE states = %s"
    params = [statename]

    if operator:
        query += " AND operator = %s"
        params.append(operator)
    if departure_time:
        query += " AND " + departure_time
    if bus_type:
        query += " AND bustype LIKE %s"
        params.append(bus_type)
    if ratings:
        query += " AND star_rating BETWEEN %s AND %s"
        params.extend(ratings)
    if min_seats is not None:
        query += " AND seats_available >= %s"
        params.append(min_seats)
    if route:
        query += " AND route_name = %s"
        params.append(route)
    if min_fare is not None:
        query += " AND price <= %s"
        params.append(min_fare)

    cursor.execute(query, tuple(params))
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    cursor.close()
    mydb.close()

    if not results:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(results, columns=columns)

    for time_column in ['departing_time', 'reaching_time']:
        if time_column in df.columns:
            df[time_column] = df[time_column].apply(lambda x: (pd.to_timedelta(x).components.hours, pd.to_timedelta(x).components.minutes))
            df[time_column] = df[time_column].apply(lambda x: f"{x[0]:02}:{x[1]:02}:00")

    return df

def allfilterfunc():
    # Initialize session state for dropdowns if they don't exist
    if 'selected_state' not in st.session_state:
        st.session_state['selected_state'] = ""
    if 'selected_operator' not in st.session_state:
        st.session_state['selected_operator'] = ""
 # Create columns for dropdowns
    col1, col2 = st.columns(2)
    with col1:
        state = get_state()
        # Use session state for 'State Name' dropdown
        st.session_state['selected_state'] = st.selectbox(
            "State Name", 
            options=[""] + state, 
            index=[""] + state.index(st.session_state['selected_state']) if st.session_state['selected_state'] in state else 0
        )
    with col2:
        # Use session state for 'Bus Operator Pvt/Govt' dropdown
        st.session_state['selected_operator'] = st.selectbox(
            "Bus Operator Pvt/Govt", 
            options=["", "Government", "Private"], 
            index=["", "Government", "Private"].index(st.session_state['selected_operator'])
        )

    filter1 = st.session_state['selected_state']
    optional_filter = st.session_state['selected_operator']

    if filter1:
        st.write("Additional Filters")
        bus_route = get_route(filter1)
        min_fare, max_fare = get_min_max_fare(filter1)  # Fetch min and max fare for the selected state
        min_seats, max_seats = get_min_max_seats(filter1)  # Fetch min and max seats for the selected state

        col7, col8 = st.columns(2)
        with col7:
            filter6 = st.selectbox(
                "Bus Route", 
                options=[""] + bus_route, 
                key="bus_route"  # Use session state key
            )
        with col8:
            # Combine Min and Max Bus Fare in one column
            bus_fare = st.number_input(
                "Bus Fare Range",
                min_value=min_fare or 0.0,
                max_value=max_fare or 10000.0,
                value=min_fare or 0.0,
                step=50.00,
                key="bus_fare"  # Use session state key
            )

        col3, col4 = st.columns(2)
        with col3:
            filter2 = st.selectbox(
                "Departure Time", 
                options=["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"], 
                key="departure_time"  # Use session state key
            )
        with col4:
            filter3 = st.selectbox(
                "Bus Type:", 
                options=["", "Seater", "Sleeper", "AC", "NonAC"], 
                key="bus_type"  # Use session state key
            )

        col5, col6 = st.columns(2)
        with col5:
            filter4 = st.slider(
                "Traveler Ratings", 
                0.0, 5.0, (0.0, 5.0), 
                step=0.1,
                key="traveler_ratings"  # Use session state key
            )
        with col6:
            # Combine Min and Max Seats in one column
            seats_avail = st.number_input(
                "Seats Availability",
                min_value=min_seats or 0,
                max_value=max_seats or 50,
                value=min_seats or 0,
                step=1,
                key="seats_avail"  # Use session state key
            )

        DepartureCond = None
        if filter2 == "06:00 - 12:00 Morning":
            DepartureCond = "TIME(departing_time) BETWEEN '06:00:00' AND '12:00:00'"
        elif filter2 == "12:00 - 18:00 Afternoon":
            DepartureCond = "TIME(departing_time) BETWEEN '12:00:00' AND '18:00:00'"
        elif filter2 == "18:00 - 24:00 Evening":
            DepartureCond = "TIME(departing_time) BETWEEN '18:00:00' AND '24:00:00'"
        elif filter2 == "00:00 - 06:00 Night":
            DepartureCond = "TIME(departing_time) BETWEEN '00:00:00' AND '06:00:00'"

        BusTypeCond = None
        if filter3 == "Seater":
            BusTypeCond = "%Seater%"
        elif filter3 == "Sleeper":
            BusTypeCond = "%Sleeper%"
        elif filter3 == "AC":
            BusTypeCond = "%A/C%"
        elif filter3 == "NonAC":
            BusTypeCond = "%Non AC%"

        if st.button("Search"):
            st.subheader("Filtered Results")
            filtered_df = get_filtered_data(
                statename=filter1,
                route=filter6,
                operator=optional_filter,
                departure_time=DepartureCond,
                bus_type=BusTypeCond,
                ratings=filter4,
                min_seats=seats_avail,
                max_seats=seats_avail + 1,  # Adjust max_seats to ensure all values greater than min_seats are included
                min_fare=bus_fare  # Now the max fare is filtered using <= operator
            )

            if filtered_df.empty:
                st.write("No results found for the selected filters.")
            else:
                st.dataframe(filtered_df)
