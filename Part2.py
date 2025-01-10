import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import tkinter as tk
import pyautogui
import pandas as pd
import pyperclip
from tkinter import filedialog
import json

## All the xpath in the code below is base on the staging web, so if there is any difference from the staging and production, pls change accrodingly

def upload_img(imgPath, addImgBtn):
    print(os.path.isfile(imgPath))
    if (os.path.isfile(imgPath)):
        pyperclip.copy(imgPath)
        addImgBtn.click()
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter') 

def automation_process():

    excelPath = excel_path

    dataDF = pd.read_excel(excelPath, sheet_name=0)
    dataDF = dataDF[dataDF["Dish Name"].notna()]

    dupCount = pd.read_excel(excelPath, sheet_name=1)["dupCount"][0]
    dupCount = json.loads(dupCount)
    print(dupCount)

    ### Loading up driver options

    options = webdriver.ChromeOptions() 
    driver = webdriver.Chrome(options=options) 
    driver.maximize_window()
    wait = WebDriverWait(driver, timeout = 5)

    ## Change the url to the production once approve to rollout for production
    driver.get("https://queuecuts.com:444")
    ##

    emailInputID = "Email"
    passwordInputID = "id_password"
    submitBtnXPath = "//button[@type='submit']"

    emailInput = driver.find_element(By.ID, emailInputID)
    passwordInput = driver.find_element(By.ID, passwordInputID)
    submitBtn = driver.find_element(By.XPATH, submitBtnXPath)

    wait.until(lambda d: submitBtn.is_displayed())
    emailInput.send_keys(email)
    passwordInput.send_keys(password)
    submitBtn.click()

    storeSelectID = "selectStore"

    storeSelect = Select(driver.find_element(By.ID, storeSelectID))
    storeSelect.select_by_visible_text(store)

    ## Change the url to the production once approve to rollout for production
    driver.get("https://queuecuts.com:444/YourStore/EditStore")

    menuBtnXPath = "//main[1]//div[1]//a[2]" # Change according to html 
    menuInputID = "menu_Name"
    menuDescID = "menu_Description"

    menuBtn = driver.find_element(By.XPATH, menuBtnXPath) 
    menuBtn.click()

    
    menuInput = driver.find_element(By.ID, menuInputID)
    if menuInput.is_displayed():
        menuDesc = driver.find_element(By.ID, menuDescID)
        wait.until(lambda d: menuInput.is_displayed())

        menuInput.send_keys("Menu")
        menuDesc.send_keys("-")

        menuSubmit = driver.find_element(By.TAG_NAME, "form").find_element(By.TAG_NAME, "button")
        menuSubmit.click()
    else:
        print("Menu already created")

    # Automate uploading of food items

    addCatBtnXPath = "//a[text() = 'Add Food Category']"
    addImgBtnID = "output"
    foodNameInputID = "food_Name"
    foodCategoryInputID = "food_Category"
    foodPriceInputID = "food_Start_Price"
    foodTakeawayInputID = "food_Takeaway_Fee"
    foodPrepareInputID = "food_Prepare_Time"
    foodDescInputID = "food_Description"
    submitBtnXPath = "//button[@type='submit']"
    menuBackBtnXPath = "//form//a[1]"


    for index in dataDF.index:
        AddCatBtn = driver.find_element(By.XPATH, addCatBtnXPath)
        pyautogui.press('end')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, addCatBtnXPath)))
        time.sleep(0.5)
        AddCatBtn.click()
        wait.until(expected_conditions.presence_of_element_located((By.ID, addImgBtnID)))

        addImgBtn = driver.find_element(By.ID, addImgBtnID)
        foodNameInput = driver.find_element(By.ID, foodNameInputID)
        foodCategoryInput = driver.find_element(By.ID, foodCategoryInputID)
        foodPriceInput = driver.find_element(By.ID, foodPriceInputID)
        foodTakeawayInput = driver.find_element(By.ID, foodTakeawayInputID)
        foodPrepareInput = driver.find_element(By.ID, foodPrepareInputID)
        foodDescInput = driver.find_element(By.ID, foodDescInputID)
        submitBtn = driver.find_element(By.XPATH, submitBtnXPath)

        imgName = re.sub('[^A-Za-z0-9]+', "", dataDF['Dish Name'][index])
        print(imgName)
        documents = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents') 
        folder_path = f'{documents}\Grab Images\{folderName}'
        imgPath = f"{folder_path}\{imgName}.png"
        imgPath = imgPath.replace("/", "\\")
        imgPath = imgPath.replace('\n', '')
        print(imgPath)
        upload_img(imgPath, addImgBtn)
        
        foodNameInput.send_keys(dataDF["Dish Name"][index])
        foodCategoryInput.send_keys(dataDF["Category"][index])
        foodPriceInput.send_keys(dataDF["Price"][index])
        foodTakeawayInput.send_keys(0)
        foodPrepareInput.send_keys(15)
        foodDescInput.send_keys(dataDF["Description"][index])

        ActionChains(driver).move_to_element(submitBtn).perform()
        wait.until(lambda d: submitBtn.is_displayed())
        submitBtn.click()
        
        wait.until(expected_conditions.presence_of_element_located((By.XPATH, menuBackBtnXPath)))
        menuBackBtn = driver.find_element(By.XPATH, menuBackBtnXPath)
        wait.until(lambda d: menuBackBtn.is_displayed())
        menuBackBtn.click()

    # Automate uploading of option groups

    optionData = []

    optionGrpDFNames = list(dataDF["Section Title"][dataDF["Section Title"].notna()])
    optionGrpDFTypes = list(dataDF["Option Group Type"][dataDF["Option Group Type"].notna()])
    optionGrpDFSpecs = list(dataDF["Section Subtitle"][dataDF["Section Subtitle"].notna()])
    optionGrpDFButtons = list(dataDF["Button Name"][dataDF["Button Name"].notna()])
    optionGrpDFPrices = list(dataDF["Option Price"][dataDF["Option Price"].notna()])

    for i in range(len(optionGrpDFNames)):
        optionGrpNames = optionGrpDFNames[i].split("~~")
        optionGrpTypes = optionGrpDFTypes[i].split("~~")
        optionGrpSpecs = optionGrpDFSpecs[i].split("~~")
        optionNames = optionGrpDFButtons[i].split("|")
        optionPrices = optionGrpDFPrices[i].split("|")
            
        for j in range(len(optionGrpNames)):
            # Clean option names and prices to remove empty strings
            cleaned_optionNames = [name for name in optionNames[j].split("~") if name.strip() != ""]
            cleaned_optionPrices = [price for price in optionPrices[j].split("~") if price.strip() != ""]
                    
            optionData.append([optionGrpNames[j], optionGrpTypes[j], optionGrpSpecs[j], cleaned_optionNames, cleaned_optionPrices])

    createdOptionGrps = []


    optionGrpBtnXPath = "//main//ul//li[2]//a"
    addOptionGrpBtnXPath = "//a[@href='/Menu/AddOptionGroup']"
    groupNameInputID = "opt_Grp_Name"   
    optionGrpTypeID = "opt_Grp_Type"
    optionGrpMandID = "opt_Grp_IsMandatory"
    optionMinInputID = "opt_Grp_Min"
    optionMaxInputID = "opt_Grp_Max"
    createBtnXPath = "//form//button"
    addOptionBtnXPath = "//a[contains(@href, '/Menu/AddNewOption')]"

    wait.until(expected_conditions.presence_of_element_located((By.XPATH, optionGrpBtnXPath)))
    optionGrpBtn = driver.find_element(By.XPATH, optionGrpBtnXPath)
    wait.until(lambda d: optionGrpBtn.is_displayed())
    optionGrpBtn.click()

    for data in optionData:
        optionGrp = data[0]
        data = {
            "GroupName": optionGrp,
            "DropDown": data[1],
            "Section Subtitle": data[2],
            "OptionNames": data[3],
            "OptionPrices": data[4]
            }
        if [data['GroupName'], data['OptionNames']] not in createdOptionGrps:
            addOptionGrpBtn = driver.find_element(By.XPATH, addOptionGrpBtnXPath)
            pyautogui.press('end')
            wait.until(expected_conditions.element_to_be_clickable((By.XPATH, addOptionGrpBtnXPath)))
            time.sleep(0.1)
            addOptionGrpBtn.click()
            wait.until(expected_conditions.presence_of_element_located((By.ID, groupNameInputID)))

            groupNameInput = driver.find_element(By.ID, groupNameInputID)
            optionGrpType = Select(driver.find_element(By.ID, optionGrpTypeID))
            optionGrpMand = driver.find_element(By.ID, optionGrpMandID)
            optionMinInput = driver.find_element(By.ID, optionMinInputID)
            optionMaxInput = driver.find_element(By.ID, optionMaxInputID)
            createBtn = driver.find_element(By.XPATH, createBtnXPath)
        
            groupNameInput.send_keys(data["GroupName"])
            optionGrpType.select_by_visible_text(data["DropDown"])
            if data["DropDown"] == "Checkbox":
                wait.until(lambda d: optionMinInput.is_displayed())
                optionMinInput.clear()
                optionMinInput.send_keys(0)
            if not "Optional" in data["Section Subtitle"]:
                optionGrpMand.click()
            if "max" in data["Section Subtitle"]:
                maxCount = data["Section Subtitle"].split(" ")[-1]
                wait.until(lambda d: optionMaxInput.is_displayed())
                optionMaxInput.clear()
                optionMaxInput.send_keys(maxCount)
                
            createBtn.click()

        ## Automate uploading of add-on Options
            index = 0
            optionGrpText = f"{data['GroupName']}"
            createdOptionGrpXPath = f"//div[@class='accordion-header']//a[normalize-space(text())='{optionGrpText}']"
            if optionGrpText in dupCount.keys():
                index = dupCount[optionGrpText][1]
                dupCount[optionGrpText][1] += 1
                createdOptionGrp = driver.find_elements(By.XPATH, createdOptionGrpXPath)[index]
            else:
                createdOptionGrp = driver.find_element(By.XPATH, createdOptionGrpXPath)

            ActionChains(driver).move_to_element(createdOptionGrp).perform()
            wait.until(lambda d: createdOptionGrp.is_displayed())
            createdOptionGrp.click()

            for i in range(len(data["OptionNames"])):
                
                addOptionBtn = driver.find_element(By.XPATH, addOptionBtnXPath)
                ActionChains(driver).move_to_element(addOptionBtn).perform()
                wait.until(lambda d: addOptionBtn.is_displayed())
                time.sleep(0.2)
                addOptionBtn.click()

                optionNameInputID = "opt_Unit"
                optionPriceInputID = "opt_Price"
                submitOptionBtnXPath = "//button[@type='submit']"

                optionNameInput = driver.find_element(By.ID, optionNameInputID)
                optionPriceInput = driver.find_element(By.ID, optionPriceInputID)
                submitOptionBtn = driver.find_element(By.XPATH, submitOptionBtnXPath)

                wait.until(lambda d: optionNameInput.is_displayed())
                optionNameInput.send_keys(data["OptionNames"][i])
                optionPriceInput.send_keys(data["OptionPrices"][i])
                submitOptionBtn.click()

            ## Automate Linking Dish to Option

            addLinkedDishBtnXPath = "//a[contains(@href, '/Menu/LinkedDish')]"
            optionGrpBackBtnXPath = "//a[contains(@href, 'Menu/OptionGroups')]"

            addLinkedDishBtn = driver.find_element(By.XPATH, addLinkedDishBtnXPath)
            ActionChains(driver).move_to_element(addLinkedDishBtn).perform()
            wait.until(lambda d: addLinkedDishBtn.is_displayed())
            addLinkedDishBtn.click()

            submitLinkedDishBtnXPath = "//button[@type='submit']"

            def split_data(x):
                if type(x) != float and "|" in x:
                    return x.split("|")
                elif type(x) != float:
                    return x.split("~~")
                else:
                    return ""
            transformed_df = dataDF[["Section Title", "Button Name"]].map(split_data)
            names = list(dataDF[(transformed_df["Section Title"].apply(lambda x: data["GroupName"] in x)) & 
                                (transformed_df["Button Name"].apply(lambda y: "~~".join(data["OptionNames"]) in y))]["Dish Name"])
            for name in names:
                
                itemNameXPATH = f'//div[contains(text(), "{name}")]//input'

                itemName = driver.find_element(By.XPATH, itemNameXPATH)
                ActionChains(driver).move_to_element(itemName).perform()
                wait.until(lambda d: itemName.is_displayed())
                itemName.click()

            submitLinkedDishBtn = driver.find_element(By.XPATH, submitLinkedDishBtnXPath)
            ActionChains(driver).move_to_element(submitLinkedDishBtn).perform()
            wait.until(lambda d: submitLinkedDishBtn.is_displayed())
            submitLinkedDishBtn.click()

            optionGrpBackBtn = driver.find_element(By.XPATH, optionGrpBackBtnXPath)
            wait.until(lambda d: optionGrpBackBtn.is_displayed())
            optionGrpBackBtn.click()

            createdOptionGrps.append([data["GroupName"], data["OptionNames"]])
    create_input()

