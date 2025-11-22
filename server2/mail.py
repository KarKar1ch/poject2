# test_parser_simple.py
from parser_fns import parser
import logging

# Включаем подробное логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_parser_simple():
    print("🔍 ТЕСТИРОВАНИЕ ПАРСЕРА (упрощенное)")
    
    # Тестовые ИНН
    test_inns = [
        "7707083893",  # Яндекс
        "7736207543",  # 1С
        "7810712392"   # Сбер
    ]
    
    for inn in test_inns:
        print(f"\n🎯 Тестируем ИНН: {inn}")
        try:
            # Парсим без сохранения в БД
            result = parser.parse_company_data(inn, save_to_db=False)
            if result:
                print("✅ УСПЕХ! Получены данные:")
                print(f"   Название: {result.get('name', 'N/A')}")
                print(f"   ИНН: {result.get('inn', 'N/A')}")
                print(f"   ОГРН: {result.get('ogrn', 'N/A')}")
                print(f"   Адрес: {result.get('address', 'N/A')}")
                print(f"   Налоги: {result.get('taxes_full', 'N/A')}")
            else:
                print("❌ Парсинг не удался")
                
        except Exception as e:
            print(f"💥 Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    parser.close()

if __name__ == "__main__":
    test_parser_simple()