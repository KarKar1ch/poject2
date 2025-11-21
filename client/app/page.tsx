"use client"
import { ChartRadialText } from '@/model/Card/Card';
import Header from '@/model/Header/Header';
import React, { useEffect, useState } from 'react';

interface Company {
  id: number;
  name: string;
  reestr: boolean;
}

const MainPage: React.FC = () => {
  const [data, setData] = useState<Company[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/companies');

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
    <div className='bg-[#ECEDF0] pl-[15px] pr-[15px]'>
      <Header/>
      <main className='mt-[30px] '>
        <div className='flex justify-between'>
          <ChartRadialText/>
        </div>
        <div className='bg-white mt-[50px] shadow-sm rounded-lg'>
            {data ? (
              data.map((company) => (
                <div key={company.id} className='mb-[7px]'>
                  <div>Компания: {company.name}</div>
                  <div>Входит в реестр: {company.reestr ? "Да" : "Нет"}</div>
                </div>
              ))
            ) : (
              <div>Данные не найдены</div>
            )}
        </div>
      </main>
    </div>
  );
};

export default MainPage;