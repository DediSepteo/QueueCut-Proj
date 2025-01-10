import time
import os
import urllib.request
import re
import threading
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from PIL import Image
from bs4 import BeautifulSoup
import html
import tkinter as tk
from tkinter import ttk
import pandas as pd
import json
import urllib

def full_web_scrape(address, link):
    imgInfo = []

    cat_names = []
    dish_names = []
    dish_descs = []
    dish_prices = []
    section_subtitles_arr = []
    group_types_arr = []
    label_names_arr = []
    label_prices_arr = []
    section_titles_arr = []
    section_title_tracker = {}
    dupCount = {}
    # Defining web driver
    options = webdriver.ChromeOptions() 
    prefs = {
    "profile.default_content_setting_values.geolocation": 2  # 1: Allow, 2: Block
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options) 
    driver.maximize_window()
    wait = WebDriverWait(driver, timeout = 15)

    address_for_coords = address.split(",")[0]
    driver.get("https://www.gps-coordinates.net")
    driver.execute_script("window.scrollBy(0, 1000);")

    addressInputID = "address"
    submitBtnXPath = "//button[contains(text(), 'Get GPS Coordinates')]"

    addressInput = driver.find_element(By.ID, addressInputID)
    submitBtn = driver.find_element(By.XPATH, submitBtnXPath)
    latitudeInput = driver.find_element(By.ID, 'latitude')
    longitudeInput = driver.find_element(By.ID, 'longitude')
    coordsFound = False
    for i in range(4):
        ActionChains(driver).move_to_element(addressInput).perform()
        addressInput.clear()
        addressInput.send_keys(address_for_coords)
        time.sleep(1)
        addressInput.send_keys(Keys.ENTER)   
        ActionChains(driver).move_to_element(submitBtn).perform()
        submitBtn.click()
        wait.until(lambda d: addressInput.get_attribute("value") != address_for_coords)
        print(addressInput.get_attribute("value"))
        if "Singapore" in addressInput.get_attribute('value'):
            coordsFound = True
            break
    latitude = float(latitudeInput.get_attribute("value"))
    longitude = float(longitudeInput.get_attribute("value"))
    driver.quit()
    
    options = webdriver.ChromeOptions() 
    driver = webdriver.Chrome(options=options) 
    driver.maximize_window()
    print(latitude, longitude)
    if coordsFound:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "isAccurate": True
        }
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)
        driver.get(link)

        driver.delete_cookie("location")
    
        location_value = {
            "id":"I",
            "latitude":latitude,
            "longitude":longitude,
            "address":"Placeholder",
            "countryCode":"SG",
            "isAccurate":True,
            "addressDetail":"Placeholder",
            "noteToDriver":"","city":"Singapore City","cityID":6,
            "displayAddress":"Extracting..."
        }

        location_value_json = json.dumps(location_value)

        url_encoded_string = urllib.parse.quote(location_value_json)

        location_cookie = {
            "name": "location",
            "value": url_encoded_string,
            # "domain": "food.grab.com",
            "path": "/",
            "sameSite": "None"
        }

        driver.add_cookie(location_cookie)

        driver.refresh()

        # print(driver.get_cookies())

        # locationDivXPath = "//div[contains(@class, 'info')]"
        # locationImgDivXPath = "//div[contains(@class, 'location-icon')]"
        # storeNameClass = "name___1Ls94"
        # locationDiv = driver.find_element(By.XPATH, locationDivXPath)
        # locationDiv.click()   
        # locationImgDiv = driver.find_element(By.XPATH, locationImgDivXPath)
        # locationImgDiv.click()
        # time.sleep(0.5)
        # storeName = driver.find_element(By.CLASS_NAME, storeNameClass)
        # print("Clicked!")
        # wait.until(expected_conditions.invisibility_of_element_located(storeName))
        time.sleep(2)
            
    else:
        driver.get(link)
        # Defining XPaths
        locationDivXPath = "//div[contains(@class, 'info')]"
        locationInputID = "location-input" #//p[contains(@class, 'itemNameTitle')]

        # Clicking on the location div
        locationDiv = driver.find_element(By.XPATH, locationDivXPath)
        locationDiv.click()
        locationInp = driver.find_element(By.ID, locationInputID)
        locationInp.send_keys(address)
        locationInp.send_keys(Keys.ENTER)  
        locationInp.send_keys(Keys.ENTER)
        time.sleep(2)
        locationInp.send_keys(Keys.ENTER)
        time.sleep(1)
    closeBtnXPATH = "//i[contains(@class, 'Close-Button')]"
    dishCatXPATH = "//div[contains(@class, 'category___3C8lX')]"
    storeNameClass = "name___1Ls94"

    dish_cat_elements = driver.find_elements(By.XPATH, dishCatXPATH)
    storeName = driver.find_element(By.CLASS_NAME, storeNameClass).get_attribute("innerHTML")
    for cat in dish_cat_elements:
        disabled = False
        html_content = cat.get_attribute("innerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        cat_elements = soup.find("h2", class_="categoryName___szaKI")
        cat_name = cat_elements.text.strip() if cat_elements else "No Category"
        dishNamesXPATH = f'//div[contains(@id, \"{cat_name}\")]//div[contains(@class, \"menuItemWrapper___1xIAB\")]'
        item_name_elements = driver.find_elements(By.XPATH, dishNamesXPATH)
        for item_name_element in item_name_elements:
            # Check to see if item is disabled
            section_titles = ""
            group_types = ""
            section_subtitles = ""
            label_names = ""
            label_prices_data = ""
            # Extracting inner HTML
            html_content = item_name_element.get_attribute("innerHTML")
            # Parsing HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            try:
                disabledDiv = soup.find("div", class_= "disableOverlay___1mnNv")
                if disabledDiv:
                    disabled = True
            except:
                pass
            if not disabled:
                # Extracting dish information
                dish_info = soup.find("div", class_="menuItemInfo___PyfMY")
                dish_name_elem = dish_info.find("p", class_="itemNameTitle___1sFBq")
                dish_name = dish_name_elem.text.strip() if dish_name_elem else "No Name"
                dish_name = re.sub('[^A-Za-z0-9 ]+', "", dish_name)
                dish_desc_elem = dish_info.find("p", class_="itemDescription___2cIzt")
                dish_desc = dish_desc_elem.text.strip() if dish_desc_elem else "No Description"
                dish_price_elem = dish_info.find("p", class_="discountedPrice___3MBVA")
                dish_price = dish_price_elem.text.strip() if dish_price_elem else "Unknown Price"
                print("\n***************")
                print("Category:", cat_name)
                print("Dish Name:", dish_name)
                print("Dish Description:", dish_desc)
                print("Dish Price: $", dish_price)
                print("***************\n---------------------------------")
                if dish_name not in dish_names:
                    # Clicking on the dish element
                    ActionChains(driver).move_to_element(item_name_element).perform()
                    item_name_element.click()

                    itemImgXPath = f"//div[contains(@class, 'menuBody')]//img"
                    try:
                        itemImg = driver.find_element(By.XPATH, itemImgXPath)
                        print(itemImg)
                        imgInfo.append([itemImg.get_attribute("src"), dish_name])
                    except: 
                        print(f"{dish_name}'s image cannot be found")

                    # Finding option groups
                    optionGroupXPATH = "//div[contains(@class, 'menuBody')]/div[contains(@class, 'section')]"
                    optionGroups = driver.find_elements(By.XPATH, optionGroupXPATH)
                            
                    if optionGroups:
                        for optionGroup in optionGroups:
                            label_name_str = ""
                            label_price_str = ""
                            html_content = optionGroup.get_attribute("innerHTML")
                            soup = BeautifulSoup(html_content, "html.parser")
                            section_title_elem = soup.find('h6', class_='sectionTitle___pw1R4')
                            section_title = section_title_elem.text.strip() if section_title_elem else "Unknown Title"
                            section_subtitle_elem = soup.find('span', class_='sectionSubtitle___2vloa')
                            section_subtitle = section_subtitle_elem.text.strip() if section_subtitle_elem else "Subtitle"
                            print("Section Title:", section_title)
                            print("Section Subtitle:", section_subtitle)    
                            section_title = re.sub('[^A-Za-z0-9 ]+', "", section_title)
                            if section_title.endswith(" "):
                                section_title = section_title[0:-1]
                            section_title = re.sub(r'\s+', ' ', section_title)
                            # Ensure formatting of section_title is consistent
                            if " " in section_title:
                                words = section_title.split(" ")
                                section_title = ""
                                for word in words:
                                    word = word.capitalize()
                                    section_title += word + " "
                                section_title = section_title[0:-1]
                            

                            input_groups = soup.find_all('div', class_=lambda value: value and 'inputGroup___1Rtxr' in value)
                            for input_group in input_groups:
                                if input_group.attrs['class'][0] == 'ant-radio-group':
                                    group_type = 'Radio'
                                elif input_group.attrs['class'][0] == 'ant-checkbox-group':
                                    group_type = 'Checkbox'
                                else:
                                    group_type = 'No Group'
                                    # print('Group Type:', group_type)
                                group_types += group_type + "~~"

                                label_groups = input_group.find_all('div', class_='inputContent___1cvOQ')
                                for label_group in label_groups:
                                    label_text = label_group.find('span', class_='inputContentName___3-Jt8')
                                    label_prices = label_group.find_all('span')
                                    if len(label_prices) > 1 and label_prices[1].text.strip() and not label_prices[1].text.strip().isspace():
                                        label_price = label_prices[1].text.strip()
                                    else:
                                        label_price = '0'
                                    label_name = label_text.text.strip()
                                    # label_name = re.sub('[^A-Za-z0-9 ]+', "", label_name)
                                    label_name_str += label_name + "~~"
                                    label_price_str += label_price + "~~"
                                # if option group with same name exists and has different options as compared to existing option group
                                if section_title in section_title_tracker.keys():
                                    if section_title_tracker[section_title] != label_name_str:
                                        if section_title in dupCount.keys():
                                            dupCount[section_title][0] += 1
                                        else:
                                            dupCount[section_title] = [1, 0]
                                section_title_tracker[section_title] = label_name_str
                                label_name_str = label_name_str[:-2]
                                label_price_str = label_price_str[:-2]
                                label_names += label_name_str + "|"
                                label_prices_data += label_price_str + "|"
                                section_titles += section_title + "~~"
                                section_subtitles += section_subtitle + "~~"

                            

                        section_titles = section_titles[:-2]
                        section_titles_arr.append(section_titles)
                        group_types = group_types[:-2]
                        group_types_arr.append(group_types)
                        section_subtitles = section_subtitles[:-2]
                        section_subtitles_arr.append(section_subtitles)
                        label_names = label_names[:-1]
                        label_names_arr.append(label_names)
                        label_prices_data = label_prices_data[:-1]
                        label_prices_arr.append(label_prices_data)

                    else:
                        print("No options")
                        section_titles_arr.append("")
                        group_types_arr.append("")
                        section_subtitles_arr.append("")
                        label_names_arr.append("")
                        label_prices_arr.append("")

                    # Closing the dish popup
                    closeBtn = driver.find_element(By.XPATH, closeBtnXPATH)
                    time.sleep(0.2)
                    ActionChains(driver).move_to_element(closeBtn).perform()
                    closeBtn.click()         

                    if not disabled:
                        cat_name = re.sub('[^A-Za-z0-9 ]+', "", cat_name)
                        cat_names.append(html.unescape(cat_name))
                        dish_names.append(html.unescape(dish_name))
                        dish_descs.append(html.unescape(dish_desc))
                        dish_prices.append(html.unescape(dish_price))
                        # group_types.append(group_type)  
                    else:
                        cat_names.append("")
                        dish_names.append("")
                        dish_descs.append("")
                        dish_prices.append("")
                        section_titles_arr.append("")
                        group_types_arr.append("")
                        section_subtitles_arr.append("")
                        label_names_arr.append("")
                        label_prices_arr.append("")


    driver.quit()
    # Create DataFrame after loop
    df = pd.DataFrame({
        "Category": cat_names,
        "Dish Name": dish_names,
        "Description": dish_descs,
        "Price": dish_prices,
        "Section Title": section_titles_arr,
        "Option Group Type": group_types_arr,
        "Section Subtitle" : section_subtitles_arr,
        "Button Name": label_names_arr,
        "Option Price": label_prices_arr
    })

    
    fileName = re.sub(r'\W+', '_', storeName)
    fileName = re.sub(r'_+', '_', fileName)
    fileName = fileName.strip('_') + ".xlsx"
    writer = pd.ExcelWriter(fileName, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    dupCount = json.dumps(dupCount)
    df2 = pd.DataFrame({"dupCount":[dupCount]})
    df2.to_excel(writer, index=False, sheet_name="Sheet2")

    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    # Adding format to function 
    red_format = workbook.add_format({'font_color': 'red', 'bold': True, 'font_size': 17})

    # Iterating through cells and identifying "pipe" character
    for row_num, row in enumerate(df.itertuples(), start=1):
        for col_num, value in enumerate(row[1:], start=0):  # row[1:] to skip the Index column
            if isinstance(value, str) and '|' in value:
                parts = value.split('|')
                rich_string = []
                for part in parts[:-1]:
                    rich_string.append(part)
                    rich_string.append(red_format)
                    rich_string.append('|')
                rich_string.append(parts[-1])
                worksheet.write_rich_string(row_num, col_num, *rich_string)
            else:
                worksheet.write(row_num, col_num, value)
    writer.close()

    print(f"{fileName} was created")

    return [imgInfo, storeName]

def downloading_popup(data):
    documents = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents')
    main_folder_path = f'{documents}\\Grab Images'
    storeName = data[1]
    folder_path = main_folder_path + "\\" + storeName

    root2 = tk.Tk()
    root2.title("Image Download Progress")
    root2.geometry("400x100")
    root2.attributes("-topmost", 1)
    progressbar = ttk.Progressbar(root2, orient="horizontal", mode="determinate")
    progressbar.pack(pady=20, padx=20)

    def download_status(count, total_data):
        if count == 1:
            progressbar.configure(maximum=total_data)
        progressbar.step(1)
        if count == total_data:
            print("Images downloaded!")
            root2.destroy()
            window = tk.Tk()
            window.title("Complete")
            window.attributes("-topmost", 1)
            window.geometry("400x100")
            
            # Add a label with the message
            label = tk.Label(window, text="Menu Extraction Finished!", font=("Arial", 12))
            label.pack(pady=20, padx=20)
            
            # Add an "OK" button to close the window
            button = tk.Button(window, text="OK", command=window.destroy, width=20, height=2)
            button.pack(pady=2)
            
            # Run the Tkinter event loop
            window.mainloop()

    def download_imgs(data):
        count = 0
        imgInfo = data[0]
        if not os.path.exists(main_folder_path):
            os.makedirs(main_folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for img in imgInfo:
            count += 1
            itemImgSrc = img[0]
            dish_name = img[1]
            img_name = re.sub('[^A-Za-z0-9]+', "", dish_name) + ".png"
            img_path = folder_path + "\\" + img_name
            urllib.request.urlretrieve(itemImgSrc, img_path)
            img = Image.open(img_path)
            img = img.convert("P", palette=Image.ADAPTIVE)
            img.save(img_path)
            download_status(count, len(imgInfo))

    threading.Thread(target=download_imgs, args=(data,)).start()
    root2.mainloop()

def start_process():
    address = address_entry.get()
    link = link_entry.get()

    if address and link:
        data = full_web_scrape(address, link)
        downloading_popup(data)
    else:
        print("Address and link are required.")

root = tk.Tk()
root.title("grabfood scrape Automation")
root.geometry("500x300")

tk.Label(root, text="Enter the store address:").pack(pady=5)
address_entry = tk.Entry(root, width=50)
address_entry.pack(pady=5)

tk.Label(root, text="Enter the store grabfood link:").pack(pady=5)
link_entry = tk.Entry(root, width=50)
link_entry.pack(pady=5)

start_button = tk.Button(root, text="Start", command=start_process)
start_button.pack(pady=20)

root.mainloop()
