from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import colorama
import math

def wait_find_element(driver, byType, elementID, timeout=20, forceDelay=0, silentPrint=False):
    '''
    Wait for a page element to be viewable and then get it.
    Timeout waiting after a set amount of time if element never can be found (doesn't appear). -1 = never time out.
    Force a delay before looking for an element to prevent cases where finding an element (and then performing an action on it) too quickly can cause unexpected element behaviour.
    '''
    # never time out
    if(timeout < 0):
        timeout = math.inf
    if(forceDelay > 0):
        time.sleep(forceDelay)
    try:
        start = time.time()
        if(not silentPrint): print("Waiting for page to render " + byType + " element: " + elementID)
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((byType, elementID)))
        seconds = str(int(time.time() - start))
        if(not silentPrint): print(byType + " element found after " + seconds + " seconds.")
        return element
    except TimeoutException:
        print(colorama.Fore.RED + "Timed out!")
        print("Either an intentional time out or not able to get a page element because it doesn't exist / page loading took too much time!" + colorama.Style.RESET_ALL)
    except:
        print("Something went wrong when trying to find a page element.")

def print_solveCaptcha(timeout):
    print("\n" + colorama.Fore.GREEN
    + "**"*37
    + "\n"
    + "Solve the captcha and then go to the next page. " + str(timeout) + " seconds until timeout."
    + "\n"
    + "**"*37
    + colorama.Style.RESET_ALL + "\n")

def start_driver(site):
    print(colorama.Fore.RED + "\n*** AVOID MOVING YOUR MOUSE OVER THE WEB PAGE DURING ELEMENT NAVIGATION TO PREVENT UNEXPECTED BEHAVIOUR AND ERRORS ***\n" + colorama.Style.RESET_ALL)
    print("Starting web driver...")
    driver = webdriver.Firefox()
    print("Loading: {}".format(site))
    driver.get(site)
    driver.maximize_window()
    return driver

def wait_for_page(driver, targetIDs):
    '''
    Constantly wait for a page to be loaded which has an ID that is any one of the IDs in a given array.
    This effectively allows the user to use the website without the script interrupting.
    Some pages have a unique screen ID which is shown in the top right corner.
    This ID can be conveniently used to check which page is current, and thus be abused to effectively wait for user input.

    Arguments:
        driver : webdriver obj
            the webdriver object
        targetIDs : str array
            the array of screenIDs to check for
    '''

    if(not isinstance(targetIDs, list)):
        targetIDs = [targetIDs]

    while(True):
        try:
            screenID = driver.find_element(By.ID, 'templateDivScreenId').text
            if(screenID in targetIDs):
                break
        except:
            break


class ScrollPage:
    def TOP(driver):
        driver.execute_script("window.scrollTo(0, 0);")

    def BOTTOM(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
