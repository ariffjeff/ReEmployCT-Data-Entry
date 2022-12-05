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
        print(byType + " element found after " + seconds + " seconds. ({})".format(elementID)) # ignore silentPrint request since printing is ok after wait
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

def wait_for_pages_by_screenID(driver, screenIDs, timeout=math.inf, forceDelay=0, silentPrint=False):
    '''
    Wait for a page with a specific screenID is loaded (HTML element ID: templateDivScreenId) that is any one of the IDs in a given array. Never timesout by default.
    This effectively allows the user to use the website without the script interrupting.
    Some pages have a unique screen ID which is shown in the top right corner.
    This ID can be conveniently used to check which page is current, and thus be abused to effectively wait for user input.

    Arguments:
        driver : webdriver obj
            the webdriver object
        screenIDs : str array
            the array of page's screenIDs to check for
        timeout : int obj
            the time it takes to receive an exception timeout if the page with the screenID could not be found
        forceDelay : int obj
            sleep before performing the wait. useful for not wanting to find an element too quickly in some situations
        silentPrint : bool obj
            if True, do not print a log about looking for the page before doing the wait.
    '''

    if(not isinstance(screenIDs, list) or len(screenIDs) <= 1):
        raise Exception("screenIDs argument must be an array of more than one screenIDs.")
    
    if(forceDelay > 0):
        time.sleep(forceDelay)

    try:
        if(not silentPrint): print("Waiting for any page to render: {}".format(screenIDs))

        expected_conditions = []
        for screenID in screenIDs:
            expected_conditions.append(EC.text_to_be_present_in_element((By.ID, 'templateDivScreenId'), screenID))

        element = WebDriverWait(driver, timeout).until(EC.any_of(*expected_conditions))
        return element
    except TimeoutException:
        print(colorama.Fore.RED + "Timed out!")
        print("Either an intentional time out or not able to get a page element because it doesn't exist / page loading took too much time!" + colorama.Style.RESET_ALL)
    except:
        print("Something went wrong when trying to find a page element.")

def wait_for_page_by_screenID(driver, screenID, timeout=math.inf, forceDelay=0, silentPrint=False):
    '''
    Wait until a page with a specific screenID is loaded (HTML element ID: templateDivScreenId). Never timesout by default.

    Arguments:
        driver : webdriver obj
            the webdriver object
        screenID : str obj
            the page's screenID to check for
        timeout : int obj
            the time it takes to receive an exception timeout if the page with the screenID could not be found
        forceDelay : int obj
            sleep before performing the wait. useful for not wanting to find an element too quickly in some situations
        silentPrint : bool obj
            if True, do not print a log about looking for the page before doing the wait.
    '''
    if(forceDelay > 0):
        time.sleep(forceDelay)
    try:
        if(not silentPrint): print("Waiting for page to render: {}".format(screenID))
        element = WebDriverWait(driver, timeout).until(EC.text_to_be_present_in_element((By.ID, 'templateDivScreenId'), screenID))
        return element
    except TimeoutException:
        print(colorama.Fore.RED + "Timed out!")
        print("Either an intentional time out or not able to get a page element because it doesn't exist / page loading took too much time!" + colorama.Style.RESET_ALL)
    except:
        print("Something went wrong when trying to find a page element.")

class ScrollPage:
    def TOP(driver):
        driver.execute_script("window.scrollTo(0, 0);")

    def BOTTOM(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
