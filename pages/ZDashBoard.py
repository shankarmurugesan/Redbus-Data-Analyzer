import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from DataClean_DB_Insert import create_connection
import seaborn as sns

st.header("DashBoard")
def barchart():
    st.subheader("State-Wise Bus Count: Government vs. Private")

    # Establish a connection to the MySQL database
    mydb = create_connection()
    cursor = mydb.cursor()

    # Define the query to get state-wise bus count, differentiated by government and private
    query = """
    SELECT states, operator, COUNT(busname) AS bus_count
    FROM bus_routes
    GROUP BY states, operator
    """

    # Execute the query
    cursor.execute(query)
    rows = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    mydb.close()

    # Process the results into a DataFrame
    data = {'state': [], 'operator': [], 'bus_count': []}
    for row in rows:
        state, operator, bus_count = row
        data['state'].append(state)
        data['operator'].append(operator)
        data['bus_count'].append(bus_count)

    df = pd.DataFrame(data)

    # Pivot the DataFrame for plotting
    pivot_df = df.pivot(index='state', columns='operator', values='bus_count').fillna(0)

    # Plotting the bar chart using Streamlit's st.bar_chart
    st.bar_chart(pivot_df)

    # For additional customization with matplotlib (optional)
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_df.plot(kind='bar', ax=ax, color=['skyblue', 'lightgreen'])

    # Adding labels and title
    ax.set_xlabel('State')
    ax.set_ylabel('Number of Buses')
    ax.set_title('Count of Buses per State (Government vs Private)')
    ax.legend(title='Bus Type')
    plt.xticks(rotation=45)

    # Display the custom chart using st.pyplot()
    st.pyplot(fig)

def donut_chart():
    st.subheader("State-Wise Distribution of Buses with Ratings Above 4 Stars")
    # Establish a connection to the MySQL database
    mydb = create_connection()
    # Create a cursor object
    cursor = mydb.cursor()

    # Define the query to get state-wise count of buses with more than 4-star ratings
    query = """
    SELECT states, COUNT(busname) AS bus_count
    FROM bus_routes
    WHERE star_rating > 4
    GROUP BY states
    """

    # Execute the query
    cursor.execute(query)

    # Fetch all the results
    rows = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    mydb.close()

    # Check if rows are fetched correctly
    if not rows:
        st.write("No data found.")
        return

    # Process the results into a DataFrame
    data = {'state': [], 'bus_count': []}
    for row in rows:
        state, bus_count = row
        data['state'].append(state)
        data['bus_count'].append(bus_count)

    df = pd.DataFrame(data)

    # Check DataFrame content
    if df.empty:
        st.write("No data available for plotting.")
        return

    # Plotting the donut chart
    fig, ax = plt.subplots(figsize=(10, 6))
    wedges, texts, autotexts = ax.pie(
        df['bus_count'],
        labels=df['state'],
        autopct='%1.1f%%',
        startangle=140,
        colors=plt.get_cmap('tab20').colors
    )

    # Draw a circle at the center to make it a donut chart
    centre_circle = plt.Circle((0, 0), 0.5, fc='white')
    fig.gca().add_artist(centre_circle)

    # Adding labels and title
    plt.title('State-Wise Count of Buses with > 4 Star Ratings')

    # Display the chart using st.pyplot() for Streamlit
    st.pyplot(fig)


# Call the function to display the chart
if __name__ == "__main__":
    barchart()
    donut_chart()

