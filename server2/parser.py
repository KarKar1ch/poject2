from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import psycopg2
import time




# Данные для заполнения
company_data = [
    {"name": "КОДЭ", "inn": "3906900574"},
    # Добавьте другие компании здесь по образцу
]

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")


def check_company_in_reestr(inn):
    """Проверяет компанию по ИНН в реестре"""
    a = False
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://www.gosuslugi.ru/itorgs")
        time.sleep(3)
        
        search_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input[role='combobox']"))
        )
        
        search_input.clear()
        search_input.send_keys(inn)
        time.sleep(2)
        
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.lookup-button"))
        )
        search_button.click()
        
        time.sleep(5)
        
        # Проверка наличия в реестре
        try:
            title_elements = driver.find_elements(By.CLASS_NAME, "title-h5")
            for elem in title_elements:
                if "Компания входит в реестр аккредитованных ИТ-компаний" in elem.text:
                    a = True
                    break
        except:
            pass
        
        if not a:
            try:
                driver.find_element(By.XPATH, "//*[contains(text(), 'Компания входит в реестр')]")
                a = True
            except:
                pass
        
        if not a:
            page_text = driver.page_source
            if "Компания входит в реестр аккредитованных ИТ-компаний" in page_text:
                a = True
        
        driver.quit()
        return a
        
    except Exception as e:
        print(f"Ошибка при проверке компании: {e}")
        try:
            driver.quit()
        except:
            pass
        return False


def save_to_database(company_name, in_reestr):
    """Сохраняет данные в базу данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Создание таблицы если не существует
        create_table_query = """
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            reestr BOOLEAN,
            name TEXT
        );
        """
        cursor.execute(create_table_query)
        
        # Вставка данных
        insert_query = """
        INSERT INTO companies (reestr, name) 
        VALUES (%s, %s);
        """
        
        cursor.execute(insert_query, (in_reestr, company_name))
        conn.commit()
        
        print(f"✓ Данные сохранены: {company_name}, Реестр: {in_reestr}")
        
        # Проверяем, что данные добавились
        cursor.execute("SELECT * FROM companies;")
        records = cursor.fetchall()
        print(f"Всего записей в таблице: {len(records)}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as db_error:
        print(f"✗ Ошибка при работе с базой данных: {db_error}")
        return False


def main():
    print("Начинаем заполнение таблицы companies...")
    
    # Очистка таблицы перед заполнением (опционально)
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM companies;")  # Очищаем таблицу
        conn.commit()
        cursor.close()
        conn.close()
        print("Таблица очищена")
    except Exception as e:
        print(f"Ошибка при очистке таблицы: {e}")
    
    # Обрабатываем каждую компанию
    for company in company_data:
        print(f"\nПроверяем компанию: {company['name']} (ИНН: {company['inn']})")
        
        # Проверяем наличие в реестре
        in_reestr = check_company_in_reestr(company['inn'])
        
        # Сохраняем в базу данных
        save_to_database(company['name'], in_reestr)
        
        # Пауза между запросами
        time.sleep(2)
    
    print("\n" + "="*50)
    print("Заполнение таблицы завершено!")
    
    # Финальная проверка содержимого таблицы
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies ORDER BY id;")
        records = cursor.fetchall()
        
        print("\nСодержимое таблицы companies:")
        print("ID | Реестр | Название")
        print("-" * 30)
        for record in records:
            print(f"{record[0]} | {record[1]} | {record[2]}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при чтении таблицы: {e}")
