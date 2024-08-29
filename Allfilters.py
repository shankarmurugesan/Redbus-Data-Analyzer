import pandas as pd
import streamlit as st
import mysql.connector
from DataClean_DB_Insert import create_connection

# Function definitions remain unchanged
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

    # Start constructing the query
    query = "SELECT * FROM bus_routes WHERE states = %s"
    params = [statename]

    # Apply filters
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
    # Ensure session state variables are initialized before creating widgets
    if 'selected_state' not in st.session_state:
        st.session_state['selected_state'] = ""
    if 'selected_operator' not in st.session_state:
        st.session_state['selected_operator'] = ""
    if 'selected_route' not in st.session_state:
        st.session_state['selected_route'] = ""
    if 'selected_departure_time' not in st.session_state:
        st.session_state['selected_departure_time'] = ""
    if 'selected_bus_type' not in st.session_state:
        st.session_state['selected_bus_type'] = ""
    if 'selected_ratings' not in st.session_state:
        st.session_state['selected_ratings'] = (0.0, 5.0)
    if 'selected_seats_avail' not in st.session_state:
        st.session_state['selected_seats_avail'] = 0
    if 'selected_bus_fare' not in st.session_state:
        st.session_state['selected_bus_fare'] = 0.0

    # Create columns for dropdowns
    col1, col2 = st.columns(2)
    with col1:
        states = get_state()
        selected_state = st.selectbox(
            "State Name",
            options=[""] + states,
            index=([""] + states).index(st.session_state['selected_state']) if st.session_state['selected_state'] in states else 0,
            key="selected_state"
        )
        # Update session state after widget creation
        st.session_state['selected_state'] = selected_state  

    with col2:
        selected_operator = st.selectbox(
            "Bus Operator Pvt/Govt",
            options=["", "Government", "Private"],
            index=(["", "Government", "Private"]).index(st.session_state['selected_operator']),
            key="selected_operator"
        )
        # Update session state after widget creation
        st.session_state['selected_operator'] = selected_operator  

    # Fetch all data required for other filters if a state is selected
    bus_route = get_route(selected_state)
    min_fare, max_fare = get_min_max_fare(selected_state)  # Fetch min and max fare for the selected state
    min_seats, max_seats = get_min_max_seats(selected_state)  # Fetch min and max seats for the selected state

    col3, col4 = st.columns(2)
    with col3:
        selected_route = st.selectbox(
            "Bus Route",
            options=[""] + bus_route,
            index=([""] + bus_route).index(st.session_state['selected_route']) if st.session_state['selected_route'] in bus_route else 0,
            key="selected_route"
        )
        # Update session state after widget creation
        st.session_state['selected_route'] = selected_route  

    with col4:
        selected_bus_fare = st.number_input(
            "Bus Fare Range",
            min_value=min_fare or 0.0,
            max_value=max_fare or 10000.0,
            value=st.session_state['selected_bus_fare'] or 0.0,
            step=50.00,
            key="selected_bus_fare"
        )
        # Update session state after widget creation
        st.session_state['selected_bus_fare'] = selected_bus_fare  

    col5, col6 = st.columns(2)
    with col5:
        selected_departure_time = st.selectbox(
            "Departure Time",
            options=["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"],
            index=(["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"]).index(st.session_state['selected_departure_time']) if st.session_state['selected_departure_time'] in ["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"] else 0,
            key="selected_departure_time"
        )
        # Update session state after widget creation
        st.session_state['selected_departure_time'] = selected_departure_time  

    with col6:
        selected_bus_type = st.selectbox(
            "Bus Type:",
            options=["", "Seater", "Sleeper", "AC", "NonAC"],
            index=(["", "Seater", "Sleeper", "AC", "NonAC"]).index(st.session_state['selected_bus_type']) if st.session_state['selected_bus_type'] in ["", "Seater", "Sleeper", "AC", "NonAC"] else 0,
            key="selected_bus_type"
        )
        # Update session state after widget creation
        st.session_state['selected_bus_type'] = selected_bus_type  

    col7, col8 = st.columns(2)
    with col7:
        selected_ratings = st.slider(
            "Traveler Ratings",
            0.0, 5.0, st.session_state['selected_ratings'],
            step=0.1,
            key="selected_ratings"
        )
        # Update session state after widget creation
        st.session_state['selected_ratings'] = selected_ratings  

    with col8:
        selected_seats_avail = st.number_input(
            "Seats Availability",
            min_value=min_seats or 0,
            max_value=max_seats or 50,
            value=st.session_state['selected_seats_avail'],
            step=1,
            key="selected_seats_avail"
        )
        # Update session state after widget creation
        st.session_state['selected_seats_avail'] = selected_seats_avail  

    # Set DepartureCond based on selected_departure_time
    DepartureCond = None
    if selected_departure_time == "06:00 - 12:00 Morning":
        DepartureCond = "TIME(departing_time) BETWEEN '06:00:00' AND '12:00:00'"
    elif selected_departure_time == "12:00 - 18:00 Afternoon":
        DepartureCond = "TIME(departing_time) BETWEEN '12:00:00' AND '18:00:00'"
    elif selected_departure_time == "18:00 - 24:00 Evening":
        DepartureCond = "TIME(departing_time) BETWEEN '18:00:00' AND '24:00:00'"
    elif selected_departure_time == "00:00 - 06:00 Night":
        DepartureCond = "TIME(departing_time) BETWEEN '00:00:00' AND '06:00:00'"

    # Set BusTypeCond based on selected_bus_type
    BusTypeCond = None
    if selected_bus_type == "Seater":
        BusTypeCond = "%Seater%"
    elif selected_bus_type == "Sleeper":
        BusTypeCond = "%Sleeper%"
    elif selected_bus_type == "AC":
        BusTypeCond = "%A/C%"
    elif selected_bus_type == "NonAC":
        BusTypeCond = "%Non AC%"

    if st.button("Search"):
        st.subheader("Filtered Results")
        filtered_df = get_filtered_data(
            statename=selected_state,
            route=selected_route,
            operator=selected_operator,
            departure_time=DepartureCond,
            bus_type=BusTypeCond,
            ratings=selected_ratings,
            min_seats=selected_seats_avail,
            max_seats=selected_seats_avail + 1,
            min_fare=selected_bus_fare
        )

        if filtered_df.empty:
            st.write("No results found for the selected filters.")
        else:
            st.dataframe(filtered_df)
