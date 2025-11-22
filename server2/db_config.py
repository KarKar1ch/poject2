import asyncpg
import os
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'parser'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

async def get_db_connection():
    try:
        connection = await asyncpg.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print("Подключение к PostgreSQL установлено")
        return connection
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None

async def main():
    conn = await get_db_connection()
    if conn:
        version = await conn.fetchval("SELECT version();")
        print(f"Версия PostgreSQL: {version}")
        await conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())