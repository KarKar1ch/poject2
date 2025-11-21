# database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db_config import DB_CONFIG

DATABASE_URL = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(20), unique=True, nullable=False, index=True)
    ogrn = Column(String(20))
    reestr = Column(Boolean, default=False)

class Database:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.session = None

    def init_connection(self):
        try:
            self.session = self.SessionLocal()
            print("✅ Подключение к БД установлено")
            return True
        except SQLAlchemyError as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return False

    def get_connection(self):
        return self.session is not None

    def check_table_exists(self):
        try:
            inspector = inspect(self.engine)
            exists = inspector.has_table('companies')
            return exists
        except SQLAlchemyError as e:
            print(f"❌ Ошибка проверки таблицы: {e}")
            return False

    def check_columns_exist(self):
        """Проверяет наличие всех необходимых столбцов в таблице"""
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns('companies')
            column_names = [col['name'] for col in columns]
            
            required_columns = ['id', 'name', 'inn', 'ogrn', 'reestr']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"❌ Отсутствуют столбцы: {missing_columns}")
                return False
            else:
                print("✅ Все необходимые столбцы присутствуют")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка проверки столбцов: {e}")
            return False

    def create_table(self):
        try:
            # Проверяем существование таблицы
            table_exists = self.check_table_exists()
            columns_ok = False
            
            if table_exists:
                # Если таблица существует, проверяем столбцы
                columns_ok = self.check_columns_exist()
            
            if not table_exists or not columns_ok:
                # Если таблицы нет или столбцы неполные, пересоздаем
                print("🔄 Создаем/обновляем таблицу companies...")
                Base.metadata.drop_all(bind=self.engine)
                Base.metadata.create_all(bind=self.engine)
                print("✅ Таблица companies создана/обновлена")
            else:
                print("✅ Таблица companies уже существует и имеет правильную структуру")
            
            return True
            
        except SQLAlchemyError as e:
            print(f"❌ Ошибка создания таблицы: {e}")
            return False

    def insert_company(self, data):
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return None

            # Проверяем обязательные поля
            if not data.get('name') or not data.get('inn'):
                print("❌ Отсутствуют обязательные поля: name или inn")
                return None

            company = Company(
                name=data.get('name'),
                inn=data.get('inn'),
                ogrn=data.get('ogrn', ''),
                reestr=data.get('reestr', False)
            )
            
            self.session.add(company)
            self.session.commit()
            self.session.refresh(company)
            
            print(f"✅ Компания '{company.name}' успешно добавлена в БД (ID: {company.id})")
            
            return {
                'id': company.id,
                'name': company.name,
                'inn': company.inn,
                'ogrn': company.ogrn,
                'reestr': company.reestr
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"❌ Ошибка вставки компании: {e}")
            return None

    def get_all_companies(self):
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return []

            companies = self.session.query(Company).order_by(Company.id).all()
            print(f"✅ Получено {len(companies)} компаний из БД")
            
            return [
                {
                    'id': company.id,
                    'name': company.name,
                    'inn': company.inn,
                    'ogrn': company.ogrn,
                    'reestr': company.reestr
                }
                for company in companies
            ]
        except SQLAlchemyError as e:
            print(f"❌ Ошибка получения компаний: {e}")
            return []

    def get_company_by_inn(self, inn):
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return None

            company = self.session.query(Company).filter(Company.inn == inn).first()
            if company:
                print(f"✅ Компания с ИНН {inn} найдена в БД")
                return {
                    'id': company.id,
                    'name': company.name,
                    'inn': company.inn,
                    'ogrn': company.ogrn,
                    'reestr': company.reestr
                }
            else:
                print(f"⚠️ Компания с ИНН {inn} не найдена в БД")
                return None
        except SQLAlchemyError as e:
            print(f"❌ Ошибка поиска компании по ИНН: {e}")
            return None

    def get_company_by_id(self, company_id):
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return None

            company = self.session.query(Company).filter(Company.id == company_id).first()
            if company:
                return {
                    'id': company.id,
                    'name': company.name,
                    'inn': company.inn,
                    'ogrn': company.ogrn,
                    'reestr': company.reestr
                }
            return None
        except SQLAlchemyError as e:
            print(f"❌ Ошибка поиска компании по ID: {e}")
            return None

    def update_company(self, company_id, data):
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return None

            company = self.session.query(Company).filter(Company.id == company_id).first()
            if not company:
                print(f"⚠️ Компания с ID {company_id} не найдена")
                return None
            
            allowed_fields = ['name', 'inn', 'ogrn', 'reestr']
            updated_fields = []
            
            for field in allowed_fields:
                if field in data:
                    old_value = getattr(company, field)
                    new_value = data[field]
                    if old_value != new_value:
                        setattr(company, field, new_value)
                        updated_fields.append(field)
            
            if updated_fields:
                self.session.commit()
                self.session.refresh(company)
                print(f"✅ Компания ID {company_id} обновлена: {', '.join(updated_fields)}")
            else:
                print("ℹ️ Нет изменений для обновления")
            
            return {
                'id': company.id,
                'name': company.name,
                'inn': company.inn,
                'ogrn': company.ogrn,
                'reestr': company.reestr
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"❌ Ошибка обновления компании: {e}")
            return None

    def delete_company(self, company_id):
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return False

            company = self.session.query(Company).filter(Company.id == company_id).first()
            if company:
                company_name = company.name
                self.session.delete(company)
                self.session.commit()
                print(f"✅ Компания '{company_name}' (ID: {company_id}) удалена из БД")
                return True
            else:
                print(f"⚠️ Компания с ID {company_id} не найдена")
                return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"❌ Ошибка удаления компании: {e}")
            return False

    def delete_company_by_inn(self, inn):
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return False

            company = self.session.query(Company).filter(Company.inn == inn).first()
            if company:
                company_name = company.name
                self.session.delete(company)
                self.session.commit()
                print(f"✅ Компания '{company_name}' (ИНН: {inn}) удалена из БД")
                return True
            else:
                print(f"⚠️ Компания с ИНН {inn} не найдена")
                return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"❌ Ошибка удаления компании по ИНН: {e}")
            return False

    def clear_all_companies(self):
        """Очищает всю таблицу компаний"""
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return False

            count = self.session.query(Company).count()
            self.session.query(Company).delete()
            self.session.commit()
            print(f"✅ Удалено {count} компаний из БД")
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"❌ Ошибка очистки таблицы: {e}")
            return False

    def get_companies_count(self):
        """Возвращает количество компаний в БД"""
        try:
            if not self.session:
                print("❌ Нет подключения к БД")
                return 0

            count = self.session.query(Company).count()
            return count
        except SQLAlchemyError as e:
            print(f"❌ Ошибка получения количества компаний: {e}")
            return 0

    def close_connection(self):
        if self.session:
            self.session.close()
            print("✅ Подключение к БД закрыто")

# Глобальный экземпляр базы данных
db = Database()