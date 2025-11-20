from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

a=0

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")


try:
   
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    
    driver.get("https://www.gosuslugi.ru/itorgs")
    time.sleep(3)  
    
   
    search_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input[role='combobox']"))
    )
    
    
    search_input.send_keys("3906900574")
    time.sleep(2)
    
    
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.lookup-button"))
    )
    search_button.click()
    

    time.sleep(5)  
    

    try:
        title_elements = driver.find_elements(By.CLASS_NAME, "title-h5")
        for i, elem in enumerate(title_elements):
            if "Компания входит в реестр аккредитованных ИТ-компаний" in elem.text:
                a = True
                print(a)
                break
    except Exception as e:
        print(f"Ошибка при поиске по классу: {e}")
    
    
    try:
        title_xpath = driver.find_element(By.XPATH, "//*[contains(text(), 'Компания входит в реестр')]")
        print(f"Найден элемент по XPath: {title_xpath.text}")
        a = True
        print(a)
    except Exception as e:
        print(f"Не удалось найти элемент по XPath: {e}")
    
    
    try:
        title_css = driver.find_element(By.CSS_SELECTOR, ".title-h5")
        print(f"Найден элемент по CSS: {title_css.text}")
        if "Компания входит в реестр аккредитованных ИТ-компаний" in title_css.text:
            a = True
            print(a)
    except Exception as e:
        print(f"{e}")
    
 
    page_text = driver.page_source
    if "Компания входит в реестр аккредитованных ИТ-компаний" in page_text:
        a = True
        print(a)
    else:
        print("Текст не найден в исходном коде страницы")
        
   
    visible_text = driver.find_element(By.TAG_NAME, "body").text
    if "Компания входит в реестр аккредитованных ИТ-компаний" in visible_text:
        a = True
        print(a)

except Exception as e:
    print(f"Произошла ошибка: {e}")
    
    try:
        driver.save_screenshot("error.png")
    except:
        pass
finally:
    try:
        driver.quit()
    except:
        pass