import os
import time
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from DataClean_DB_Insert import datacleandbinsert
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options

def scrabdata(unique_key):
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"  # Specify the path to Firefox binary


    # Determine state-specific details
    state_map = {
        "Chandigarh_CTU": ("chandigarh-transport-undertaking-ctu", "Chandigarh"),
        "Jammu_JKSRTC": ("jksrtc", "Jammu"),
        "Bihar_BSRTC": ("bihar-state-road-transport-corporation-bsrtc", "Bihar"),
        "North_Bengal_NBSRTC": ("north-bengal-state-transport-corporation", "North_Bengal"),
        "Assam_KAAC": ("kaac-transport", "Assam"),
        "Goa_KTCL": ("ktcl", "Goa"),
        "South_Bengal_SBSTC": ("south-bengal-state-transport-corporation-sbstc", "South_Bengal"),
        "West_Bengal_WBTC": ("west-bengal-transport-corporation", "West_Bengal"),
        "Haryana_HRTC": ("hrtc", "Haryana"),
    }

    stateroute, statename = state_map.get(unique_key, ("pepsu", "Punjab"))
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(f'https://www.redbus.in/online-booking/{stateroute}/?utm_source=rtchometile')
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)  # Increase wait time for stability

    # Collect route names and links
    all_route_names = []
    all_route_links = []
    j = 1
    while True:
        print(f"Page {j}")
        route_elements = driver.find_elements(By.CSS_SELECTOR, "a.route")
        for element in route_elements:
            route_name = element.text
            route_link = element.get_attribute('href')
            if route_name not in all_route_names:  # Avoid duplicates
                all_route_names.append(route_name)
                all_route_links.append(route_link)

        try:
            next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "DC_117_pageTabs") and text()="{j + 1}"]')))
            actions = ActionChains(driver)
            actions.move_to_element(next_page_button).perform()
            time.sleep(2)
            next_page_button.click()
            j += 1
        except Exception as e:
            print(f"Could not move to the next page: {e}")
            break

    routes = list(zip(all_route_names, all_route_links))
    print(f"Total routes found: {len(routes)}")

    # Collect bus information from route links
    bus_data = []
    seen_buses = set()  # Set to track unique bus records

    for route_name, url in routes:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bus-items')))

            # Check for all "View Buses" buttons and click each one if available
            try:
                # Find all elements matching the "View Buses" button
                view_bus_buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[contains(@class, "button") and contains(text(), "View Buses") and .//i[contains(@class, "icon-down")]]')))
                for button in view_bus_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(2)  # Wait for the bus details to load
                # After clicking all "View Buses" buttons, proceed to scrape the page
                # Add your scraping logic here
            except Exception as e:
                print(f"Error interacting with 'View Buses' buttons: {e}")

            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                buses = driver.find_elements(By.CSS_SELECTOR, '.bus-items .clearfix')
                if not buses:
                    print(f"No buses found for route: {route_name}")
                    break

                for bus in buses:
                    try:
                        bus_info = {
                            "busname": bus.find_element(By.CSS_SELECTOR, 'div[class*="travels"]').text,
                            "bustype": bus.find_element(By.CSS_SELECTOR, 'div[class*="bus-type"]').text,
                            "departing_time": bus.find_element(By.CSS_SELECTOR, 'div[class*="dp-time"]').text,
                            "duration": bus.find_element(By.CSS_SELECTOR, 'div[class*="dur"]').text,
                            "reaching_time": bus.find_element(By.CSS_SELECTOR, 'div[class*="bp-time"]').text,
                            "star_rating": bus.find_element(By.CSS_SELECTOR, 'div[class*="column-six"]').text,
                            "price": bus.find_element(By.CSS_SELECTOR, 'div[class*="seat-fare"]').text,
                            "seat_availability": bus.find_element(By.CSS_SELECTOR, 'div[class*="column-eight"]').text,
                            "route_name": route_name,
                            "route_link": url,
                            "state": statename
                        }

                        # Create a unique key for the bus_info
                        bus_key = (
                        bus_info["busname"], bus_info["departing_time"], bus_info["route_name"], bus_info["bustype"],
                        bus_info["reaching_time"])

                        if bus_key not in seen_buses:
                            seen_buses.add(bus_key)
                            bus_data.append(bus_info)

                    except Exception as e:
                        print(f"Error extracting bus details for {route_name}: {e}")

                # Scroll down to load more buses
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for the page to load
                new_height = driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:
                    try:
                        load_more_button = driver.find_element(By.XPATH, '//button[contains(text(), "Load More")]')
                        if load_more_button.is_displayed():
                            load_more_button.click()
                            time.sleep(2)  # Wait for the new buses to load
                        else:
                            break
                    except Exception as e:
                        print(f"Load More button not found or not clickable: {e}")
                        break
                last_height = new_height

            print("-" * 40)

        except Exception as e:
            print(f"Error loading page for route {route_name}: {e}")

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(bus_data)

    # Get the current date and time
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H-%M-%S")

    # Define the folder name and file path
    folder_name = "D:/Project"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Define the file path with the current date and time
    file_path = os.path.join(folder_name, f"{statename}_{current_date}_{current_time}.xlsx")

    # Check for existing files created within the last 10 seconds
    file_created_within_10s = False
    for file in os.listdir(folder_name):
        if file.startswith(f"{statename}_{current_date}"):
            file_path_check = os.path.join(folder_name, file)
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path_check))
            if now - file_mod_time <= timedelta(seconds=10):
                file_created_within_10s = True
                break

    if file_created_within_10s:
        print("File already present from the last 10 seconds. Please try again later.")
    else:
        # Save the DataFrame to an Excel file
        df.to_excel(file_path, index=False)
        print(f"Data saved to {file_path}")

    # Close the driver
    driver.quit()

    #calling data clean file function
    datacleandbinsert(statename)
