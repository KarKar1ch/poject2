import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';


export default function Tables({ data }: { data: any[] | null }) {
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

  const exportToExcel = () => {
    if (!data || data.length === 0) return;

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
              ${data.map(company => `
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
  };

  const handleAddCompany = async () => {
    if (!newCompany.name.trim() || !newCompany.inn.trim() || !newCompany.ogrn.trim()) {
      setError('Все поля обязательны для заполнения');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/companies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newCompany),
      });

      if (!response.ok) {
        throw new Error('Ошибка при добавлении компании');
      }

      setNewCompany({
        name: '',
        inn: '',
        ogrn: '',
        reestr: false
      });
      setIsAdding(false);
      window.location.reload();
      
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

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      
      {/* ФИКСИРОВАННАЯ ШАПКА ПРИ СКРОЛЛЕ ВСЕЙ СТРАНИЦЫ */}
      <div className="sticky top-0 z-50 p-4 border-b border-gray-200 flex justify-between items-center bg-white shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800">Компании в реестре</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setIsAdding(!isAdding)}
            className="px-4 py-2 bg-[#5D39F5] text-white rounded-[30px] hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2"
          >
            <Image src="/plus_24.svg" alt="funnel" width={20} height={20}/>
            Добавить компанию
          </button>
          <button
            onClick={exportToExcel}
            disabled={!data || data.length === 0}
            className="pl-[10px] bg-[#5D39F5] text-white w-[40px] rounded-[100%] hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2"
          >
            <Image src="/download_24.svg" alt="funnel" width={20} height={20}/>
          </button>
        </div>
      </div>

     
      {isAdding && (
        <div className="p-4 border-b border-gray-200 ">
          <h4 className="text-md font-semibold text-gray-800 mb-3">Добавить новую компанию</h4>
          {error && (
            <div className="mb-3 p-2 bg-red-100 border border-red-400 text-red-700 rounded">
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
                placeholder="Введите название"
              />
            </div>
            <div>
              <input
                type="text"
                value={newCompany.inn}
                onChange={(e) => handleInputChange('inn', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Введите ИНН"
              />
            </div>
            <div className="flex items-end gap-3">
              <div className="flex items-center">
              </div>
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
                  className="px-4 py-2 bg-white text-black rounded-[30px] hover:bg-gray-600"
                >
                  Отмена
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Таблица */}
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
            {data && data.length > 0 ? (
              data.map((company, index) => (
                <tr 
                  key={company.id} 
                  className='bg-white hover:bg-gray-50 cursor-pointer transition-colors'
                  onClick={() => handleCompanyClick(company.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {company.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {company.inn}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
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
                <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                  {data ? 'Нет данных для отображения' : 'Данные не найдены'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}