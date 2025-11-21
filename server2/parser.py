# parser.py
import requests
import time
from database import db
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CompanyParser:
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium
        self.driver = None
        
        # Настройка requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        self.base_url = "https://www.gosuslugi.ru"
        self.search_url = "https://www.gosuslugi.ru/itorgs"
        
        # Инициализируем БД
        self._init_database()
        
        if self.use_selenium:
            self._init_selenium()
    
    def _init_database(self):
        """Инициализирует базу данных"""
        try:
            db.init_connection()
            db.create_table()
            print("✅ База данных подключена")
        except Exception as e:
            print(f"⚠️ Ошибка подключения к БД: {e}")
        
    def _init_selenium(self):
        """Инициализирует Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Selenium WebDriver инициализирован")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации Selenium: {e}")
            self.use_selenium = False

    def _search_with_selenium(self, inn: str):
        """Поиск компании с использованием Selenium"""
        if not self.driver:
            return None
            
        try:
            print(f"🛞 Загружаем страницу поиска...")
            self.driver.get(self.search_url)
            
            # Ждем загрузки страницы
            time.sleep(3)
            
            # Пробуем найти поле ввода на главной странице
            print("🔍 Ищем поле ввода на главной странице...")
            
            selectors = [
                "input[type='text']",
                "input.search-input", 
                "input[aria-label*='печатать']",
                "input[role='combobox']",
                ".search-input",
                "input"
            ]
            
            search_input = None
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            search_input = element
                            print(f"✅ Найдено поле ввода: {selector}")
                            break
                    if search_input:
                        break
                except:
                    continue
            
            if not search_input:
                print("❌ Не найдено поле ввода на главной странице")
                return None
            
            # Вводим ИНН
            print(f"⌨️ Вводим ИНН: {inn}")
            search_input.clear()
            search_input.send_keys(inn)
            
            time.sleep(1)
            
            # Нажимаем Enter
            print("↵ Нажимаем Enter...")
            search_input.send_keys(Keys.ENTER)
            
            # Ждем загрузки результатов
            print("⏳ Ожидаем загрузки результатов...")
            time.sleep(5)
            
            # Проверяем URL - если остались на той же странице, значит что-то пошло не так
            current_url = self.driver.current_url
            print(f"📄 Текущий URL: {current_url}")
            
            # Получаем HTML страницы
            page_html = self.driver.page_source
            print("✅ Получен HTML страницы с результатами")
            
            # Сохраняем HTML для отладки
            with open(f'result_{inn}.html', 'w', encoding='utf-8') as f:
                f.write(page_html)
            print(f"💾 HTML сохранен в result_{inn}.html")
            
            return {'html': page_html}
            
        except Exception as e:
            print(f"❌ Ошибка Selenium: {e}")
            return None

    def _parse_search_result(self, html_content: str, inn: str):
        """Парсит HTML результат поиска"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            print("🔍 Анализируем результаты поиска...")
            
            # Сохраняем все текстовые блоки для отладки
            text_blocks = []
            for element in soup.find_all(['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'span']):
                text = element.get_text(strip=True)
                if text and len(text) > 5:
                    text_blocks.append(text)
            
            print(f"📝 Найдено текстовых блоков: {len(text_blocks)}")
            
            # Выводим первые 10 блоков для отладки
            for i, text in enumerate(text_blocks[:10]):
                print(f"  {i+1}. {text[:100]}...")
            
            # Анализируем текст страницы
            page_text = soup.get_text().lower()
            
            # Ключевые фразы для "НЕ в реестре"
            not_in_reestr_phrases = [
                'не входит в реестр',
                'не найдена', 
                'не найдено',
                'компания с такими реквизитами не найдена'
            ]
            
            # Ключевые фразы для "В реестре"  
            in_reestr_phrases = [
                'входит в реестр',
                'аккредитована',
                'аккредитованных ит-компаний'
            ]
            
            # Проверяем фразы для "НЕ в реестре"
            for phrase in not_in_reestr_phrases:
                if phrase in page_text:
                    print(f"❌ Найдена фраза '{phrase}' - компания НЕ в реестре")
                    return {
                        'in_reestr': False,
                        'message': 'Компания не входит в реестр аккредитованных ИТ-компаний',
                        'details': self._extract_company_details(soup, inn)
                    }
            
            # Проверяем фразы для "В реестре"
            for phrase in in_reestr_phrases:
                if phrase in page_text:
                    print(f"✅ Найдена фраза '{phrase}' - компания в реестре")
                    return {
                        'in_reestr': True,
                        'message': 'Компания входит в реестр аккредитованных ИТ-компаний',
                        'details': self._extract_company_details(soup, inn)
                    }
            
            # Если явных фраз нет, проверяем наличие информации о компании
            company_info = self._extract_company_details(soup, inn)
            if company_info and company_info.get('name') and company_info['name'] != f"Компания ИНН {inn}":
                print("✅ Найдена информация о компании - предполагаем что в реестре")
                return {
                    'in_reestr': True,
                    'message': 'Компания найдена в реестре',
                    'details': company_info
                }
            else:
                print("❌ Информация о компании не найдена")
                return {
                    'in_reestr': False,
                    'message': 'Компания не найдена в реестре',
                    'details': None
                }
            
        except Exception as e:
            print(f"Ошибка парсинга результата: {e}")
            return {
                'in_reestr': False,
                'message': f'Ошибка парсинга: {e}',
                'details': None
            }

    def _extract_company_details(self, soup: BeautifulSoup, inn: str):
        """Извлекает детальную информацию о компании"""
        try:
            company_info = {
                'name': f"Компания ИНН {inn}",
                'inn': inn,
                'ogrn': '',
                'address': '',
                'status': ''
            }
            
            # Ищем название компании в различных элементах
            name_candidates = []
            
            # Ищем в заголовках
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
                elements = soup.find_all(tag)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 5:
                        name_candidates.append(text)
            
            # Ищем в div с классами содержащими company, name, title
            for div in soup.find_all('div', class_=True):
                classes = ' '.join(div.get('class', []))
                if any(word in classes.lower() for word in ['company', 'name', 'title', 'organization']):
                    text = div.get_text(strip=True)
                    if text and len(text) > 5:
                        name_candidates.append(text)
            
            # Выбираем лучшее название (самое длинное, не содержащее служебных слов)
            best_name = f"Компания ИНН {inn}"
            for candidate in name_candidates:
                if (len(candidate) > len(best_name) and 
                    not any(word in candidate.lower() for word in ['реестр', 'аккредит', 'поиск', 'результат', 'каталог', 'войти', 'госуслуги', 'ит-компани'])):
                    best_name = candidate
            
            company_info['name'] = best_name
            
            if best_name != f"Компания ИНН {inn}":
                print(f"✅ Название компании: {best_name}")
            
            # Ищем ОГРН
            all_text = soup.get_text()
            ogrn_patterns = [
                r'ОГРН[:\s]*([0-9]{13,15})',
                r'ОГРНИП[:\s]*([0-9]{13,15})',
                r'([0-9]{13,15}).*ОГРН'
            ]
            
            for pattern in ogrn_patterns:
                ogrn_match = re.search(pattern, all_text, re.IGNORECASE)
                if ogrn_match:
                    company_info['ogrn'] = ogrn_match.group(1)
                    print(f"✅ ОГРН: {company_info['ogrn']}")
                    break
            
            return company_info
            
        except Exception as e:
            print(f"Ошибка извлечения деталей компании: {e}")
            return {
                'name': f"Компания ИНН {inn}",
                'inn': inn,
                'ogrn': '',
                'address': '',
                'status': ''
            }

    def check_company_by_inn(self, inn: str):
        """Проверяет компанию по ИНН"""
        try:
            print(f"\n🔍 ПРОВЕРКА КОМПАНИИ С ИНН: {inn}")
            
            search_result = self._search_with_selenium(inn)
            
            if not search_result:
                return {
                    "inn": inn,
                    "exists": False,
                    "in_reestr": False,
                    "details": None,
                    "error": "Не удалось выполнить поиск",
                    "source": "selenium"
                }
            
            if 'html' in search_result:
                parsed_result = self._parse_search_result(search_result['html'], inn)
                
                company_info = {
                    "name": parsed_result['details']['name'] if parsed_result['details'] else f"Компания ИНН {inn}",
                    "inn": inn,
                    "ogrn": parsed_result['details']['ogrn'] if parsed_result['details'] else '',
                    "reestr": parsed_result['in_reestr']
                }
                
                # Сохраняем в базу данных
                try:
                    db_result = db.insert_company(company_info)
                    if db_result:
                        print(f"✅ Данные сохранены в БД")
                    else:
                        print(f"⚠️ Не удалось сохранить в БД")
                except Exception as e:
                    print(f"⚠️ Ошибка сохранения в БД: {e}")
                
                return {
                    "inn": inn,
                    "exists": parsed_result['in_reestr'],
                    "in_reestr": parsed_result['in_reestr'],
                    "details": company_info,
                    "message": parsed_result['message'],
                    "source": "selenium"
                }
            
        except Exception as e:
            print(f"💥 Ошибка при проверке компании: {e}")
            return {
                "inn": inn,
                "exists": False,
                "in_reestr": False,
                "details": None,
                "error": str(e),
                "source": "selenium"
            }

    def check_multiple_companies(self, inn_list: list):
        """Проверяет несколько компаний с задержками"""
        results = []
        total = len(inn_list)
        
        for i, inn in enumerate(inn_list, 1):
            print(f"\n📊 [{i}/{total}] Проверка компании...")
            
            result = self.check_company_by_inn(inn)
            results.append(result)
            
            # Задержка между запросами (кроме последней)
            if i < total:
                print("⏳ Задержка 3 секунды...")
                time.sleep(3)
        
        return results

    def close(self):
        """Закрывает сессию и драйвер"""
        if self.session:
            self.session.close()
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Selenium закрыт")
            except:
                pass

# Глобальный экземпляр парсера
parser = CompanyParser(use_selenium=True)

# Автоматический тест при запуске файла
if __name__ == '__main__':
    print("🚀 АВТОМАТИЧЕСКИЙ ТЕСТ ПАРСЕРА")
    
    try:
        # Тестируем несколько ИНН
        test_inns = ["3900008350", "7708542719"]
        
        for inn in test_inns:
            result = parser.check_company_by_inn(inn)
            
            print(f"\n🎯 РЕЗУЛЬТАТ ДЛЯ {inn}:")
            print(f"   Найдена: {result['exists']}") 
            print(f"   В реестре: {result['in_reestr']}")
            print(f"   Сообщение: {result['message']}")
            
            if result['details']:
                print(f"   Название: {result['details']['name']}")
                print(f"   ОГРН: {result['details']['ogrn']}")
            
            print("-" * 50)
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        parser.close()