def create_input(): 
    def choose_excel_file():
        global excel_path
        excel_path = tk.filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        excel_entry.delete(0, tk.END)  # Clear any previous path
        excel_entry.insert(tk.END, excel_path)  # Insert the selected file path into the entry

    def submit():
        global email
        global password
        global store
        global folderName
        email = email_entry.get()
        password = password_entry.get()
        store = storeName_entry.get()
        folderName = folderName_entry.get()
        root.destroy()
        automation_process()

    # Create the main window
    root = tk.Tk()
    root.geometry("750x400")
    root.title("Input Box Example")

    store_label = tk.Label(root, text="Enter email:")
    store_label.pack()

    # Create an entry widget for input
    email_entry = tk.Entry(root, width=60)
    email_entry.pack()

    store_label = tk.Label(root, text="Enter password")
    store_label.pack()

    # Create an entry widget for input
    password_entry = tk.Entry(root, width=60)
    password_entry.pack()

    store_label = tk.Label(root, text="Enter merchant portal store name")
    store_label.pack()

    # Create an entry widget for input
    storeName_entry = tk.Entry(root, width=60)
    storeName_entry.pack()

    # Creating an entry for foldername
    folder_label = tk.Label(root, text = "Enter Grab store name")
    folder_label.pack()

    folderName_entry = tk.Entry(root, width = 60)
    folderName_entry.pack()

    # Create a button to choose Excel file
    choose_excel_button = tk.Button(root, text="Choose Excel File", command=choose_excel_file)
    choose_excel_button.pack()

    # Entry widget to display selected Excel file path
    excel_entry = tk.Entry(root, width=60)
    excel_entry.pack()


    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.pack()

    tk.Label(root, text="Created by : HS & Dedi").pack(pady=5)


    root.mainloop()

create_input()
