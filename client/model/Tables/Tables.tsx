import { useRef } from 'react';

export default function Tables({ data }: { data: any[] | null }) {
  const tableRef = useRef<HTMLTableElement>(null);

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
                <th>Реестр</th>
              </tr>
            </thead>
            <tbody>
              ${data.map(company => `
                <tr>
                  <td>${company.name}</td>
                  <td>${company.inn || ''}</td>
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

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      
      <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
        <h3 className="text-lg font-semibold text-gray-800">Компании в реестре</h3>
        <button
          onClick={exportToExcel}
          disabled={!data || data.length === 0}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Скачать Excel
        </button>
      </div>

      
      <table ref={tableRef} className="w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tl-lg">
              Компания
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ИНН
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tr-lg">
              Аккредитация 
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data && data.length > 0 ? (
            data.map((company, index) => (
              <tr 
                key={company.id} 
                className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
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
              <td colSpan={3} className="px-6 py-4 text-center text-sm text-gray-500">
                {data ? 'Нет данных для отображения' : 'Данные не найдены'}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}