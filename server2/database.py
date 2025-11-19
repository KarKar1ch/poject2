import psycopg2
import json
import re
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        self.create_table()
    
    def connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                port="5432", 
                database="nalog_db",
                user="postgres", 
                password="password"
            )
            print(" Подключение к БД успешно")
        except Exception as e:
            print(f" Ошибка подключения к БД: {e}")
    
    def create_table(self):
        """Создание таблицы с нужными полями"""
        try:
            cur = self.conn.cursor()
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                inn VARCHAR(20),
                ogrn VARCHAR(20),
                category VARCHAR(500),
                region VARCHAR(500),
                inclusion_date DATE,
                exclusion_date DATE,
                raw_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            self.conn.commit()
            cur.close()
            print(" Таблица companies создана")
            
        except Exception as e:
            print(f" Ошибка создания таблицы: {e}")
    
    def extract_data_from_results(self, results):
        """Извлечение структурированных данных из результатов парсинга"""
        inn = ""
        ogrn = ""
        category = ""
        region = ""
        inclusion_date = None
        exclusion_date = None
        
        if not results or len(results) < 2:
            return inn, ogrn, category, region, inclusion_date, exclusion_date
        
        # Объединяем весь текст для поиска
        all_text = " ".join([" ".join(row) for row in results])
        
        # Ищем ИНН (10 или 12 цифр)
        inn_match = re.search(r'\b\d{10}\b|\b\d{12}\b', all_text)
        if inn_match:
            inn = inn_match.group()
        
        # Ищем ОГРН (13 цифр)
        ogrn_match = re.search(r'\b\d{13}\b', all_text)
        if ogrn_match:
            ogrn = ogrn_match.group()
        
        # Пытаемся извлечь данные из структурированной таблицы
        for row in results:
            row_text = " ".join(row).lower()
            
            # Категория (ищем ключевые слова)
            if any(word in row_text for word in ['категория', 'кат.', 'риск']):
                category = " ".join(row)
            
            # Регион
            if any(word in row_text for word in ['республика', 'область', 'край', 'г. ', 'москва', 'санкт-петербург']):
                region = " ".join(row)
            
            # Даты (ищем в формате ДД.ММ.ГГГГ)
            date_matches = re.findall(r'\b\d{2}\.\d{2}\.\d{4}\b', " ".join(row))
            if date_matches:
                if not inclusion_date and len(date_matches) >= 1:
                    try:
                        inclusion_date = datetime.strptime(date_matches[0], '%d.%m.%Y').date()
                    except:
                        pass
                if not exclusion_date and len(date_matches) >= 2:
                    try:
                        exclusion_date = datetime.strptime(date_matches[1], '%d.%m.%Y').date()
                    except:
                        pass
        
        return inn, ogrn, category, region, inclusion_date, exclusion_date
    
    def save_company(self, inn_search, results):
        """Сохранение компании с разбором данных"""
        try:
            # Извлекаем структурированные данные
            inn, ogrn, category, region, inclusion_date, exclusion_date = self.extract_data_from_results(results)
            
            # Если ИНН не нашли в результатах, используем поисковый
            if not inn:
                inn = inn_search
            
            cur = self.conn.cursor()
            cur.execute("""
            INSERT INTO companies 
            (inn, ogrn, category, region, inclusion_date, exclusion_date, raw_data) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                inn, 
                ogrn, 
                category, 
                region, 
                inclusion_date, 
                exclusion_date, 
                json.dumps(results, ensure_ascii=False)
            ))
            
            self.conn.commit()
            cur.close()
            print(f"Данные компании сохранены: ИНН {inn}")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения компании: {e}")
            return False
    
    def get_history(self):
        """Получение истории поисков"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT inn, ogrn, category, region, 
                       inclusion_date, exclusion_date, created_at
                FROM companies 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            rows = cur.fetchall()
            cur.close()
            
            history = []
            for row in rows:
                history.append({
                    'inn': row[0] or 'не найден',
                    'ogrn': row[1] or 'не найден',
                    'category': row[2] or 'не указана',
                    'region': row[3] or 'не указан',
                    'inclusion_date': row[4].strftime('%d.%m.%Y') if row[4] else 'нет',
                    'exclusion_date': row[5].strftime('%d.%m.%Y') if row[5] else 'нет',
                    'date': row[6].strftime('%d.%m.%Y %H:%M')
                })
            
            return history
        except Exception as e:
            print(f" Ошибка получения истории: {e}")
            return []
    
    def company_exists(self, inn):
        """Проверка существования компании в БД"""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT id FROM companies WHERE inn = %s", (inn,))
            exists = cur.fetchone() is not None
            cur.close()
            return exists
        except Exception as e:
            print(f" Ошибка проверки компании: {e}")
            return False