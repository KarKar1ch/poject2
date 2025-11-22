from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uvicorn
from database import db
from parser_fns import parser
from contextlib import asynccontextmanager
import logging
import asyncio
import time
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальные переменные для мониторинга
app_stats = {
    "start_time": None,
    "requests_processed": 0,
    "companies_parsed": 0,
    "errors_count": 0
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_stats["start_time"] = datetime.now()
    logger.info("🚀 Starting up FastAPI Server...")
    
    # Инициализация БД с повторными попытками
    db_status = await initialize_database()
    if not db_status:
        logger.error("❌ Failed to initialize database")
    
    # Инициализация парсера
    parser_status = await initialize_parser()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    await shutdown_services()

app = FastAPI(
    title="Company Parser API",
    description="API для парсинга данных компаний с Rusprofile и управления базой данных",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic модели
class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Название компании")
    inn: str = Field(..., min_length=10, max_length=12, description="ИНН компании")
    ogrn: Optional[str] = Field(None, max_length=15, description="ОГРН компании")
    reestr: bool = Field(False, description="Наличие в реестре")

    @validator('inn')
    def validate_inn(cls, v):
        if not v.isdigit():
            raise ValueError('ИНН должен содержать только цифры')
        return v

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    inn: Optional[str] = Field(None, min_length=10, max_length=12)
    ogrn: Optional[str] = Field(None, max_length=15)
    reestr: Optional[bool] = None

class CheckRequest(BaseModel):
    inn: str = Field(..., min_length=10, max_length=12, description="ИНН для проверки")
    force_refresh: bool = Field(False, description="Принудительный перепарсинг")

class MultipleCheckRequest(BaseModel):
    inn_list: List[str] = Field(..., min_items=1, max_items=100)
    delay_between: float = Field(3.0, ge=1.0, le=10.0, description="Задержка между запросами")
    save_to_db: bool = Field(True, description="Сохранять в БД")

class CompanyIdsSearchRequest(BaseModel):
    company_ids: List[int] = Field(..., min_items=1, max_items=100, description="Список ID компаний")

class ParseResult(BaseModel):
    message: str
    data: Dict[str, Any]
    status: str
    execution_time: float
    source: str

class BatchParseResult(BaseModel):
    total_count: int
    success_count: int
    failed_count: int
    execution_time: float
    companies: List[Dict[str, Any]]

class HealthStatus(BaseModel):
    status: str
    database: str
    parser: str
    uptime: str
    requests_processed: int
    companies_parsed: int

# Зависимости
async def get_db_connection():
    """Зависимость для проверки подключения к БД"""
    if not db.get_connection():
        raise HTTPException(status_code=503, detail="Database unavailable")
    return db

async def track_request():
    """Трекинг запросов"""
    app_stats["requests_processed"] += 1

# Вспомогательные функции
async def initialize_database():
    """Инициализация базы данных"""
    max_retries = 3
    for attempt in range(max_retries):
        logger.info(f"🔄 Attempting database connection ({attempt + 1}/{max_retries})...")
        if db.init_connection():
            # Создаем таблицы
            tables_created = db.create_table()
            rusprofile_tables_created = db.create_rusprofile_table()
            
            if tables_created and rusprofile_tables_created:
                logger.info("✅ Database initialized successfully")
                
                # Проверяем существующие данные
                companies_count = db.get_companies_count()
                logger.info(f"📊 Database contains {companies_count} companies")
                return True
        else:
            logger.warning(f"⚠️ Database connection failed (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
    
    logger.error("❌ All database connection attempts failed")
    return False

async def initialize_parser():
    """Инициализация парсера"""
    try:
        if parser.driver:
            logger.info("✅ Parser initialized successfully")
            return True
        else:
            logger.warning("⚠️ Parser initialization failed - running in fallback mode")
            return False
    except Exception as e:
        logger.error(f"❌ Parser initialization error: {e}")
        return False

async def shutdown_services():
    """Корректное завершение работы сервисов"""
    try:
        parser.close()
        logger.info("✅ Parser closed")
    except Exception as e:
        logger.error(f"❌ Error closing parser: {e}")
    
    try:
        db.close_connection()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")

# Эндпоинты
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Корневой эндпоинт с информацией об API"""
    return {
        "message": "🚀 Company Parser API v2.0",
        "description": "API для парсинга данных компаний с Rusprofile",
        "version": "2.0.0",
        "endpoints": {
            "health": "GET /health",
            "docs": "GET /docs",
            "database": {
                "get_companies": "GET /companies",
                "create_company": "POST /companies",
                "get_company": "GET /companies/{id}",
                "update_company": "PUT /companies/{id}",
                "delete_company": "DELETE /companies/{id}",
                "search_by_ids": "POST /companies/search-by-ids"
            },
            "parsing": {
                "parse_single": "POST /rusprofile/parse",
                "parse_batch": "POST /rusprofile/parse/batch",
                "parse_120_companies": "POST /rusprofile/parse/120-companies",
                "get_taxes": "GET /rusprofile/taxes/{inn}"
            },
            "rusprofile_data": {
                "get_companies": "GET /rusprofile/companies",
                "get_company_by_inn": "GET /rusprofile/companies/inn/{inn}",
                "get_company_by_id": "GET /rusprofile/companies/{id}",
                "search_by_ids": "POST /rusprofile/companies/search-by-ids"
            },
            "monitoring": {
                "stats": "GET /stats",
                "db_status": "GET /db/status",
                "parser_status": "GET /parser/status"
            }
        }
    }

@app.get("/health", response_model=HealthStatus)
async def health_check(db_connection: bool = Depends(get_db_connection)):
    """Проверка здоровья сервиса"""
    uptime = datetime.now() - app_stats["start_time"]
    uptime_str = str(uptime).split('.')[0]  # Убираем микросекунды
    
    parser_status = "active" if parser.driver else "inactive"
    db_status = "connected" if db_connection else "disconnected"
    
    return HealthStatus(
        status="healthy",
        database=db_status,
        parser=parser_status,
        uptime=uptime_str,
        requests_processed=app_stats["requests_processed"],
        companies_parsed=app_stats["companies_parsed"]
    )

@app.get("/stats")
async def get_stats():
    """Статистика работы приложения"""
    uptime = datetime.now() - app_stats["start_time"]
    
    return {
        "uptime": str(uptime).split('.')[0],
        "requests_processed": app_stats["requests_processed"],
        "companies_parsed": app_stats["companies_parsed"],
        "errors_count": app_stats["errors_count"],
        "start_time": app_stats["start_time"].isoformat(),
        "database_connection": "connected" if db.get_connection() else "disconnected",
        "parser_status": "active" if parser.driver else "inactive"
    }

@app.get("/db/status")
async def database_status():
    """Детальный статус базы данных"""
    connection_status = db.get_connection()
    
    tables_info = {}
    if connection_status:
        tables = ['companies', 'companies_rusprofile']
        for table in tables:
            exists = db.check_table_exists(table)
            tables_info[table] = {
                "exists": exists,
                "columns_ok": db.check_columns_exist(table, ['id', 'name', 'inn']) if exists else False
            }
    
    return {
        "connection": "connected" if connection_status else "disconnected",
        "tables": tables_info,
        "companies_count": db.get_companies_count() if connection_status else 0,
        "rusprofile_companies_count": len(db.get_all_rusprofile_companies()) if connection_status else 0
    }

@app.get("/parser/status")
async def parser_status():
    """Статус парсера"""
    return {
        "selenium_available": parser.use_selenium and parser.driver is not None,
        "executor_working": hasattr(parser, 'executor') and parser.executor is not None,
        "session_active": parser.session is not None,
        "status": "active" if parser.driver else "inactive",
        "mode": "selenium" if parser.use_selenium and parser.driver else "fallback"
    }

# Эндпоинты для работы с компаниями
@app.get("/companies", dependencies=[Depends(track_request)])
async def get_companies(
    skip: int = Query(0, ge=0, description="Пропустить записей"),
    limit: int = Query(100, ge=1, le=1000, description="Лимит записей"),
    db_connection: bool = Depends(get_db_connection)
):
    """Получить список компаний с пагинацией"""
    logger.info(f"GET /companies - skip: {skip}, limit: {limit}")
    
    companies = db.get_all_companies()
    total = len(companies)
    
    # Применяем пагинацию
    paginated_companies = companies[skip:skip + limit]
    
    return {
        "companies": paginated_companies,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "has_more": skip + limit < total
        }
    }

@app.get("/companies/{company_id}", dependencies=[Depends(track_request)])
async def get_company(company_id: int, db_connection: bool = Depends(get_db_connection)):
    """Получить компанию по ID"""
    logger.info(f"GET /companies/{company_id}")
    
    company = db.get_company_by_id(company_id)
    if company:
        return company
    raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")

@app.get("/companies/inn/{inn}", dependencies=[Depends(track_request)])
async def get_company_by_inn(inn: str, db_connection: bool = Depends(get_db_connection)):
    """Получить компанию по ИНН"""
    logger.info(f"GET /companies/inn/{inn}")
    
    company = db.get_company_by_inn(inn)
    if company:
        return company
    raise HTTPException(status_code=404, detail=f"Company with INN {inn} not found")

@app.post("/companies", status_code=201, dependencies=[Depends(track_request)])
async def create_company(company: CompanyCreate, db_connection: bool = Depends(get_db_connection)):
    """Создать новую компанию"""
    logger.info(f"POST /companies - {company.name} (INN: {company.inn})")
    
    # Проверяем, существует ли компания с таким ИНН
    existing_company = db.get_company_by_inn(company.inn)
    if existing_company:
        raise HTTPException(
            status_code=409,
            detail=f"Company with INN {company.inn} already exists"
        )
    
    result = db.insert_company(company.dict())
    if result:
        return result
    raise HTTPException(status_code=500, detail="Failed to create company")

@app.put("/companies/{company_id}", dependencies=[Depends(track_request)])
async def update_company(
    company_id: int,
    company: CompanyUpdate,
    db_connection: bool = Depends(get_db_connection)
):
    """Обновить данные компании"""
    logger.info(f"PUT /companies/{company_id}")
    
    result = db.update_company(company_id, company.dict(exclude_unset=True))
    if result:
        return result
    raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")

@app.delete("/companies/{company_id}", dependencies=[Depends(track_request)])
async def delete_company(company_id: int, db_connection: bool = Depends(get_db_connection)):
    """Удалить компанию"""
    logger.info(f"DELETE /companies/{company_id}")
    
    success = db.delete_company(company_id)
    if success:
        return {"message": f"Company with ID {company_id} deleted successfully"}
    raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")

@app.post("/companies/search-by-ids", dependencies=[Depends(track_request)])
async def search_companies_by_ids(
    request: CompanyIdsSearchRequest,
    db_connection: bool = Depends(get_db_connection)
):
    """Найти компании по списку ID"""
    logger.info(f"POST /companies/search-by-ids - IDs: {request.company_ids}")
    
    try:
        results = db.get_companies_by_ids(request.company_ids)
        found_ids = [company['id'] for company in results]
        not_found_ids = [id for id in request.company_ids if id not in found_ids]
        
        logger.info(f"✅ Found {len(results)} companies out of {len(request.company_ids)} requested")
        
        return {
            "found_companies": results,
            "not_found_ids": not_found_ids,
            "summary": {
                "requested": len(request.company_ids),
                "found": len(results),
                "not_found": len(not_found_ids)
            }
        }
        
    except Exception as e:
        app_stats["errors_count"] += 1
        logger.error(f"Error searching companies by IDs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Эндпоинты для парсинга Rusprofile
@app.post("/rusprofile/parse", response_model=ParseResult, dependencies=[Depends(track_request)])
async def parse_rusprofile_company(
    request: CheckRequest,
    db_connection: bool = Depends(get_db_connection)
):
    """Спарсить данные компании с Rusprofile"""
    start_time = time.time()
    logger.info(f"POST /rusprofile/parse - INN: {request.inn}, force_refresh: {request.force_refresh}")
    
    try:
        # Проверяем, есть ли уже данные в БД
        if not request.force_refresh:
            existing_company = db.get_rusprofile_company_by_inn(request.inn)
            if existing_company:
                execution_time = time.time() - start_time
                return ParseResult(
                    message="Company data retrieved from database",
                    data=existing_company,
                    status="cached",
                    execution_time=round(execution_time, 2),
                    source="database"
                )
        
        # Парсим новые данные
        result = await parser.parse_company_data_async(request.inn)
        execution_time = time.time() - start_time
        
        if result:
            app_stats["companies_parsed"] += 1
            return ParseResult(
                message="Company data parsed successfully from Rusprofile",
                data=result,
                status="success",
                execution_time=round(execution_time, 2),
                source="rusprofile"
            )
        
        raise HTTPException(status_code=500, detail="Failed to parse company data")
        
    except asyncio.TimeoutError:
        execution_time = time.time() - start_time
        app_stats["errors_count"] += 1
        raise HTTPException(
            status_code=408,
            detail=f"Parsing timeout for INN {request.inn}"
        )
    except Exception as e:
        execution_time = time.time() - start_time
        app_stats["errors_count"] += 1
        logger.error(f"Parsing error for INN {request.inn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rusprofile/parse/batch", response_model=BatchParseResult, dependencies=[Depends(track_request)])
async def parse_rusprofile_multiple(
    request: MultipleCheckRequest,
    db_connection: bool = Depends(get_db_connection)
):
    """Массовый парсинг компаний с Rusprofile"""
    start_time = time.time()
    logger.info(f"POST /rusprofile/parse/batch - {len(request.inn_list)} companies")
    
    if len(request.inn_list) > 100:
        raise HTTPException(status_code=400, detail="Too many INNs. Maximum: 100")
    
    try:
        results = await parser.check_multiple_companies_async(
            request.inn_list,
            delay_between=request.delay_between,
            save_to_db=request.save_to_db
        )
        
        successful = len([r for r in results if r and r.get('name')])
        execution_time = time.time() - start_time
        
        app_stats["companies_parsed"] += successful
        
        return BatchParseResult(
            total_count=len(request.inn_list),
            success_count=successful,
            failed_count=len(request.inn_list) - successful,
            execution_time=round(execution_time, 2),
            companies=results
        )
        
    except Exception as e:
        app_stats["errors_count"] += 1
        logger.error(f"Batch parsing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rusprofile/parse/120-companies", dependencies=[Depends(track_request)])
async def parse_120_companies(background_tasks: BackgroundTasks):
    """Запустить парсинг 120 компаний из Excel файла в фоновом режиме"""
    logger.info("POST /rusprofile/parse/120-companies")
    
    background_tasks.add_task(parser.parse_120_companies)
    
    return {
        "message": "Mass parsing of 120 companies started in background",
        "status": "processing",
        "task_id": f"parse_120_{int(time.time())}"
    }

@app.get("/rusprofile/taxes/{inn}", dependencies=[Depends(track_request)])
async def get_rusprofile_taxes(inn: str):
    """Получить данные о налогах компании"""
    logger.info(f"GET /rusprofile/taxes/{inn}")
    
    try:
        result = await parser.parse_company_data_async(inn, save_to_db=False)
        if result and (result.get('taxes_value') or result.get('taxes_full')):
            return {
                'taxes_value': result.get('taxes_value'),
                'taxes_full': result.get('taxes_full'),
                'company_name': result.get('name'),
                'inn': inn,
                'source': result.get('source', 'unknown')
            }
        raise HTTPException(status_code=404, detail="Tax data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Эндпоинты для работы с данными Rusprofile
@app.get("/rusprofile/companies", dependencies=[Depends(track_request)])
async def get_rusprofile_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db_connection: bool = Depends(get_db_connection)
):
    """Получить компании из таблицы Rusprofile"""
    logger.info(f"GET /rusprofile/companies - skip: {skip}, limit: {limit}")
    
    companies = db.get_all_rusprofile_companies()
    total = len(companies)
    
    paginated_companies = companies[skip:skip + limit]
    
    return {
        "companies": paginated_companies,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "has_more": skip + limit < total
        }
    }

@app.get("/rusprofile/companies/{company_id}", dependencies=[Depends(track_request)])
async def get_rusprofile_company_by_id(company_id: int, db_connection: bool = Depends(get_db_connection)):
    """Получить компанию из Rusprofile по ID"""
    logger.info(f"GET /rusprofile/companies/{company_id}")
    
    # Получаем все компании и ищем по ID
    companies = db.get_all_rusprofile_companies()
    company = next((c for c in companies if c['id'] == company_id), None)
    
    if company:
        return company
    raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found in Rusprofile data")

@app.get("/rusprofile/companies/inn/{inn}", dependencies=[Depends(track_request)])
async def get_rusprofile_company_by_inn(inn: str, db_connection: bool = Depends(get_db_connection)):
    """Получить компанию из Rusprofile по ИНН"""
    logger.info(f"GET /rusprofile/companies/inn/{inn}")
    
    company = db.get_rusprofile_company_by_inn(inn)
    if company:
        return company
    raise HTTPException(status_code=404, detail=f"Company with INN {inn} not found in Rusprofile data")

@app.post("/rusprofile/companies/search-by-ids", dependencies=[Depends(track_request)])
async def search_rusprofile_companies_by_ids(
    request: CompanyIdsSearchRequest,
    db_connection: bool = Depends(get_db_connection)
):
    """Найти компании из Rusprofile по списку ID"""
    logger.info(f"POST /rusprofile/companies/search-by-ids - IDs: {request.company_ids}")
    
    try:
        results = db.get_rusprofile_companies_by_ids(request.company_ids)
        found_ids = [company['id'] for company in results]
        not_found_ids = [id for id in request.company_ids if id not in found_ids]
        
        logger.info(f"✅ Found {len(results)} Rusprofile companies out of {len(request.company_ids)} requested")
        
        return {
            "found_companies": results,
            "not_found_ids": not_found_ids,
            "summary": {
                "requested": len(request.company_ids),
                "found": len(results),
                "not_found": len(not_found_ids)
            }
        }
        
    except Exception as e:
        app_stats["errors_count"] += 1
        logger.error(f"Error searching Rusprofile companies by IDs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Глобальный обработчик HTTP исключений"""
    app_stats["errors_count"] += 1
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик всех исключений"""
    app_stats["errors_count"] += 1
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    print("🚀 Starting FastAPI Server on http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000/docs")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info",
        access_log=True
    )