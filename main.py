from random import random
from pkg_resources import require
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import datetime
import smtplib
from email.message import EmailMessage
import creds

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead+7)

def send_email(x):
    try:
        from_address = creds.from_email
        to_address = creds.email
        subject = "Tennis Reservation"
        body = x
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_address
        msg["To"] = to_address
        msg.set_content(body)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(from_address, creds.from_password)
        server.send_message(msg)
    except Exception as e:
        print("Problem sending email")
        print(e)


def wait_for_element_by_xpath(xpath, time):
    try:
        element = WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except Exception as e:
        print("Could not find element")


def wait_for_element_by_id(id, time):
    try:
        element = WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, id))
        )
        return element
    except Exception as e:
        print("Could not find element.")

def wait_for_element_by_class(class_name, time):
    try:
        element = WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        return element
    except Exception as e:
        print("Could not find element.")


def random_agent():
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value] 

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


wait = 10

user_agent = random_agent()

options = webdriver.FirefoxOptions()
options.headless = True
options.add_argument(f"user-agent={user_agent}")
driver = webdriver.Firefox(
    executable_path="geckodriver",
    options=options,
)
driver.maximize_window()

action = ActionChains(driver)

body = ""
friday = ""

preferred_times = ["11:30am", "11:00am", "12:00pm"]

def reservation():
    # Get the website
    driver.get("https://gtc.clubautomation.com/")

    # Wait for login form to appear
    try:
        wait_for_element_by_id("caSignInLoginForm", wait)
    except:
        print("Did not find the login form.")
        return

    # Input the username/email
    try:
        driver.find_element(By.ID,"login").send_keys(creds.email)
    except:
        print("Error inputting the email.")
        return


    # Input password into the password field
    try:
        driver.find_element(By.ID,"password").send_keys(creds.password)
    except:
        print("Error inputting password.")
        return

    

    # Click the submit button
    try:
        driver.find_element(By.ID,"loginButton").click()
    except:
        print("Unable to submit creds.")
        return

    # Wait for side bar to load
    try:
        wait_for_element_by_id("left_sidebar", wait)
    except:
        print("Unable to find sidebar.")
        return

    # Go to reserve a court menu
    try:
        driver.find_element(By.ID,"menu_reserve_a_court").click()
    except:
        print("Unable to find reserve a court menu in side bar.")
        return

    

    # Wait for reservation page to load
    try:
        wait_for_element_by_id("reserve-court-filter", wait)
    except:
        print("Unable to find search form.")
        return



    # Click the location drop down
    try:
        driver.find_element(By.ID,"location_chosen").click()
    except:
        print("Could not click location picker")
        return

    
    # Select the location
    try:
        lis = driver.find_element(By.ID,"location_chosen").find_element(By.CLASS_NAME,'chosen-results').find_elements(By.TAG_NAME,'li')
        selected_elem = None
        for li in lis:
            if li.text == "Tennis":
                selected_elem = li
                break
        
        if selected_elem == None:
            return
        
        selected_elem.click()
    except:
        print("Couldnt click location as Tennis")
        return

    
    # Find the list of time intervals
    try:
        labels = driver.find_element(By.CLASS_NAME,"l-block").find_elements(By.TAG_NAME, "label")
        # Clicking on the correct time i.e 60 minutes
        required_time_elem = None
        
        for label in labels:
            if label.text == "60 Min":
                required_time_elem = label
                break
            
        ActionChains(driver).move_to_element(required_time_elem).click().perform()     
        
        if required_time_elem == None:
            print("60 minute not found")
            return
        
    except:
        print("Could not find time values.")
        return
    


    # Find the date field
    try:
        date_field = driver.find_element(By.ID, "date")


        # Calculate the date required for booking
        date_full = datetime.datetime.now()

        date_in_format = next_weekday(date_full, 2).strftime('%x')
        date_field.clear()
        date_field.send_keys(date_in_format)

    except:
        print("Could not find the date picker.")
        return

    
    


    # Find the search button
    try:
        driver.find_element(By.ID, "reserve-court-search").click()
    except:
        print("Could not find and click the search button")
        return


    # Get all the the available time slots
    try:
        all_times_available = wait_for_element_by_id("times-to-reserve", wait).find_elements(By.TAG_NAME, "a")


        # Choose the preferred time slot from the list available
        chosen_time = None

        for time in preferred_times:
            for t in all_times_available:
                if time == t.text:
                    chosen_time = t
                    break

            if chosen_time != None:
                break

        chosen_time.click()

    except:
        mail_body = (
            "No reservation available for : "
            + date_in_format
        )
        send_email(mail_body)

        print("Unable to find times")
        return


    


    # Click the confirm button to confirm the booking
    try:
        submit_button = wait_for_element_by_id("confirm",wait)
        sleep(5)
        submit_button.click()
    except:
        print("Unable to finish invoice submission")
        return
    

    mail_body = "Booking confirmed for: " + date_in_format + " at " + chosen_time.text

    send_email(mail_body)


    driver.close()
    return

reservation()

try:
    driver.close()
except:
    print("Already closed")