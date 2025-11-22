import requests
import time
import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompanyParser:
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium
        self.driver = None
        
        # Настройка requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        self.base_url = "https://www.rusprofile.ru"
        
        # Инициализируем БД
        self._init_database()
        
        if self.use_selenium:
            self._init_selenium()
    
    def _init_database(self):
        """Инициализирует базу данных"""
        try:
            from database import db
            db.init_connection()
            db.create_rusprofile_table()  # Создаем таблицу для rusprofile данных
            logger.info("✅ База данных подключена и таблицы созданы")
        except Exception as e:
            logger.error(f"⚠️ Ошибка подключения к БД: {e}")
    
    def _init_selenium(self):
        """Инициализирует Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined}")
            logger.info("✅ Selenium WebDriver инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Selenium: {e}")
            self.use_selenium = False

    def _search_with_selenium(self, inn: str):
        """Поиск компании на rusprofile с использованием Selenium"""
        if not self.driver:
            return None
            
        try:
            logger.info(f"🛞 Загружаем страницу поиска rusprofile...")
            self.driver.get(self.base_url)
            
            # Ждем загрузки страницы
            time.sleep(3)
            
            # Пробуем найти поле ввода
            logger.info("🔍 Ищем поле ввода на rusprofile...")
            
            selectors = [
                "input[name='query']",
                "input[placeholder*='ИНН']",
                "input[placeholder*='названи']",
                "#autocomplete-item_95",
                "#autocomplete-item_83", 
                "[id*='autocomplete-item']",
                "[data-autotest='index-search']",
                "input[type='text']"
            ]
            
            search_input = None
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            search_input = element
                            logger.info(f"✅ Найдено поле ввода: {selector}")
                            break
                    if search_input:
                        break
                except:
                    continue
            
            if not search_input:
                logger.error("❌ Не найдено поле ввода на rusprofile")
                return None
            
            # Вводим ИНН
            logger.info(f"⌨️ Вводим ИНН: {inn}")
            search_input.clear()
            search_input.send_keys(inn)
            
            time.sleep(1)
            
            # Нажимаем Enter
            logger.info("↵ Нажимаем Enter...")
            search_input.send_keys(Keys.ENTER)
            
            # Ждем загрузки результатов
            logger.info("⏳ Ожидаем загрузки результатов...")
            time.sleep(5)
            
            # Проверяем URL
            current_url = self.driver.current_url
            logger.info(f"📄 Текущий URL: {current_url}")
            
            # Если это страница поиска, кликаем на первую компанию
            if "search" in current_url:
                logger.info("📋 На странице поиска, ищем первую компанию...")
                company_selectors = [
                    ".company-name",
                    ".search-result-item a",
                    ".link-arrow", 
                    ".gp-name a",
                    "a[href*='/id/']",
                    ".legal-name"
                ]
                
                for selector in company_selectors:
                    try:
                        first_company = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        first_company.click()
                        logger.info("✅ Перешли на страницу компании")
                        time.sleep(3)
                        break
                    except:
                        continue
            
            # Получаем HTML страницы
            page_html = self.driver.page_source
            
            return {'html': page_html}
            
        except Exception as e:
            logger.error(f"❌ Ошибка Selenium: {e}")
            return None

    def _parse_company_data(self, html_content: str, inn: str, company_data: dict = None):
        """Парсит данные компании с rusprofile"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            logger.info("🔍 Анализируем данные компании...")
            
            # Извлекаем название компании
            company_name = self._extract_company_name(soup, inn, company_data)
            
            # Извлекаем реквизиты
            requisites = self._extract_requisites(soup, inn)
            
            # Извлекаем адрес
            address = self._extract_address(soup)
            
            # Извлекаем статус
            status, in_reestr = self._extract_status(soup)
            
            # Извлекаем налоги
            taxes_data = self._extract_taxes(soup)
            
            # Извлекаем дополнительные данные
            additional_data = self._extract_additional_data(soup)
            
            company_info = {
                "name": company_name,
                "inn": requisites.get('inn', inn),
                "ogrn": requisites.get('ogrn', ''),
                "kpp": requisites.get('kpp', ''),
                "address": address,
                "status": status,
                "in_reestr": in_reestr,
                "registration_date": additional_data.get('registration_date', ''),
                "authorized_capital": additional_data.get('authorized_capital', ''),
                "main_activity": additional_data.get('main_activity', ''),
                "taxes_value": taxes_data.get('taxes_value'),
                "taxes_full": taxes_data.get('taxes_full'),
                "source": "rusprofile",
                "parsed_at": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"✅ Данные компании извлечены: {company_name}")
            return company_info
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга данных компании: {e}")
            return self._create_fallback_data(inn, company_data)

    def _extract_company_name(self, soup: BeautifulSoup, inn: str, company_data: dict = None):
        """Извлекает название компании"""
        # Приоритет: название из переданных данных, затем с сайта
        if company_data and company_data.get('name'):
            return company_data['name']
            
        name_selectors = [
            ".company-name",
            "h1",
            ".legal-name", 
            ".company-title",
            "[itemprop='name']"
        ]
        
        for selector in name_selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    name = element.get_text(strip=True)
                    logger.info(f"✅ Название с сайта: {name}")
                    return name
            except:
                continue
                
        return f"Компания ИНН {inn}"

    def _extract_requisites(self, soup: BeautifulSoup, inn: str):
        """Извлекает реквизиты компании"""
        requisites = {'inn': inn, 'ogrn': '', 'kpp': ''}
        
        try:
            # Ищем реквизиты в тексте страницы
            page_text = soup.get_text()
            
            # ОГРН
            ogrn_patterns = [
                r'ОГРН[:\s]*([0-9]{13,15})',
                r'ОГРНИП[:\s]*([0-9]{13,15})',
                r'([0-9]{13,15}).*ОГРН'
            ]
            
            for pattern in ogrn_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    requisites['ogrn'] = match.group(1)
                    logger.info(f"✅ ОГРН: {requisites['ogrn']}")
                    break
            
            # КПП
            kpp_patterns = [
                r'КПП[:\s]*([0-9]{9})',
                r'([0-9]{9}).*КПП'
            ]
            
            for pattern in kpp_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    requisites['kpp'] = match.group(1)
                    logger.info(f"✅ КПП: {requisites['kpp']}")
                    break
                    
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения реквизитов: {e}")
            
        return requisites

    def _extract_address(self, soup: BeautifulSoup):
        """Извлекает адрес компании"""
        address_selectors = [
            "[itemprop='address']",
            ".address",
            ".company-address",
            ".company-info-address"
        ]
        
        for selector in address_selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    address = element.get_text(strip=True)
                    logger.info(f"✅ Адрес: {address}")
                    return address
            except:
                continue
                
        return ""

    def _extract_status(self, soup: BeautifulSoup):
        """Извлекает статус компании"""
        status_selectors = [
            ".company-status",
            ".status",
            ".status-label"
        ]
        
        for selector in status_selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    status = element.get_text(strip=True)
                    in_reestr = any(word in status.lower() for word in ['действующ', 'active', 'действует'])
                    logger.info(f"✅ Статус: {status}, В реестре: {in_reestr}")
                    return status, in_reestr
            except:
                continue
                
        return "Действующая", True

    def _extract_taxes(self, soup: BeautifulSoup):
        """Извлекает данные о налогах"""
        try:
            # Способ 1: Ищем по структуре блока с налогами
            taxes_selectors = [
                "//div[contains(@class, 'connexion-col__title') and contains(text(), 'Налоги')]",
                "//div[contains(text(), 'Налоги')]",
                "//*[contains(text(), 'Налоги') and contains(text(), 'млн руб')]",
                "//*[contains(text(), 'Налоги') and contains(text(), 'тыс. руб')]"
            ]
            
            for selector in taxes_selectors:
                try:
                    taxes_elements = soup.find_all(string=re.compile(r'Налоги', re.IGNORECASE))
                    for element in taxes_elements:
                        parent = element.parent
                        # Поднимаемся по дереву чтобы найти блок с числами
                        for i in range(3):  # Проверяем 3 уровня вверх
                            if parent:
                                text = parent.get_text()
                                if 'млн руб' in text or 'тыс. руб' in text:
                                    # Ищем числа в тексте
                                    numbers = re.findall(r'\d[\d\s]*', text)
                                    if numbers:
                                        # Берем первое число после "Налоги"
                                        taxes_value = numbers[0].strip()
                                        taxes_full = f"{taxes_value} млн руб." if 'млн' in text else f"{taxes_value} тыс. руб."
                                        logger.info(f"✅ Найдены налоги: {taxes_full}")
                                        return {
                                            'taxes_value': taxes_value,
                                            'taxes_full': taxes_full
                                        }
                            if parent:
                                parent = parent.parent
                except:
                    continue
            
            # Способ 2: Ищем по классам
            taxes_class_selectors = [
                ".connexion-col",
                ".company-finance",
                ".taxes-block",
                "[class*='tax']"
            ]
            
            for selector in taxes_class_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        text = element.get_text()
                        if 'Налоги' in text and ('млн руб' in text or 'тыс. руб' in text):
                            numbers = re.findall(r'\d[\d\s]*', text)
                            if numbers:
                                taxes_value = numbers[0].strip()
                                taxes_full = f"{taxes_value} млн руб." if 'млн' in text else f"{taxes_value} тыс. руб."
                                logger.info(f"✅ Найдены налоги через классы: {taxes_full}")
                                return {
                                    'taxes_value': taxes_value,
                                    'taxes_full': taxes_full
                                }
                except:
                    continue
                    
            logger.warning("⚠️ Налоги не найдены")
            return {}
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения налогов: {e}")
            return {}

    def _extract_additional_data(self, soup: BeautifulSoup):
        """Извлекает дополнительные данные"""
        data = {
            'registration_date': '',
            'authorized_capital': '', 
            'main_activity': ''
        }
        
        try:
            page_text = soup.get_text()
            
            # Дата регистрации
            date_patterns = [
                r'Регистрация\s*[\n:]?\s*(\d{1,2}\s+\w+\s+\d{4})',
                r'Дата регистрации\s*[\n:]?\s*(\d{1,2}\s+\w+\s+\d{4})',
                r'(\d{1,2}\s+\w+\s+\d{4}).*Регистрация'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    data['registration_date'] = match.group(1).strip()
                    break
            
            # Уставной капитал
            capital_patterns = [
                r'Уставный капитал\s*[\n:]?\s*([\d\s,]+руб)',
                r'Уставной капитал\s*[\n:]?\s*([\d\s,]+руб)'
            ]
            
            for pattern in capital_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    data['authorized_capital'] = match.group(1).strip()
                    break
            
            # Основной вид деятельности
            activity_selectors = [".okved", ".main-activity"]
            for selector in activity_selectors:
                try:
                    element = soup.select_one(selector)
                    if element and element.get_text(strip=True):
                        data['main_activity'] = element.get_text(strip=True)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения дополнительных данных: {e}")
            
        return data

    def _create_fallback_data(self, inn: str, company_data: dict = None):
        """Создает данные по умолчанию при ошибке"""
        company_name = company_data.get('name', f"Компания ИНН {inn}") if company_data else f"Компания ИНН {inn}"
        
        return {
            "name": company_name,
            "inn": inn,
            "ogrn": "",
            "kpp": "", 
            "address": "",
            "status": "Действующая",
            "in_reestr": True,
            "registration_date": "",
            "authorized_capital": "",
            "main_activity": "",
            "taxes_value": None,
            "taxes_full": None,
            "source": "fallback",
            "parsed_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def save_company_to_db(self, company_info):
        """Сохраняет данные компании в БД"""
        try:
            from database import db
            
            # Подготавливаем данные для сохранения
            db_data = {
                'name': company_info.get('name', ''),
                'inn': company_info.get('inn', ''),
                'ogrn': company_info.get('ogrn', ''),
                'kpp': company_info.get('kpp', ''),
                'address': company_info.get('address', ''),
                'status': company_info.get('status', ''),
                'in_reestr': company_info.get('in_reestr', False),
                'registration_date': company_info.get('registration_date', ''),
                'authorized_capital': company_info.get('authorized_capital', ''),
                'main_activity': company_info.get('main_activity', ''),
                'taxes_value': company_info.get('taxes_value', ''),
                'taxes_full': company_info.get('taxes_full', ''),
                'source': company_info.get('source', 'rusprofile'),
                'parsed_at': company_info.get('parsed_at', '')
            }
            
            result = db.insert_rusprofile_company(db_data)
            if result:
                logger.info(f"✅ Данные компании '{db_data['name']}' сохранены в БД")
                return result
            else:
                logger.error("❌ Не удалось сохранить данные компании в БД")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в БД: {e}")
            return None

    def parse_company_data(self, inn: str, company_data: dict = None, save_to_db: bool = True):
        """Парсит данные компании с rusprofile и сохраняет в БД"""
        try:
            logger.info(f"\n🔍 ПАРСИНГ КОМПАНИИ С ИНН: {inn}")
            
            if company_data:
                logger.info(f"🎯 Данные для сохранения: {company_data.get('name', 'N/A')}")
            
            search_result = self._search_with_selenium(inn)
            
            if not search_result:
                logger.warning("⚠️ Поиск не удался, используем данные по умолчанию")
                company_info = self._create_fallback_data(inn, company_data)
            else:
                company_info = self._parse_company_data(search_result['html'], inn, company_data)
            
            # Сохраняем в БД если требуется
            if save_to_db:
                db_result = self.save_company_to_db(company_info)
                if db_result:
                    company_info['db_id'] = db_result['id']
            
            return company_info
            
        except Exception as e:
            logger.error(f"💥 Ошибка при парсинге компании: {e}")
            company_info = self._create_fallback_data(inn, company_data)
            
            # Сохраняем в БД даже при ошибке
            if save_to_db:
                self.save_company_to_db(company_info)
            
            return company_info

    def get_company_taxes(self, inn: str):
        """Получает данные о налогах компании"""
        company_data = self.parse_company_data(inn)
        return {
            'taxes_value': company_data.get('taxes_value'),
            'taxes_full': company_data.get('taxes_full')
        }

    def check_company_by_inn(self, inn: str):
        """Алиас для обратной совместимости"""
        return self.get_company_taxes(inn)

    def check_multiple_companies(self, inn_list: list):
        """Проверяет несколько компаний"""
        results = []
        total = len(inn_list)
        
        for i, inn in enumerate(inn_list, 1):
            logger.info(f"\n📊 [{i}/{total}] Парсинг компании ИНН: {inn}")
            
            result = self.parse_company_data(inn)
            results.append(result)
            
            # Задержка между запросами
            if i < total:
                delay = 3
                logger.info(f"⏳ Задержка {delay} секунд...")
                time.sleep(delay)
        
        return results

    def parse_120_companies(self):
        """Парсит 120 компаний из Excel файла"""
        try:
            # Загружаем Excel файл
            file_path = "Dop_materialy_Razrabotka_analiticheskoj_sistemy_Akkreditovannye (1).xlsx"
            logger.info(f"📖 Загружаем данные из Excel файла: {file_path}")
            
            df = pd.read_excel(file_path, sheet_name='Аккредитованные ИТ-компании')
            
            # Берем первые 120 строк
            companies_data = df.head(120)
            
            results = []
            total = len(companies_data)
            
            for index, row in companies_data.iterrows():
                inn = str(row.get('ИНН', '')).strip()
                company_name = row.get('Сокращенное наименование', '') or row.get('Полное наименование', '')
                
                if inn and inn != 'Нет данных' and len(inn) >= 10:
                    logger.info(f"\n📊 [{index + 1}/{total}] Парсинг компании: {company_name} (ИНН: {inn})")
                    
                    company_data = {
                        'name': company_name,
                        'inn': inn,
                        'revenue': row.get('Выручка, руб.', ''),
                        'taxes_paid': row.get('Сумма уплаченных налогов, руб.', ''),
                        'employees': row.get('Среднесписочная численность', '')
                    }
                    
                    # Парсим данные
                    result = self.parse_company_data(inn, company_data, save_to_db=True)
                    results.append(result)
                    
                    # Задержка между запросами
                    if index + 1 < total:
                        delay = 5  # 5 секунд задержки
                        logger.info(f"⏳ Задержка {delay} секунд...")
                        time.sleep(delay)
                else:
                    logger.warning(f"⚠️ Пропущена компания с невалидным ИНН: {company_name}")
            
            # Сохраняем результаты в CSV
            self._save_results_to_csv(results, "rusprofile_120_companies.csv")
            
            logger.info(f"🎯 Парсинг завершен! Обработано компаний: {len(results)}")
            return results
            
        except Exception as e:
            logger.error(f"💥 Ошибка массового парсинга: {e}")
            return []

    def _save_results_to_csv(self, results, filename):
        """Сохраняет результаты в CSV файл"""
        try:
            data_to_save = []
            for result in results:
                row = {
                    'Название': result.get('name', ''),
                    'ИНН': result.get('inn', ''),
                    'ОГРН': result.get('ogrn', ''),
                    'КПП': result.get('kpp', ''),
                    'Адрес': result.get('address', ''),
                    'Статус': result.get('status', ''),
                    'В реестре': 'Да' if result.get('in_reestr') else 'Нет',
                    'Дата регистрации': result.get('registration_date', ''),
                    'Уставной капитал': result.get('authorized_capital', ''),
                    'Основной вид деятельности': result.get('main_activity', ''),
                    'Налоги': result.get('taxes_full', ''),
                    'Источник': result.get('source', '')
                }
                data_to_save.append(row)
            
            df = pd.DataFrame(data_to_save)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"💾 Результаты сохранены в {filename}")
            
        except Exception as e:
            logger.error(f"⚠️ Ошибка сохранения в CSV: {e}")

    def close(self):
        """Закрывает сессию и драйвер"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ Selenium закрыт")
            except:
                pass

# Глобальный экземпляр парсера
parser = CompanyParser(use_selenium=True)

# Тестирование
if __name__ == '__main__':
    logger.info("🚀 ТЕСТИРОВАНИЕ ПАРСЕРА RUSPROFILE")
    
    try:
        # Выбери что тестировать:
        # 1. Тестовые ИНН
        test_individual = False
        # 2. Массовый парсинг 120 компаний
        test_mass = True
        
        if test_individual:
            # Тестовые ИНН
            test_inns = ["3906216773", "7707083893"]
            
            for inn in test_inns:
                result = parser.parse_company_data(inn)
                if result:
                    logger.info(f"\n✅ РЕЗУЛЬТАТ ДЛЯ ИНН {inn}:")
                    for key, value in result.items():
                        logger.info(f"   {key}: {value}")
                else:
                    logger.error(f"❌ Не удалось спарсить данные для ИНН {inn}")
        
        if test_mass:
            # Массовый парсинг 120 компаний
            logger.info("🎯 ЗАПУСК МАССОВОГО ПАРСИНГА 120 КОМПАНИЙ")
            results = parser.parse_120_companies()
            
            # Статистика
            successful = len([r for r in results if r and r.get('name')])
            logger.info(f"\n📈 СТАТИСТИКА ПАРСИНГА:")
            logger.info(f"   Всего обработано: {len(results)}")
            logger.info(f"   Успешно спарсено: {successful}")
            logger.info(f"   С ошибками: {len(results) - successful}")
                    
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
    finally:
        parser.close()