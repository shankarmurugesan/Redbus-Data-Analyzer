import mysql.connector
from mysql.connector import Error
import streamlit as st
import pandas as pd
import os

# Establish a connection to the MySQL database
def create_connection():
    try:
        mydb = mysql.connector.connect(
            host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
            port="4000",
            user="3dThprF9Dbe3P8c.root",
            password="IDtIXLlb6Io3Lh87",  
            database="redbus",
        )
        if mydb.is_connected():
            return mydb
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None
def datacleandbinsert(statename):
    # Set the correct path to the directory
    directory = f'D:/Project/'  # Update the path here

    # Check if the directory exists
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The directory '{directory}' does not exist.")

    # List all Excel files in the directory that contain the statename and end with .xlsx
    excel_files = [f for f in os.listdir(directory) if statename in f and f.endswith('.xlsx')]

    if not excel_files:
        raise FileNotFoundError(f"No Excel files found for {statename} in '{directory}'.")

    # Get the full file paths
    excel_files_full_path = [os.path.join(directory, f) for f in excel_files]

    # Find the Excel file with the latest modification time
    latest_file = max(excel_files_full_path, key=os.path.getmtime)

    # Read the latest Excel file into a pandas DataFrame
    df = pd.read_excel(latest_file)

    # Process the DataFrame as needed
    print(f"Imported file: {latest_file}")

    # Keep only the first 3 characters in the star_rating column
    df['star_rating'] = df['star_rating'].astype(str).str[:3]

    # Keep only Original price after discount
    df['price'] = df['price'].astype(str).apply(lambda x: x.split()[-1])

    # Create the 'operator' column based on the 'busname' field
    prefixes = ('KAAC', 'RSRTC','Bihar','Kadamba','HRTC','JKRTC','PEPSU','SBSTC','WBTC','NBSTC','WBSTC','West bengal','NBSRTC','RSRTC')  # List of prefixes
    df['operator'] = df['busname'].apply(lambda x: 'Government' if isinstance(x, str) and x.startswith(prefixes) else 'Private')

    # Drop rows where any of the required columns are empty
    required_columns = ['busname', 'bustype', 'departing_time', 'duration', 'reaching_time', 'star_rating', 'price', 'seat_availability', 'route_name']
    df = df.dropna(subset=required_columns)

    print(df.head())

    # Insert cleaned data into MySQL table 'bus_routes'
    try:
        # Establish a connection to the MySQL database
        mydb = create_connection()
        cursor = mydb.cursor()

        # Define the state to clean up
        state_to_clean = df['state'].iloc[0]  # Assuming all rows have the same state

        # Define the delete query to remove existing data for the state
        delete_query = """
            DELETE FROM bus_routes WHERE state = %s
        """
        # Execute the delete query
        cursor.execute(delete_query, (state_to_clean,))
        print(f"Existing records for state '{state_to_clean}' removed from bus_routes table.")

        # Define the insert query
        insert_query = """
            INSERT INTO bus_routes (
                busname, bustype, departing_time, duration, reaching_time, star_rating,
                price, seats_available, route_name, route_link, state, operator
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

        # Replace NaN with None in the DataFrame
        #df = df.where(pd.notnull(df), None)

        # Insert data into the table
        for index, row in df.iterrows():
            cursor.execute(insert_query, (
                row['busname'], row['bustype'], row['departing_time'], row['duration'],
                row['reaching_time'], row['star_rating'], row['price'],
                row['seat_availability'], row['route_name'], row['route_link'],
                row['state'], row['operator']
            ))
        # Commit the transaction
        mydb.commit()

        #print("Data inserted successfully into bus_routes table.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        cursor.close()
        mydb.close()
