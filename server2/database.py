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
            return True
        except SQLAlchemyError as e:
            print(f"Ошибка подключения: {e}")
            return False

    def get_connection(self):
        return self.session is not None

    def check_table_exists(self):
        try:
            inspector = inspect(self.engine)
            exists = inspector.has_table('companies')
            return exists
        except SQLAlchemyError as e:
            print(f"Ошибка проверки таблицы: {e}")
            return False

    def create_table(self):
        try:
            table_exists = self.check_table_exists()
            
            if table_exists:
                return True
            
            Base.metadata.create_all(bind=self.engine)
            return True
            
        except SQLAlchemyError as e:
            print(f"Ошибка создания таблицы: {e}")
            return False

    def insert_company(self, data):
        try:
            company = Company(
                name=data.get('name'),
                inn=data.get('inn'),
                ogrn=data.get('ogrn'),
                reestr=data.get('reestr', False)
            )
            
            self.session.add(company)
            self.session.commit()
            self.session.refresh(company)
            
            return {
                'id': company.id,
                'name': company.name,
                'inn': company.inn,
                'ogrn': company.ogrn,
                'reestr': company.reestr
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Ошибка вставки компании: {e}")
            return None

    def get_all_companies(self):
        try:
            companies = self.session.query(Company).order_by(Company.id).all()
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
            print(f"Ошибка получения компаний: {e}")
            return []

    def get_company_by_inn(self, inn):
        try:
            company = self.session.query(Company).filter(Company.inn == inn).first()
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
            print(f"Ошибка поиска компании по ИНН: {e}")
            return None

    def update_company(self, company_id, data):
        try:
            company = self.session.query(Company).filter(Company.id == company_id).first()
            if not company:
                return None
            
            allowed_fields = ['name', 'inn', 'ogrn', 'reestr']
            
            for field in allowed_fields:
                if field in data:
                    setattr(company, field, data[field])
            
            self.session.commit()
            self.session.refresh(company)
            
            return {
                'id': company.id,
                'name': company.name,
                'inn': company.inn,
                'ogrn': company.ogrn,
                'reestr': company.reestr
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Ошибка обновления компании: {e}")
            return None

    def delete_company(self, company_id):
        try:
            company = self.session.query(Company).filter(Company.id == company_id).first()
            if company:
                self.session.delete(company)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Ошибка удаления компании: {e}")
            return False

    def close_connection(self):
        if self.session:
            self.session.close()

db = Database()