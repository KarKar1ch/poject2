from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from database import db
from parser import parser
from contextlib import asynccontextmanager

app = FastAPI()

class CompanyCreate(BaseModel):
    name: str
    inn: str
    ogrn: Optional[str] = None
    reestr: bool = False

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    inn: Optional[str] = None
    ogrn: Optional[str] = None
    reestr: Optional[bool] = None

class CheckRequest(BaseModel):
    inn: str

class MultipleCheckRequest(BaseModel):
    inn_list: List[str]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.init_connection()
    db.create_table()
    yield
    # Shutdown
    parser.close()
    db.close_connection()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return {
        "message": "API для проверки компаний в реестре",
        "endpoints": {
            "create_company": "POST /companies",
            "get_all_companies": "GET /companies", 
            "get_company": "GET /companies/{id}",
            "get_company_by_inn": "GET /companies/inn/{inn}",
            "update_company": "PUT /companies/{id}",
            "delete_company": "DELETE /companies/{id}",
            "check_company": "POST /check/company",
            "check_multiple_companies": "POST /check/companies",
            "health_check": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db.get_connection() else "disconnected"
    }

@app.post("/companies", status_code=201)
async def create_company(company: CompanyCreate):
    required_fields = ['name', 'inn']
    for field in required_fields:
        if not getattr(company, field):
            raise HTTPException(status_code=400, detail=f"Отсутствует обязательное поле: {field}")
    
    result = db.insert_company(company.dict())
    if result:
        return result
    raise HTTPException(status_code=500, detail="Не удалось создать компанию")

@app.get("/companies")
async def get_companies():
    companies = db.get_all_companies()
    return companies

@app.get("/companies/{company_id}")
async def get_company(company_id: int):
    companies = db.get_all_companies()
    company = next((c for c in companies if c['id'] == company_id), None)
    
    if company:
        return company
    raise HTTPException(status_code=404, detail="Компания не найдена")

@app.get("/companies/inn/{inn}")
async def get_company_by_inn(inn: str):
    company = db.get_company_by_inn(inn)
    if company:
        return company
    raise HTTPException(status_code=404, detail="Компания не найдена")

@app.put("/companies/{company_id}")
async def update_company(company_id: int, company: CompanyUpdate):
    result = db.update_company(company_id, company.dict(exclude_unset=True))
    if result:
        return result
    raise HTTPException(status_code=404, detail="Компания не найдена")

@app.delete("/companies/{company_id}")
async def delete_company(company_id: int):
    success = db.delete_company(company_id)
    if success:
        return {"message": "Компания успешно удалена"}
    raise HTTPException(status_code=404, detail="Компания не найдена")

@app.post("/check/company", status_code=201)
async def check_company(request: CheckRequest):
    result = parser.check_company_by_inn(request.inn)
    if result:
        return result
    raise HTTPException(status_code=500, detail="Не удалось проверить компанию")

@app.post("/check/companies")
async def check_multiple_companies(request: MultipleCheckRequest):
    if not request.inn_list:
        raise HTTPException(status_code=400, detail="Список ИНН не может быть пустым")
    
    results = parser.check_multiple_companies(request.inn_list)
    return {
        "checked_count": len(results),
        "companies": results
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)