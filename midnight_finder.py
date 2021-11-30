# ---- This script may have a few bugs ----

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import schedule

remove_string = ['st', 'nd', 'rd', 'th']
current_appointment_datetime = datetime(2021, 12, 8, 10, 45, 0)

f_result = open("results.txt", "w")
f = open("info.txt", "r")
last_name_text = f.readline()
license_number_text = f.readline()
keyword_text = f.readline()
location_text_part_one = f.readline()
location_text_part_two = f.readline()

service = Service("chromedriver.exe")
options = webdriver.ChromeOptions()

driver = webdriver.Chrome(service=service, options=options)

def open_webpage():
    driver.get("https://onlinebusiness.icbc.com/webdeas-ui/home")
    driver.maximize_window()

    driver.implicitly_wait(3)
    next_button = driver.find_element_by_class_name("mat-button-wrapper")
    next_button.click()

    last_name = driver.find_element_by_id("mat-input-0")
    last_name.send_keys(last_name_text)

    license_number = driver.find_element_by_id("mat-input-1")
    license_number.send_keys(license_number_text)

    keyword = driver.find_element_by_id("mat-input-2")
    keyword.send_keys(keyword_text)

    box = driver.find_element_by_class_name("mat-checkbox-inner-container")
    box.click()

    sign_in = driver.find_elements_by_class_name("mat-button-wrapper")
    sign_in[1].click()

    driver.implicitly_wait(3)
    reschedule = driver.find_element_by_xpath("//span[contains(text(), 'Reschedule appointment')]")
    reschedule.click()

    driver.implicitly_wait(3)
    yes = driver.find_element_by_xpath("//span[contains(text(), 'Yes')]")
    yes.click()

    time.sleep(1)

    driver.implicitly_wait(3)
    location = driver.find_element_by_id("mat-input-3")
    location.send_keys(location_text_part_one)
    time.sleep(0.75)
    location.send_keys(location_text_part_two)
    time.sleep(0.75)

    driver.implicitly_wait(2)
    drop_down = driver.find_elements_by_class_name("mat-option-text")
    drop_down[0].click()

    search = driver.find_elements_by_class_name("mat-button-wrapper")
    search[4].click()

def refresh_times():
    time_found = False

    driver.implicitly_wait(3)
    nearest_location = driver.find_elements_by_class_name("appointment-location-wrapper")
    driver.execute_script("arguments[0].scrollIntoView();", nearest_location[0])
    driver.execute_script("arguments[0].click();", nearest_location[0])

    driver.implicitly_wait(3)
    times = driver.find_elements_by_class_name("date-title")

    if len(times) == 0:
        time.sleep(0.5)
        nearest_location[0].click()
        time.sleep(1)

    # Loop through available times
    for available_times in times:
        driver.implicitly_wait(3)
        driver.execute_script("arguments[0].scrollIntoView();", available_times)

        # Date string
        string = available_times.text

        # Write to file
        f_result.write(string)

        # Simplify date string
        for remove in remove_string:
            string = string.replace(remove, "")

        if "2022" in string:
            f_result.write(string)
            f_result.write("Aborted because nothing worthy was found.")
            break

        time_button = available_times.find_element_by_xpath(".//../mat-button-toggle/button")
        time_button_text = time_button.find_element_by_xpath(".//div").text

        # Convert everything to datetime
        potential_appointment_date = datetime.strptime(string, "%A, %B %d, %Y")
        potential_appointment_time = datetime.strptime(time_button_text, "%I:%M %p")
        potential_appointment_datetime = datetime.combine(potential_appointment_date.date(), potential_appointment_time.time())

        # If the potential appointment is earlier than the current appointment
        if potential_appointment_datetime < current_appointment_datetime:
            # Print for user information
            print("\n\n --------- Current Appointment Datetime: ", current_appointment_datetime, " ---------")
            print("\n\n --------- New Potential Datetime:       ", potential_appointment_datetime, " ---------\n\n")

            # Select
            driver.execute_script("arguments[0].scrollIntoView();", time_button)
            driver.execute_script("arguments[0].click();", time_button)

            # Break out of loops
            time_found = True
            break

    if time_found:
        driver.implicitly_wait(3)
        review_appointment = driver.find_element_by_xpath("//span[contains(text(), 'Review Appointment')]")
        review_appointment.click()

        time.sleep(1)
        driver.implicitly_wait(3)
        next_button = driver.find_element_by_xpath("//span[contains(text(), 'Next')]")
        next_button.click()

        driver.implicitly_wait(3)
        SMS = driver.find_elements_by_name("otpType")
        time.sleep(0.25)
        SMS[1].click()
        # time.sleep(0.25)

        driver.implicitly_wait(3)
        send_button = driver.find_element_by_xpath("//span[contains(text(), 'Send')]")
        send_button.click()
    else:
        driver.close()
        exit()

schedule.every().day.at('23:59').do(open_webpage)
schedule.every().day.at('00:00').do(refresh_times)

while True:
    schedule.run_pending()
