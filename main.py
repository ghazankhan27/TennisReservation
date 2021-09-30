from selenium import webdriver
import time
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


def send_email(x):
    try:
        from_address = "gtc.Clubautomation@gmail.com"
        to_address = "david.hahn@gmail.com"
        subject = "Tennis Reservation"
        body = x
        msg = EmailMessage()
        msg["Subject"] = "Tennis Reservation"
        msg["From"] = from_address
        msg["To"] = to_address
        msg.set_content(body)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(from_address, "clubautomation1234")
        server.send_message(msg)
    except Exception as e:
        print(e)
        driver.close()


def wait_for_element_by_xpath(xpath, time):
    try:
        element = WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except Exception as e:
        return None


def wait_for_element_by_id(id, time):
    try:
        element = WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, id))
        )
        return element
    except Exception as e:
        return None


def get_random_user_agent():
    software_names = [SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value]

    user_agent_rotator = UserAgent(
        software_names=software_names, operating_systems=operating_systems, limit=100
    )
    user_agents = user_agent_rotator.get_user_agents()

    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


wait = 10

user_agent = get_random_user_agent()

options = webdriver.FirefoxOptions()
options.headless = False
options.add_argument(f"user-agent={user_agent}")
driver = webdriver.Firefox(
    executable_path=r"E:\Projects\PythonProjects\TennisReservation\geckodriver.exe",
    options=options,
)
driver.maximize_window()

action = ActionChains(driver)

body = ""
friday = ""


def reservation():
    # Get the website
    driver.get("https://gtc.clubautomation.com/")

    # Wait for login form to appear
    wait_for_element_by_id("signin_login_form", wait)

    # Input the username/email
    input_username = driver.find_element_by_xpath(
        "//form[@id='signin_login_form']//input[@value='Username']"
    )
    input_username.send_keys("david.hahn@gmail.com")

    # Find the password field
    password_text = driver.find_element_by_id("password-text")
    ActionChains(driver).move_to_element(password_text).click().perform()

    # Input password into the password field
    driver.find_element_by_id("password").send_keys("Strategos4!")

    # Click the submit button
    driver.find_element_by_xpath("//div[@class='buttons-group-wrapper']//a[2]").click()

    # Wait for side bar to load
    wait_for_element_by_id("left_sidebar", wait)

    # Go to reserve a court menu
    driver.find_element_by_id("menu_reserve_a_court").click()

    # Wait for reservation page to load
    wait_for_element_by_id("reserve-court-filter", wait)

    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    # Choose the time interval 60
    time_intervals = driver.find_element_by_class_name(
        "l-block"
    ).find_elements_by_tag_name("label")
    time_interval = time_intervals[2]
    ActionChains(driver).move_to_element(time_interval).click().perform()

    # Open the date picker
    driver.find_element_by_class_name("ca-date-picker-field").click()
    weeks = driver.find_element_by_class_name(
        "datepickerDays"
    ).find_elements_by_tag_name("tr")

    # Calculate the date we want to choose
    today = datetime.date.today()
    friday = today + datetime.timedelta((4 - today.weekday()) % 7 + 7)

    # Choose the correct date from datepicker
    for week in weeks:
        dates = week.find_elements_by_tag_name("td")

        for date in dates:
            my_date = str(date.find_element_by_tag_name("span").text)
            if my_date == str(friday.day):
                required_date = date
                break

    ActionChains(driver).move_to_element(required_date).click().perform()

    # Click the search button
    driver.find_element_by_id("reserve-court-search").click()

    # Wait for available options
    tennis_reserve_times = wait_for_element_by_id("times-to-reserve", wait)

    # If times are available then choose the preferred time
    if tennis_reserve_times != None:

        tennis_reserve_times = tennis_reserve_times.find_elements_by_tag_name("td")
        times = ""

        for t in tennis_reserve_times:
            x = t.find_element_by_tag_name("b").text

            if x == "Tennis":
                times = t.find_elements_by_tag_name("a")

        if times != "":

            required_time = ""
            found = False

            my_pr_list = [0, 0, 0]

            for t in times:

                x = t.text

                if "8:30am" in x:
                    my_pr_list.insert(0, t)
                    found = True
                elif "8:00am" in x:
                    my_pr_list.insert(1, t)
                    found = True
                elif "9:00am" in x:
                    my_pr_list.insert(2, t)
                    found = True
                else:
                    next

            if found:
                for i in my_pr_list:
                    if i != 0:
                        required_time = i
                        break
                required_time.click()
                submit_button = wait_for_element_by_id("confirm", wait)
                msg_items = (
                    driver.find_element_by_id("confirm-reservation-popup")
                    .find_element_by_class_name("content")
                    .find_elements_by_tag_name("tr")
                )
                body = "Reserved:\n"
                i = 0

                for msg_item in msg_items:
                    if i != 2:
                        x = str(msg_item.find_element_by_tag_name("th").text)
                        body += x + " : "
                        y = str(msg_item.find_element_by_tag_name("td").text)
                        body += y + "\n"
                    else:
                        i += 1
                        next
                    i += 1

                # Click reserve and send email to user with time and date of reservation
                submit_button.click()
                time.sleep(10)
                send_email(body)

            else:
                day_text = friday.strftime("%A")
                day = friday.day
                month = friday.strftime("%B")
                year = friday.year
                mail_body = (
                    "No reservation available for : "
                    + day_text
                    + " "
                    + str(day)
                    + ", "
                    + str(month)
                    + ", "
                    + str(year)
                )
                send_email(mail_body)

        else:
            day_text = friday.strftime("%A")
            day = friday.day
            month = friday.strftime("%B")
            year = friday.year
            mail_body = (
                "No reservation available for : "
                + day_text
                + " "
                + str(day)
                + ", "
                + str(month)
                + ", "
                + str(year)
            )
            send_email(mail_body)

    else:
        day_text = friday.strftime("%A")
        day = friday.day
        month = friday.strftime("%B")
        year = friday.year
        mail_body = (
            "No reservation available for : "
            + day_text
            + " "
            + str(day)
            + ", "
            + str(month)
            + ", "
            + str(year)
        )
        send_email(mail_body)

    driver.close()


reservation()
