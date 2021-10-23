from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
import requests


def find_element_xpath(element_type, key, value):
    xpath_variable = "//%s[@%s='%s']" % (element_type, key, value)
    # Find element through values using Xpath
    element = driver.find_element_by_xpath(xpath_variable)
    return element


def find_elements_xpath(element_type, key, value):
    xpath_variable = "//%s[@%s='%s']" % (element_type, key, value)
    # Find element through values using Xpath
    element = driver.find_elements_by_xpath(xpath_variable)
    return element


def presence_element_xpath(element_type, key, value):
    xpath_variable = "//%s[@%s='%s']" % (element_type, key, value)
    # Assure that the element is located in the page
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath_variable))
    )
    return element


def find_elements_class_name(class_name):
    element = driver.find_elements_by_class_name(class_name)
    return element


def web_driver_wait_until_class_name(delay, class_name):
    element = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    return element


def healthcheck(instance):
    healthcheckTrueFalse = True
    health = requests.get(instance + "/sr/healthcheck")
    data = health.json()

    if data['data']['database'] != 'OK':
        healthcheckTrueFalse = False
    elif data['data']['queue'] != 'OK':
        healthcheckTrueFalse = False
    elif data['data']['smartrecruiters'] != 'OK':
        healthcheckTrueFalse = False

    return healthcheckTrueFalse


if __name__ == '__main__':
    # Opens Json instance file
    with open('Instances.json') as json_file:
        json_data = json.load(json_file)

    for instances in json_data:
        # Health check
        if healthcheck(instances['domain']):
            print("HealthCheck Success on " + instances['domain'])
            # Start webpage
            driver = webdriver.Chrome()
            driver.get(instances['domain'])

            try:
                # Make sure that the element is present and located
                presence_element_xpath('input', 'placeholder', 'Password')
            finally:
                # Assert that it has "login: DocQ" on the title
                assert "Login: DocQ" in driver.title

                # Finds user input
                username = find_element_xpath('input', 'placeholder', 'User')
                # Clear user input
                username.clear()
                # Place username from json in user input
                username.send_keys(instances['user'])

                # Finds password input
                password = find_element_xpath('input', 'placeholder', 'Password')
                # Clear password input
                password.clear()
                # Place password from json in user input
                password.send_keys(instances['password'])

                # Click on the login button
                element = find_elements_class_name('btn-login')
                for e in element:
                    e.click()

                # Goes to template page
                driver.get(str(instances['domain']) + "#/templates/main")
                # Delay 3 seconds
                delay = 3

                try:
                    web_driver_wait_until_class_name(delay, 'btn.edit')
                    element = find_elements_class_name('btn.edit')
                    for e in element:
                        e.click()
                        break
                    try:
                        web_driver_wait_until_class_name(delay, 'btn.btn-warning')
                        # Wait for 5 seconds so all the page can load
                        time.sleep(5)
                        element = find_element_xpath('*', 'title', 'Edit variable')
                        element.click()

                    except TimeoutException:
                        print("Loading of edit variable took too much time!")

                except TimeoutException:
                    print("Loading of template took too much time!")

                # Get to the plugin page
                driver.get(instances['domain']+"#/plugins/main")

                try:
                    # Expand the SR Plugin window
                    web_driver_wait_until_class_name(delay, 'btn.btn-warning')
                    # Wait for 5 seconds so all the page can load
                    time.sleep(5)
                    expand_button = find_elements_xpath('*', 'title', 'Expand / Collapse')
                    # finds the SR Plugin expandable button (it will always be the #2 at the moment)
                    index = 0
                    for e in expand_button:
                        if index == 1:
                            e.click()
                        index += 1

                except TimeoutException:
                    print("Not able to expand SR Plugin page")

                try:
                    web_driver_wait_until_class_name(delay, 'btn.btn-warning')
                    time.sleep(5)
                    save_btn = find_elements_xpath('*', 'title', 'Save instance credentials')
                    index = 0
                    for e in save_btn:
                        if index == 1:
                            e.click()
                        index += 1

                except TimeoutException:
                    print("Unable to load Save button")

                print("UX Test Success on " + instances['domain'])
                # Close connection
                driver.close()
        else:
            print("HealthCheck Failure on " + instances['domain'])
