import asyncpg

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'parser',
    'user': 'postgres',
    'password': '2009'
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