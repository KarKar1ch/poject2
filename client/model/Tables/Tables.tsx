import { useRef, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

interface Company {
  id: number;
  name: string;
  inn: string;
  ogrn: string;
  reestr: boolean;
}

export default function Tables({ data }: { data: any[] | null }) {
  const [companies, setCompanies] = useState<Company[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const tableRef = useRef<HTMLTableElement>(null);
  const router = useRouter();
  const [isAdding, setIsAdding] = useState(false);
  const [newCompany, setNewCompany] = useState({
    name: '',
    inn: '',
    ogrn: '',
    reestr: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Загрузка данных
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // ВРЕМЕННЫЕ ДАННЫЕ ДЛЯ ТЕСТИРОВАНИЯ
        const mockData: Company[] = [
          { id: 1, name: 'ООО "Рога и копыта"', inn: '1234567890', ogrn: '1234567890123', reestr: true },
          { id: 2, name: 'АО "СтройИнвест"', inn: '0987654321', ogrn: '9876543210987', reestr: false },
          { id: 3, name: 'ИП Иванов И.И.', inn: '1231231230', ogrn: '1231231230123', reestr: true },
        ];
        
        // Если данные переданы извне - используем их, иначе mock-данные
        if (data && data.length > 0) {
          setCompanies(data);
        } else {
          setCompanies(mockData);
          console.log('Используем тестовые данные:', mockData);
        }
        
      } catch (err) {
        console.error('Ошибка загрузки:', err);
        setError('Ошибка загрузки данных');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [data]);

  const exportToExcel = () => {
    if (!companies || companies.length === 0) return;

    const xml = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" 
            xmlns:x="urn:schemas-microsoft-com:office:excel" 
            xmlns="http://www.w3.org/TR/REC-html40">
        <head>
          <meta name="ProgId" content="Excel.Sheet">
          <meta charset="UTF-8">
          <style>
            table { border-collapse: collapse; }
            td { border: 1px solid black; padding: 5px; }
            th { border: 1px solid black; padding: 5px; background-color: #f0f0f0; font-weight: bold; }
          </style>
        </head>
        <body>
          <table>
            <thead>
              <tr>
                <th>Компания</th>
                <th>ИНН</th>
                <th>ОГРН</th>
                <th>Реестр</th>
              </tr>
            </thead>
            <tbody>
              ${companies.map(company => `
                <tr>
                  <td>${company.name}</td>
                  <td>${company.inn || ''}</td>
                  <td>${company.ogrn || ''}</td>
                  <td>${company.reestr ? "Да" : "Нет"}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </body>
      </html>
    `;

    const blob = new Blob([xml], { type: 'application/vnd.ms-excel' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'компании_реестр.xls');
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleAddCompany = async () => {
    if (!newCompany.name.trim() || !newCompany.inn.trim() || !newCompany.ogrn.trim()) {
      setError('Все поля обязательны для заполнения');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Временно сохраняем в localStorage для демонстрации
      const newCompanyData = {
        id: Date.now(),
        ...newCompany
      };
      
      const updatedCompanies = companies ? [...companies, newCompanyData] : [newCompanyData];
      setCompanies(updatedCompanies);
      
      // Сохраняем в localStorage
      localStorage.setItem('companies', JSON.stringify(updatedCompanies));
      
      setNewCompany({
        name: '',
        inn: '',
        ogrn: '',
        reestr: false
      });
      setIsAdding(false);
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setNewCompany(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCompanyClick = (companyId: number) => {
    router.push(`/companies/${companyId}`);
  };

  // Загрузка из localStorage при монтировании
  useEffect(() => {
    const savedCompanies = localStorage.getItem('companies');
    if (savedCompanies && (!companies || companies.length === 0)) {
      setCompanies(JSON.parse(savedCompanies));
    }
  }, []);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex justify-center items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Загрузка данных...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      
      {/* ФИКСИРОВАННАЯ ШАПКА */}
      <div className="sticky top-0 z-50 p-4 border-b border-gray-200 flex justify-between items-center bg-white shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800">Компании в реестре</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setIsAdding(!isAdding)}
            className="px-4 py-2 bg-[#5D39F5] text-white rounded-[30px] hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2"
          >
            <Image src="/plus_24.svg" alt="Добавить" width={20} height={20}/>
            Добавить компанию
          </button>
          <button
            onClick={exportToExcel}
            disabled={!companies || companies.length === 0}
            className="pl-[10px] bg-[#5D39F5] text-white w-[40px] h-[40px] rounded-full hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center"
          >
            <Image src="/download_24.svg" alt="Экспорт" width={20} height={20}/>
          </button>
        </div>
      </div>

      {/* ФОРМА ДОБАВЛЕНИЯ */}
      {isAdding && (
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <h4 className="text-md font-semibold text-gray-800 mb-3">Добавить новую компанию</h4>
          {error && (
            <div className="mb-3 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
              {error}
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div>
              <input
                type="text"
                value={newCompany.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Название компании"
              />
            </div>
            <div>
              <input
                type="text"
                value={newCompany.inn}
                onChange={(e) => handleInputChange('inn', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="ИНН"
              />
            </div>
            <div>
              <input
                type="text"
                value={newCompany.ogrn}
                onChange={(e) => handleInputChange('ogrn', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="ОГРН"
              />
            </div>
            <div className="flex items-end gap-3">
              <div className="flex gap-2">
                <button
                  onClick={handleAddCompany}
                  disabled={loading}
                  className="px-4 py-2 bg-[#5D39F5] text-white rounded-[30px] hover:bg-green-700 disabled:bg-gray-400 flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Добавление...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Сохранить
                    </>
                  )}
                </button>
                <button
                  onClick={() => {
                    setIsAdding(false);
                    setError(null);
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-[30px] hover:bg-gray-300"
                >
                  Отмена
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ТАБЛИЦА */}
      <div className="overflow-auto">
        <table ref={tableRef} className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Компания
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ИНН
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Аккредитация 
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {companies && companies.length > 0 ? (
              companies.map((company) => (
                <tr 
                  key={company.id} 
                  className='bg-white hover:bg-gray-50 cursor-pointer transition-colors'
                  onClick={() => handleCompanyClick(company.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {company.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {company.inn}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      company.reestr 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {company.reestr ? "Да" : "Нет"}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="px-6 py-8 text-center text-sm text-gray-500">
                  <div className="flex flex-col items-center justify-center">
                    <svg className="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Нет данных для отображения
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}