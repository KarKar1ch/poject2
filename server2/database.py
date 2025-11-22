# database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db_config import DB_CONFIG
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class CompanyRusprofile(Base):
    __tablename__ = 'companies_rusprofile'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(20), unique=True, nullable=False, index=True)
    ogrn = Column(String(20))
    kpp = Column(String(20))
    address = Column(String(500))
    status = Column(String(100))
    in_reestr = Column(Boolean, default=False)
    registration_date = Column(String(50))
    authorized_capital = Column(String(100))
    main_activity = Column(String(500))
    taxes_value = Column(String(50))
    taxes_full = Column(String(100))
    source = Column(String(50))
    parsed_at = Column(String(50))

class Database:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.session = None

    def init_connection(self):
        try:
            # Проверяем подключение к БД
            with self.engine.connect() as conn:
                logger.info("✅ Подключение к БД установлено")
            
            # Создаем сессию
            self.session = self.SessionLocal()
            logger.info("✅ Сессия БД создана")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка подключения к БД: {e}")
            return False

    def get_connection(self):
        return self.session is not None and self.session.is_active

    def check_table_exists(self, table_name):
        try:
            inspector = inspect(self.engine)
            exists = inspector.has_table(table_name)
            return exists
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка проверки таблицы {table_name}: {e}")
            return False

    def check_columns_exist(self, table_name, required_columns):
        """Проверяет наличие всех необходимых столбцов в таблице"""
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                logger.warning(f"❌ Отсутствуют столбцы в {table_name}: {missing_columns}")
                return False
            else:
                logger.info(f"✅ Все необходимые столбцы присутствуют в {table_name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка проверки столбцов {table_name}: {e}")
            return False

    def create_table(self):
        try:
            # Определяем необходимые столбцы для таблицы companies
            required_columns = ['id', 'name', 'inn', 'ogrn', 'reestr']
            table_exists = self.check_table_exists('companies')
            columns_ok = False
            
            if table_exists:
                # Если таблица существует, проверяем столбцы
                columns_ok = self.check_columns_exist('companies', required_columns)
            
            if not table_exists or not columns_ok:
                # Если таблицы нет или столбцы неполные, пересоздаем
                logger.info("🔄 Создаем/обновляем таблицу companies...")
                Base.metadata.create_all(bind=self.engine, tables=[Company.__table__])
                logger.info("✅ Таблица companies создана/обновлена")
            else:
                logger.info("✅ Таблица companies уже существует и имеет правильную структуру")
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка создания таблицы companies: {e}")
            return False

    def create_rusprofile_table(self):
        """Создает таблицу для данных из rusprofile"""
        try:
            # Определяем необходимые столбцы для таблицы companies_rusprofile
            required_columns = ['id', 'name', 'inn', 'ogrn', 'kpp', 'address', 'status', 
                              'in_reestr', 'registration_date', 'authorized_capital', 
                              'main_activity', 'taxes_value', 'taxes_full', 'source', 'parsed_at']
            
            table_exists = self.check_table_exists('companies_rusprofile')
            columns_ok = False
            
            if table_exists:
                columns_ok = self.check_columns_exist('companies_rusprofile', required_columns)
            
            if not table_exists or not columns_ok:
                logger.info("🔄 Создаем/обновляем таблицу companies_rusprofile...")
                Base.metadata.create_all(bind=self.engine, tables=[CompanyRusprofile.__table__])
                logger.info("✅ Таблица companies_rusprofile создана/обновлена")
            else:
                logger.info("✅ Таблица companies_rusprofile уже существует и имеет правильную структуру")
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка создания таблицы companies_rusprofile: {e}")
            return False

    def insert_company(self, data):
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return None

            # Проверяем обязательные поля
            if not data.get('name') or not data.get('inn'):
                logger.error("❌ Отсутствуют обязательные поля: name или inn")
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
            
            logger.info(f"✅ Компания '{company.name}' успешно добавлена в БД (ID: {company.id})")
            
            return {
                'id': company.id,
                'name': company.name,
                'inn': company.inn,
                'ogrn': company.ogrn,
                'reestr': company.reestr
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"❌ Ошибка вставки компании: {e}")
            return None

    def insert_rusprofile_company(self, data):
        """Вставляет компанию в таблицу rusprofile"""
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return None

            # Проверяем обязательные поля
            if not data.get('name') or not data.get('inn'):
                logger.error("❌ Отсутствуют обязательные поля: name или inn")
                return None

            company = CompanyRusprofile(
                name=data.get('name'),
                inn=data.get('inn'),
                ogrn=data.get('ogrn', ''),
                kpp=data.get('kpp', ''),
                address=data.get('address', ''),
                status=data.get('status', ''),
                in_reestr=data.get('in_reestr', False),
                registration_date=data.get('registration_date', ''),
                authorized_capital=data.get('authorized_capital', ''),
                main_activity=data.get('main_activity', ''),
                taxes_value=data.get('taxes_value', ''),
                taxes_full=data.get('taxes_full', ''),
                source=data.get('source', 'rusprofile'),
                parsed_at=data.get('parsed_at', '')
            )
            
            self.session.add(company)
            self.session.commit()
            self.session.refresh(company)
            
            logger.info(f"✅ Компания '{company.name}' успешно добавлена в БД rusprofile (ID: {company.id})")
            
            return {
                'id': company.id,
                'name': company.name,
                'inn': company.inn,
                'ogrn': company.ogrn,
                'kpp': company.kpp,
                'address': company.address,
                'status': company.status,
                'in_reestr': company.in_reestr,
                'registration_date': company.registration_date,
                'authorized_capital': company.authorized_capital,
                'main_activity': company.main_activity,
                'taxes_value': company.taxes_value,
                'taxes_full': company.taxes_full,
                'source': company.source,
                'parsed_at': company.parsed_at
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"❌ Ошибка вставки компании в rusprofile: {e}")
            return None

    def get_all_companies(self):
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return []

            companies = self.session.query(Company).order_by(Company.id).all()
            logger.info(f"✅ Получено {len(companies)} компаний из БД")
            
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
            logger.error(f"❌ Ошибка получения компаний: {e}")
            return []

    def get_all_rusprofile_companies(self):
        """Получает все компании из таблицы rusprofile"""
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return []

            companies = self.session.query(CompanyRusprofile).order_by(CompanyRusprofile.id).all()
            logger.info(f"✅ Получено {len(companies)} компаний из БД rusprofile")
            
            return [
                {
                    'id': company.id,
                    'name': company.name,
                    'inn': company.inn,
                    'ogrn': company.ogrn,
                    'kpp': company.kpp,
                    'address': company.address,
                    'status': company.status,
                    'in_reestr': company.in_reestr,
                    'registration_date': company.registration_date,
                    'authorized_capital': company.authorized_capital,
                    'main_activity': company.main_activity,
                    'taxes_value': company.taxes_value,
                    'taxes_full': company.taxes_full,
                    'source': company.source,
                    'parsed_at': company.parsed_at
                }
                for company in companies
            ]
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка получения компаний из rusprofile: {e}")
            return []

    def get_company_by_inn(self, inn):
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return None

            company = self.session.query(Company).filter(Company.inn == inn).first()
            if company:
                logger.info(f"✅ Компания с ИНН {inn} найдена в БД")
                return {
                    'id': company.id,
                    'name': company.name,
                    'inn': company.inn,
                    'ogrn': company.ogrn,
                    'reestr': company.reestr
                }
            else:
                logger.warning(f"⚠️ Компания с ИНН {inn} не найдена в БД")
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка поиска компании по ИНН: {e}")
            return None

    def get_rusprofile_company_by_inn(self, inn):
        """Находит компанию в таблице rusprofile по ИНН"""
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return None

            company = self.session.query(CompanyRusprofile).filter(CompanyRusprofile.inn == inn).first()
            if company:
                logger.info(f"✅ Компания с ИНН {inn} найдена в БД rusprofile")
                return {
                    'id': company.id,
                    'name': company.name,
                    'inn': company.inn,
                    'ogrn': company.ogrn,
                    'kpp': company.kpp,
                    'address': company.address,
                    'status': company.status,
                    'in_reestr': company.in_reestr,
                    'registration_date': company.registration_date,
                    'authorized_capital': company.authorized_capital,
                    'main_activity': company.main_activity,
                    'taxes_value': company.taxes_value,
                    'taxes_full': company.taxes_full,
                    'source': company.source,
                    'parsed_at': company.parsed_at
                }
            else:
                logger.warning(f"⚠️ Компания с ИНН {inn} не найдена в БД rusprofile")
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка поиска компании по ИНН в rusprofile: {e}")
            return None

    def get_company_by_id(self, company_id):
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
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
            logger.error(f"❌ Ошибка поиска компании по ID: {e}")
            return None

    def get_companies_by_ids(self, company_ids):
        """Находит компании по списку ID"""
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return []

            if not company_ids:
                return []

            companies = self.session.query(Company).filter(Company.id.in_(company_ids)).all()
            logger.info(f"✅ Найдено {len(companies)} компаний по {len(company_ids)} ID")
            
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
            logger.error(f"❌ Ошибка поиска компаний по IDs: {e}")
            return []

    def get_rusprofile_companies_by_ids(self, company_ids):
        """Находит компании из таблицы rusprofile по списку ID"""
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return []

            if not company_ids:
                return []

            companies = self.session.query(CompanyRusprofile).filter(CompanyRusprofile.id.in_(company_ids)).all()
            logger.info(f"✅ Найдено {len(companies)} компаний из rusprofile по {len(company_ids)} ID")
            
            return [
                {
                    'id': company.id,
                    'name': company.name,
                    'inn': company.inn,
                    'ogrn': company.ogrn,
                    'kpp': company.kpp,
                    'address': company.address,
                    'status': company.status,
                    'in_reestr': company.in_reestr,
                    'registration_date': company.registration_date,
                    'authorized_capital': company.authorized_capital,
                    'main_activity': company.main_activity,
                    'taxes_value': company.taxes_value,
                    'taxes_full': company.taxes_full,
                    'source': company.source,
                    'parsed_at': company.parsed_at
                }
                for company in companies
            ]
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка поиска компаний из rusprofile по IDs: {e}")
            return []
    
    def update_company(self, company_id, data):
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return None

            company = self.session.query(Company).filter(Company.id == company_id).first()
            if not company:
                logger.warning(f"⚠️ Компания с ID {company_id} не найдена")
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
                logger.info(f"✅ Компания ID {company_id} обновлена: {', '.join(updated_fields)}")
            else:
                logger.info("ℹ️ Нет изменений для обновления")
            
            return {
                'id': company.id,
                'name': company.name,
                'inn': company.inn,
                'ogrn': company.ogrn,
                'reestr': company.reestr
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"❌ Ошибка обновления компании: {e}")
            return None

    def delete_company(self, company_id):
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return False

            company = self.session.query(Company).filter(Company.id == company_id).first()
            if company:
                company_name = company.name
                self.session.delete(company)
                self.session.commit()
                logger.info(f"✅ Компания '{company_name}' (ID: {company_id}) удалена из БД")
                return True
            else:
                logger.warning(f"⚠️ Компания с ID {company_id} не найдена")
                return False
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"❌ Ошибка удаления компании: {e}")
            return False

    def delete_company_by_inn(self, inn):
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return False

            company = self.session.query(Company).filter(Company.inn == inn).first()
            if company:
                company_name = company.name
                self.session.delete(company)
                self.session.commit()
                logger.info(f"✅ Компания '{company_name}' (ИНН: {inn}) удалена из БД")
                return True
            else:
                logger.warning(f"⚠️ Компания с ИНН {inn} не найдена")
                return False
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"❌ Ошибка удаления компании по ИНН: {e}")
            return False

    def clear_all_companies(self):
        """Очищает всю таблицу компаний"""
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return False

            count = self.session.query(Company).count()
            self.session.query(Company).delete()
            self.session.commit()
            logger.info(f"✅ Удалено {count} компаний из БД")
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"❌ Ошибка очистки таблицы: {e}")
            return False

    def get_companies_count(self):
        """Возвращает количество компаний в БД"""
        try:
            if not self.session:
                logger.error("❌ Нет подключения к БД")
                return 0

            count = self.session.query(Company).count()
            return count
        except SQLAlchemyError as e:
            logger.error(f"❌ Ошибка получения количества компаний: {e}")
            return 0

    def close_connection(self):
        if self.session:
            self.session.close()
            logger.info("✅ Подключение к БД закрыто")

# Глобальный экземпляр базы данных
db = Database()