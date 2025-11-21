"use client"

import React, { useEffect, useState } from 'react';

interface Company {
  id: number;
  name: string;
  reestr: boolean;
}

const YourComponent: React.FC = () => {
  const [data, setData] = useState<Company[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://0.0.0.0:5000/companies');

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const result: Company[] = await response.json();
        console.log(result);
        setData(result);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (error) {
    return <div>Ошибка: {error}</div>;
  }

  return (
    <div>
      {data ? (
        data.map((company) => (
          <div key={company.id}>{company.name} {company.reestr}</div>
        ))
      ) : (
        <div>Данные не найдены</div>
      )}
    </div>
  );
};

export default YourComponent;