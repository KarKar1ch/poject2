# parser.py
import requests
import time
from database import db
import json
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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        self.base_url = "https://www.gosuslugi.ru"
        self.search_url = "https://www.gosuslugi.ru/itorgs"
        
        if self.use_selenium:
            self._init_selenium()
        
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
        
    def _add_delay(self, seconds=3):
        """Добавляет задержку"""
        print(f"⏳ Задержка {seconds} сек...")
        time.sleep(seconds)

    def _search_with_selenium(self, inn: str):
        """Поиск компании с использованием Selenium"""
        if not self.driver:
            return None
            
        try:
            print(f"🛞 Загружаем страницу поиска...")
            self.driver.get(self.search_url)
            
            # Ждем загрузки страницы
            self._add_delay(3)
            
            # Ищем поле ввода
            print("🔍 Ищем поле ввода...")
            
            selectors = [
                "input[type='text']",
                "input.search-input", 
                "input[aria-label*='печатать']",
                "input[role='combobox']",
                ".search-input",
            ]
            
            search_input = None
            for selector in selectors:
                try:
                    search_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if search_input.is_displayed() and search_input.is_enabled():
                        print(f"✅ Найдено поле ввода: {selector}")
                        break
                    else:
                        search_input = None
                except TimeoutException:
                    continue
            
            if not search_input:
                # Пробуем найти ссылку "Искать снова"
                try:
                    search_again = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Искать снова")
                    print("✅ Найдена ссылка 'Искать снова', кликаем...")
                    search_again.click()
                    self._add_delay(2)
                    
                    # После клика снова ищем поле ввода
                    for selector in selectors:
                        try:
                            search_input = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            if search_input.is_displayed() and search_input.is_enabled():
                                print(f"✅ Найдено поле ввода после клика: {selector}")
                                break
                            else:
                                search_input = None
                        except TimeoutException:
                            continue
                except:
                    print("❌ Не найдена ссылка 'Искать снова'")
                    return None
            
            if not search_input:
                print("❌ Не удалось найти поле ввода")
                return None
            
            # Вводим ИНН
            print(f"⌨️ Вводим ИНН: {inn}")
            search_input.clear()
            search_input.send_keys(inn)
            
            self._add_delay(1)
            
            # Нажимаем Enter
            print("↵ Нажимаем Enter...")
            search_input.send_keys(Keys.ENTER)
            
            # Ждем загрузки результатов
            self._add_delay(5)
            
            # Получаем HTML страницы
            page_html = self.driver.page_source
            print("✅ Получен HTML страницы")
            
            return {'html': page_html}
            
        except Exception as e:
            print(f"❌ Ошибка Selenium: {e}")
            return None

    def _search_company(self, inn: str):
        """Выполняет поиск компании по ИНН"""
        try:
            # Сначала пробуем Selenium
            if self.use_selenium and self.driver:
                print("🛞 Пробуем поиск через Selenium...")
                selenium_result = self._search_with_selenium(inn)
                if selenium_result:
                    return selenium_result
                else:
                    print("⚠️ Selenium не сработал, пробуем requests...")
            
            # Если Selenium не сработал, используем requests
            self._add_delay(2)
            response = self.session.get(self.search_url, timeout=10)
            response.raise_for_status()
            
            # Пробуем поиск через параметры URL
            search_url_with_params = f"{self.search_url}?query={inn}"
            print(f"🔍 Пробуем поиск по URL: {search_url_with_params}")
            
            response = self.session.get(search_url_with_params, timeout=15)
            if response.status_code == 200:
                print("✅ Получен ответ от поиска по URL")
                return {'html': response.text}
            
            print("❌ Поиск не сработал")
            return None
            
        except Exception as e:
            print(f"❌ Ошибка при поиске компании: {e}")
            return None

    def _parse_search_result(self, html_content: str, inn: str):
        """Парсит HTML результат поиска"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ищем сообщение о результате
            page_text = soup.get_text().lower()
            
            if 'не входит в реестр' in page_text or 'не найдена' in page_text or 'не найдено' in page_text:
                return {
                    'in_reestr': False,
                    'message': 'Компания не входит в реестр аккредитованных ИТ-компаний',
                    'details': self._extract_company_details(soup, inn)
                }
            elif 'входит в реестр' in page_text or 'аккредитована' in page_text:
                return {
                    'in_reestr': True,
                    'message': 'Компания входит в реестр аккредитованных ИТ-компаний',
                    'details': self._extract_company_details(soup, inn)
                }
            
            # Если явного сообщения нет, проверяем наличие информации о компании
            company_info = self._extract_company_details(soup, inn)
            if company_info and company_info.get('name'):
                return {
                    'in_reestr': True,
                    'message': 'Компания найдена в реестре',
                    'details': company_info
                }
            
            return {
                'in_reestr': False,
                'message': 'Компания не найдена',
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
                'name': '',
                'inn': inn,
                'ogrn': '',
                'address': '',
                'status': ''
            }
            
            # Ищем название компании
            name_selectors = ['h1', 'h2', 'h3', '.title-h1', '.title-h2', '.title-h3']
            
            for selector in name_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if (text and len(text) > 5 and 
                        not any(word in text.lower() for word in ['реестр', 'аккредит', 'поиск', 'результат', 'каталог', 'войти'])):
                        company_info['name'] = text
                        break
                if company_info['name']:
                    break
            
            # Ищем ОГРН
            all_text = soup.get_text()
            ogrn_match = re.search(r'ОГРН[:\s]*([0-9]{13,15})', all_text, re.IGNORECASE)
            if ogrn_match:
                company_info['ogrn'] = ogrn_match.group(1)
            
            return company_info
            
        except Exception as e:
            print(f"Ошибка извлечения деталей компании: {e}")
            return None

    def check_company_by_inn(self, inn: str):
        """Проверяет компанию по ИНН"""
        try:
            self._add_delay(2)
            
            print(f"🔍 Поиск компании с ИНН: {inn}")
            
            search_result = self._search_company(inn)
            
            if not search_result:
                return {
                    "inn": inn,
                    "exists": False,
                    "in_reestr": False,
                    "details": None,
                    "error": "Не удалось выполнить поиск",
                    "source": "gosuslugi_ui"
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
                    if db and hasattr(db, 'insert_company'):
                        db_result = db.insert_company(company_info)
                        if db_result:
                            print(f"✅ Данные сохранены в БД")
                except Exception as e:
                    print(f"⚠️ Ошибка сохранения в БД: {e}")
                
                return {
                    "inn": inn,
                    "exists": parsed_result['in_reestr'],
                    "in_reestr": parsed_result['in_reestr'],
                    "details": company_info,
                    "message": parsed_result['message'],
                    "source": "selenium" if self.use_selenium and self.driver else "requests"
                }
                
            else:
                return self._process_json_result(search_result, inn)
            
        except Exception as e:
            print(f"Ошибка при проверке компании: {e}")
            return {
                "inn": inn,
                "exists": False,
                "in_reestr": False,
                "details": None,
                "error": str(e),
                "source": "gosuslugi_ui"
            }

    def _process_json_result(self, search_result: dict, inn: str):
        """Обрабатывает JSON результат"""
        try:
            companies = search_result.get('companies', []) or search_result.get('content', [])
            
            if not companies:
                return {
                    "inn": inn,
                    "exists": False,
                    "in_reestr": False,
                    "details": None,
                    "error": "Компания не найдена",
                    "source": "gosuslugi_api"
                }
            
            company_data = companies[0]
            
            company_info = {
                "name": company_data.get('fullName') or company_data.get('name') or f"Компания ИНН {inn}",
                "inn": company_data.get('inn', inn),
                "ogrn": company_data.get('ogrn') or company_data.get('ogrnip', ''),
                "reestr": company_data.get('accredited', False)
            }
            
            return {
                "inn": inn,
                "exists": True,
                "in_reestr": company_info['reestr'],
                "details": company_info,
                "message": "Компания найдена в реестре",
                "source": "gosuslugi_api"
            }
            
        except Exception as e:
            print(f"Ошибка обработки JSON: {e}")
            return {
                "inn": inn,
                "exists": False,
                "in_reestr": False,
                "details": None,
                "error": str(e),
                "source": "gosuslugi_api"
            }

    def check_multiple_companies(self, inn_list: list):
        """Проверяет несколько компаний"""
        results = []
        total = len(inn_list)
        
        for i, inn in enumerate(inn_list, 1):
            print(f"\n📊 Прогресс: {i}/{total}")
            result = self.check_company_by_inn(inn)
            results.append(result)
            
            if i < total:
                self._add_delay(3)
        
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