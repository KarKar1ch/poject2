import { useState, useEffect } from 'react';

interface Company {
  id: number;
  name: string;
  inn: string;
  ogrn: string;
  reestr: boolean;
}

interface ApiResponse {
  companies: Company[];
}

export const useCompanies = () => {
  const [data, setData] = useState<Company[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('Загружаем данные...');
        
        const response = await fetch('http://localhost:5000/companies?skip=0&limit=100', {
          headers: {
            'Accept': 'application/json',
          },
        });
        
        console.log('Статус ответа:', response.status);
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const result: ApiResponse = await response.json();
        console.log('Данные получены:', result);
        
        setData(result.companies); // Извлекаем массив companies
      } catch (err: any) {
        console.error('Ошибка загрузки:', err);
        setError(err.message);
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
};