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
    # Initialize session state variables if not already present
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
        state_options = [""] + states
        # Directly tie the selectbox to session state using the key
        st.selectbox(
            "State Name",
            options=state_options,
            index=state_options.index(st.session_state.selected_state) if st.session_state.selected_state in state_options else 0,
            key='selected_state'
        )

    # Fetch data based on updated state selection
    bus_route = get_route(st.session_state.selected_state) if st.session_state.selected_state else []
    min_fare, max_fare = get_min_max_fare(st.session_state.selected_state)
    min_seats, max_seats = get_min_max_seats(st.session_state.selected_state)

    # Bus Operator Filter
    with col2:
        operator_options = ["", "Government", "Private"]
        # Directly tie the selectbox to session state using the key
        st.selectbox(
            "Bus Operator Pvt/Govt",
            options=operator_options,
            index=operator_options.index(st.session_state.selected_operator) if st.session_state.selected_operator in operator_options else 0,
            key='selected_operator'
        )

    # Additional Filters
    col3, col4 = st.columns(2)
    with col3:
        route_options = [""] + bus_route
        # Directly tie the selectbox to session state using the key
        st.selectbox(
            "Bus Route",
            options=route_options,
            index=route_options.index(st.session_state.selected_route) if st.session_state.selected_route in route_options else 0,
            key='selected_route'
        )
    with col4:
        st.number_input(
            "Bus Fare Range",
            min_value=min_fare or 0.0,
            max_value=max_fare or 10000.0,
            value=st.session_state.selected_bus_fare,
            step=50.00,
            key='selected_bus_fare'
        )

    col5, col6 = st.columns(2)
    with col5:
        departure_time_options = ["", "06:00 - 12:00 Morning", "12:00 - 18:00 Afternoon", "18:00 - 24:00 Evening", "00:00 - 06:00 Night"]
        # Directly tie the selectbox to session state using the key
        st.selectbox(
            "Departure Time",
            options=departure_time_options,
            index=departure_time_options.index(st.session_state.selected_departure_time) if st.session_state.selected_departure_time in departure_time_options else 0,
            key='selected_departure_time'
        )
    with col6:
        bus_type_options = ["", "Seater", "Sleeper", "AC", "NonAC"]
        # Directly tie the selectbox to session state using the key
        st.selectbox(
            "Bus Type:",
            options=bus_type_options,
            index=bus_type_options.index(st.session_state.selected_bus_type) if st.session_state.selected_bus_type in bus_type_options else 0,
            key='selected_bus_type'
        )

    col7, col8 = st.columns(2)
    with col7:
        st.slider(
            "Traveler Ratings",
            0.0, 5.0, st.session_state.selected_ratings, step=0.1, key='selected_ratings'
        )
    with col8:
        st.number_input(
            "Seats Availability",
            min_value=min_seats or 0,
            max_value=max_seats or 50,
            value=st.session_state.selected_seats_avail,
            step=1,
            key='selected_seats_avail'
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
    if st.session_state.selected_bus_type == "Seater":
        BusTypeCond = "%Seater%"
    elif st.session_state.selected_bus_type == "Sleeper":
        BusTypeCond = "%Sleeper%"
    elif st.session_state.selected_bus_type == "AC":
        BusTypeCond = "%A/C%"
    elif st.session_state.selected_bus_type == "NonAC":
        BusTypeCond = "%Non AC%"

    if st.button("Search"):
        st.subheader("Filtered Results")
        filtered_df = get_filtered_data(
            statename=st.session_state.selected_state,
            route=st.session_state.selected_route,
            operator=st.session_state.selected_operator,
            departure_time=DepartureCond,
            bus_type=BusTypeCond,
            ratings=st.session_state.selected_ratings,
            min_seats=st.session_state.selected_seats_avail,
            max_seats=st.session_state.selected_seats_avail + 1,  # Ensure max_seats is greater than min_seats
            min_fare=st.session_state.selected_bus_fare  # Max fare is handled by <= operator
        )

        if filtered_df.empty:
            st.write("No results found for the selected filters.")
        else:
            st.dataframe(filtered_df)

