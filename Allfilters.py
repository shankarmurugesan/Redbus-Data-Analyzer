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

def get_min_max_fare(state=None):
    if state is None:
        return None, None
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

def get_min_max_seats(state=None):
    if state is None:
        return None, None
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
    query = "SELECT * FROM bus_routes WHERE 1=1"
    params = []

    if statename:
        query += " AND states = %s"
        params.append(statename)
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
    # Initialize session state for all dropdowns and inputs
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

    # Initialize state options
    states = get_state()

    # Select State Filter
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.selected_state = st.selectbox(
            "State Name", 
            options=[""] + states, 
            index=states.index(st.session_state.selected_state) + 1 if st.session_state.selected_state in states else 0
        )

    # Other filters are independent of the selected state
    with col2:
        st.session_state.selected_operator = st.selectbox(
            "Bus Operator Pvt/Govt", 
            options=["", "Government", "Private"], 
            index=["", "Government", "Private"].index(st.session_state.selected_operator)
        )

    # Fetch data based on state selection for dependent filters
    bus_route = get_route(st.session_state.selected_state) if st.session_state.selected_state else []
    min_fare, max_fare = get_min_max_fare(st.session_state.selected_state)
    min_seats, max_seats = get_min_max_seats(st.session_state.selected_state)

    # Show additional filters regardless of state selection
    col3, col4 = st.columns(2)
    with col3:
        st.session_state.selected_route = st.selectbox(
            "Bus Route", 
            options=[""] + bus_route,
            index=bus_route.index(st.session_state.selected_route) + 1 if st.session_state.selected_route in bus_route else 0
        )
    with col4:
        st.session_state.selected_bus_fare = st.number_input(
            "Bus Fare Range",
            min_value=min_fare or 0.0,
            max_value=max_fare or 10000.0,
            value=st.session_state.selected_bus_fare,
            step=50.00
        )

    col5, col6 = st.columns(2)
    with col5:
        st.session_state.selected_departure_time = st.selectbox(
            "Departure Time", 
            options=["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"],
            index=["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"].index(st.session_state.selected_departure_time)
        )
    with col6:
        st.session_state.selected_bus_type = st.selectbox(
            "Bus Type:", 
            options=["", "Seater", "Sleeper", "AC", "NonAC"],
            index=["", "Seater", "Sleeper", "AC", "NonAC"].index(st.session_state.selected_bus_type)
        )

    col7, col8 = st.columns(2)
    with col7:
        st.session_state.selected_ratings = st.slider(
            "Traveler Ratings", 
            0.0, 5.0, 
            st.session_state.selected_ratings, 
            step=0.1
        )
    with col8:
        st.session_state.selected_seats_avail = st.number_input(
            "Seats Availability",
            min_value=min_seats or 0,
            max_value=max_seats or 50,
            value=st.session_state.selected_seats_avail,
            step=1
        )

    # Prepare condition for query
    DepartureCond = None
    if st.session_state.selected_departure_time == "06:00 - 12:00 Morning":
        DepartureCond = "TIME(departing_time) BETWEEN '06:00:00' AND '12:00:00'"
    elif st.session_state.selected_departure_time == "12:00 - 18:00 Afternoon":
        DepartureCond = "TIME(departing_time) BETWEEN '12:00:00' AND '18:00:00'"
    elif st.session_state.selected_departure_time == "18:00 - 24:00 Evening":
        DepartureCond = "TIME(departing_time) BETWEEN '18:00:00' AND '24:00:00'"
    elif st.session_state.selected_departure_time == "00:00 - 06:00 Night":
        DepartureCond = "TIME(departing_time) BETWEEN '00:00:00' AND '06:00:00'"

    BusTypeCond = None
    if st.session_state.selected_bus_type:
        BusTypeCond = "%" + st.session_state.selected_bus_type + "%"

    df = get_filtered_data(
        statename=st.session_state.selected_state,
        route=st.session_state.selected_route,
        operator=st.session_state.selected_operator,
        departure_time=DepartureCond,
        bus_type=BusTypeCond,
        ratings=st.session_state.selected_ratings,
        min_seats=st.session_state.selected_seats_avail,
        min_fare=st.session_state.selected_bus_fare
    )

    st.write("Total Filtered Buses: ", len(df))
    if not df.empty:
        st.dataframe(df)

