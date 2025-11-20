"use client"

import { NextPage } from 'next';
import { useState, useEffect } from 'react';

interface DataItem {
  id: number;
  name: string;
  reestr: boolean;
}

const DataPage: NextPage = () => {
  const [data, setData] = useState<DataItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchData = async (): Promise<void> => {
      try {
        
        const response = await fetch('http://localhost:5000/api/data');
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }
        
        const result: DataItem[] = await response.json();
        setData(result);
      } catch (err: unknown) {
        console.error('Fetch error:', err);
        setError(err instanceof Error ? err.message : 'Connection failed');
        
        
        setData([
          { id: 1, name: "КОДЭ", reestr: true },
          
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Загрузка данных...</h1>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Данные</h1>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '10px' }}>
         
        </div>
      )}

      {data.map((item) => (
        <div 
          key={item.id} 
          style={{ 
            marginBottom: '10px', 
            padding: '10px', 
            border: '1px solid #ccc'
          }}
        >
          <div><strong>ID:</strong> {item.id}</div>
          <div><strong>Name:</strong> {item.name}</div>
          <div><strong>Reestr:</strong> {item.reestr ? 'Да' : 'Нет'}</div>
        </div>
      ))}
    </div>
  );
};

export default DataPage;