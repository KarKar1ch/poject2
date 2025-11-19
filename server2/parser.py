from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def setup_driver():
    """Настройка Chrome драйвера"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Добавляем дополнительные опции для стабильности
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def search_company_by_inn(driver, inn):
    """Поиск компании по ИНН с обработкой stale elements"""
    try:
        # Открываем страницу поиска
        print("Открываем страницу поиска...")
        driver.get("https://rmsp.nalog.ru/search.html")
        
        # Ждем полной загрузки страницы
        wait = WebDriverWait(driver, 15)
        
        # Ждем загрузки поля поиска с повторными попытками
        search_input = wait.until(
            EC.presence_of_element_located((By.ID, "query"))
        )
        
        # Очищаем поле и вводим ИНН с задержками
        print(f"Вводим ИНН: {inn}")
        search_input.clear()
        time.sleep(0.5)
        search_input.send_keys(inn)
        time.sleep(0.5)
        
        # Пробуем разные способы отправки формы
        try:
            # Способ 1: Найти кнопку и кликнуть
            search_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Найти') or contains(text(), 'Поиск') or @type='submit']"))
            )
            search_button.click()
        except:
            # Способ 2: Отправить через ENTER
            print("Используем отправку через ENTER...")
            search_input.send_keys(Keys.ENTER)
        
        # Ждем загрузки результатов - проверяем разные индикаторы
        print("Ожидаем загрузки результатов...")
        time.sleep(3)
        
        # Ждем либо таблицу, либо любой элемент результатов
        try:
            # Ожидаем появления таблицы результатов
            wait.until(
                EC.presence_of_element_located((By.ID, "tblResultData"))
            )
            print("Таблица результатов найдена!")
            return True
        except TimeoutException:
            # Проверяем другие возможные элементы результатов
            print("Таблица не найдена, проверяем альтернативные элементы...")
            return check_alternative_results(driver)
            
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return False

def check_alternative_results(driver):
    """Проверка альтернативных способов идентификации результатов"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Проверяем различные возможные селекторы для таблицы результатов
        possible_selectors = [
            "#tblResultData",
            "table.table",
            "table.results", 
            ".search-results",
            ".results-table",
            "table"
        ]
        
        for selector in possible_selectors:
            try:
                table = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if table.is_displayed():
                    print(f"Найдена таблица с селектором: {selector}")
                    return True
            except:
                continue
        
        # Проверяем наличие сообщения "ничего не найдено"
        no_results_selectors = [
            "//*[contains(text(), 'ничего не найдено')]",
            "//*[contains(text(), 'не найдено')]",
            "//*[contains(text(), 'нет данных')]"
        ]
        
        for selector in no_results_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    print("Поиск не дал результатов")
                    return True
            except:
                continue
                
        print("Не удалось определить результаты поиска")
        return False
        
    except Exception as e:
        print(f"Ошибка при проверке альтернативных результатов: {e}")
        return False

def parse_results_table(driver):
    """Парсинг таблицы с результатами с обработкой stale elements"""
    try:
        # Находим таблицу с ожиданием
        wait = WebDriverWait(driver, 10)
        table = wait.until(
            EC.presence_of_element_located((By.ID, "tblResultData"))
        )
        
        # Получаем все строки таблицы
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        results = []
        
        for i, row in enumerate(rows):
            try:
                # Получаем все ячейки в строке с обработкой stale element
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if not cells:
                    # Если это заголовок (th)
                    cells = row.find_elements(By.TAG_NAME, "th")
                
                row_data = [cell.text.strip() for cell in cells]
                
                if row_data:  # Если строка не пустая
                    results.append(row_data)
                    print(f"Строка {i}: {row_data}")
                    
            except StaleElementReferenceException:
                # Если элемент устарел, перезапрашиваем строку
                print(f"Элемент устарел в строке {i}, пропускаем...")
                continue
            except Exception as e:
                print(f"Ошибка в строке {i}: {e}")
                continue
        
        return results
        
    except Exception as e:
        print(f"Ошибка при парсинге таблицы: {e}")
        return []

def safe_parse_with_retry(driver, max_retries=3):
    """Безопасный парсинг с повторными попытками"""
    for attempt in range(max_retries):
        try:
            results = parse_results_table(driver)
            if results:
                return results
            else:
                print(f"Попытка {attempt + 1}: данные не найдены")
                time.sleep(2)
        except StaleElementReferenceException:
            print(f"Попытка {attempt + 1}: stale element, повторяем...")
            time.sleep(2)
        except Exception as e:
            print(f"Попытка {attempt + 1}: ошибка {e}")
            time.sleep(2)
    
    return []

def save_to_excel(data, filename="results.xlsx"):
    """Сохранение результатов в Excel"""
    if data:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, header=False)
        print(f"Результаты сохранены в {filename}")

def debug_page(driver):
    """Функция для отладки - сохранение текущего состояния страницы"""
    try:
        # Сохраняем скриншот
        driver.save_screenshot("debug_screenshot.png")
        print("Скриншот сохранен как debug_screenshot.png")
        
        # Сохраняем HTML
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("HTML сохранен как debug_page.html")
        
        # Сохраняем текущий URL
        print(f"Текущий URL: {driver.current_url}")
        
    except Exception as e:
        print(f"Ошибка при отладке: {e}")

def main():
    driver = None
    try:
        # Настройки
        INN = "5024182694"
        
        # Инициализация драйвера
        print("Запускаем браузер...")
        driver = setup_driver()
        
        # Выполняем поиск
        if search_company_by_inn(driver, INN):
            print("Поиск выполнен успешно!")
            
            # Даем время для полной загрузки
            time.sleep(2)
            
            # Парсим результаты с повторными попытками
            results = safe_parse_with_retry(driver)
            
            if results:
                print("\n" + "="*50)
                print("НАЙДЕННЫЕ ДАННЫЕ:")
                print("="*50)
                
                for i, row in enumerate(results):
                    print(f"{i+1}. {row}")
                
                # Сохраняем в Excel
                save_to_excel(results)
            else:
                print("Данные не найдены в таблице")
                debug_page(driver)
        else:
            print("Не удалось выполнить поиск")
            debug_page(driver)
            
    except Exception as e:
        print(f"Общая ошибка: {e}")
        if driver:
            debug_page(driver)
        
    finally:
        if driver:
            print("Закрываем браузер...")
            driver.quit()

if __name__ == "__main__":
    main()