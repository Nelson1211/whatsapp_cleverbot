from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time 
from os import path

browser = None
message = None
current_tab = None
new_tab = None
Link = "https://web.whatsapp.com/"
Link_bot = "http://www.cleverbot.com/"

def whatsapp_login():
    global wait, browser, Link, current_tab, new_tab
    chrome_options = Options()
    chrome_options.add_argument('--user-data-dir=./User_Data')
    browser = webdriver.Chrome('/Users/nelson/Downloads/ChatBotSample/chromedriver', options=chrome_options)
    wait = WebDriverWait(browser, 600)
    browser.get(Link)
    current_tab = browser.current_window_handle
    browser.execute_script('window.open("http://www.cleverbot.com/");')
    new_tab = [tab for tab in browser.window_handles if tab != current_tab][0]
    browser.switch_to.window(current_tab)
        
def check_exists_by_xpath(xpath):
    global browser
    try:
        browser.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def check_new_messages():
    global browser
    try:
        browser.find_element_by_xpath("//span[contains(@class,'P6z4j')]")
    except NoSuchElementException:
        return False
    return True

def store_transcripts(target, message, flag):
    filename = "transcripts/{}.txt".format(target)
    if path.exists(filename):
        f=open(filename, "a+")
        if flag == 0:
            f.write("Incoming: {}\r\n".format(message))
        else:
            f.write("Outgoing: {}\r\n".format(message))
    else:
        f=open(filename, "w+")
        if flag == 0:
            f.write("Incoming: {}\r\n".format(message))
        else:
            f.write("Outgoing: {}\r\n".format(message))

def get_targets():
    global browser
    browser.refresh()
    time.sleep(5)
    reply_user = browser.find_elements_by_xpath("//span[contains(@dir,'auto')]")
    limit = len(reply_user) - 5
    ptr = 0
    targets = []
    for i in range(len(reply_user), 0, -1):
        if i == len(reply_user):
            ptr = 0
        else:
            ptr = i
        reply_user[ptr].click()
        time.sleep(1)
        message_queue = browser.find_elements_by_xpath("//div[starts-with(@class,'FTBzM')]")
        if message_queue[-1].get_attribute('class').endswith('message-in'):
            target = reply_user[ptr].get_attribute('title')
            if target != '' and len(target.split(' ')) <= 2:
                targets.append(target)
        if i == limit:
            return targets

def check_reply_and_reply():
    global browser
    targets = get_targets()
    if targets != None:
        for target in targets:
            print(target)
            x_arg = "//span[contains(@title,'{}')]".format(target)
            send_to = browser.find_element_by_xpath(x_arg)
            send_to.click()
            message_queue = browser.find_elements_by_xpath("//div[starts-with(@class,'FTBzM')]")
            first_reply = 0
            target_message = ''
            for j in range(len(message_queue) - 1, -1, -1):
                if not message_queue[j].get_attribute('class').endswith('message-in'):
                    first_reply = j+1
                    break
            if len(target.split()) <= 2:
                for j in range(first_reply, len(message_queue)):
                    message_queue = browser.find_elements_by_xpath("//div[starts-with(@class,'FTBzM')]")
                    message_queue = message_queue[j].find_elements_by_xpath(".//*")[1]
                    message_queue = message_queue.find_elements_by_xpath(".//div[contains(@class,'-N6Gq')]")[0]
                    for i in range(4):
                        message_queue = message_queue.find_elements_by_xpath(".//*")[0]
                    target_message += message_queue.text.replace("\n", ", ").strip()
                    target_message += " "
            if target_message != '':
                store_transcripts(target, target_message, 0)
                if len(target_message) > 0:
                    send_message(target,target_message)

def get_message():
    global browser
    time.sleep(3)
    check_reply_and_reply()
    time.sleep(3)
    get_message()

def send_message(target, message):
    global wait, browser, current_tab, new_tab
    browser.switch_to.window(new_tab)
    input_bot = browser.find_element_by_xpath('//*[@id="avatarform"]/input[1]')
    for ch in message:
        if ch == "\n":
            ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.BACKSPACE).perform()
        else:
            input_bot.send_keys(ch)
    input_bot.send_keys(Keys.ENTER)
    time.sleep(8)
    output_bot = browser.find_element_by_xpath('//*[@id="line1"]/span[1]')
    reply = output_bot.text
    browser.switch_to.window(current_tab)
    x_arg = "//span[contains(@title,'{}')]".format(target)
    send_to = browser.find_element_by_xpath(x_arg)
    send_to.click()
    input_box = browser.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
    for ch in reply:
        if ch == "\n":
            ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.BACKSPACE).perform()
        else:
            input_box.send_keys(ch)
    input_box.send_keys(Keys.ENTER)
    store_transcripts(target, reply, 1)
    print("Message sent successfully")
    time.sleep(3)
    get_message()

if __name__ == "__main__":

    print("Web Page Open")

    whatsapp_login()
    time.sleep(3)
    get_message()
    browser.quit()
