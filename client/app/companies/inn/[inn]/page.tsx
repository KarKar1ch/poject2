"use client";

import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';

interface Company {
  id: number;
  name: string;
  inn: string;
  ogrn: string;
  kpp: string;
  address: string;
  status: string;
  in_reestr: boolean;
  registration_date: string;
  authorized_capital: string;
  main_activity: string;
  taxes_value: string;
  taxes_full: string;
  source: string;
  parsed_at: string;
}

const CompanyByInnPage: React.FC = () => {
  const params = useParams();
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        setLoading(true);
        const inn = params.inn as string;
        
        if (!inn) {
          throw new Error('ИНН не указан');
        }

        // Запрос по ИНН
        const response = await fetch(`http://localhost:5000/rusprofile/companies/inn/${inn}`);
        
        if (!response.ok) {
          throw new Error('Компания не найдена');
        }
        
        const data = await response.json();
        setCompany(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (params.inn) {
      fetchCompany();
    }
  }, [params.inn]);

  // ... остальной код такой же как в CompanyPage
  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>Ошибка: {error}</div>;
  if (!company) return <div>Компания не найдена</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">{company.name}</h1>
      <p>ИНН: {company.inn}</p>
      <p>ОГРН: {company.ogrn}</p>
      {/* остальные данные */}
    </div>
  );
};

export default CompanyByInnPage;