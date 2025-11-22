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

const CompanyPage: React.FC = () => {
  const params = useParams();
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        setLoading(true);
        const id = params.id as string;
        
        if (!id) {
          throw new Error('ID не указан');
        }

        // 1. Сначала получаем компанию по ID чтобы узнать ИНН
        const companyResponse = await fetch(`http://localhost:5000/companies/${id}`);
        
        if (!companyResponse.ok) {
          throw new Error('Компания не найдена в базе');
        }
        
        const companyData = await companyResponse.json();
        
        // 2. Теперь получаем подробные данные по ИНН
        const inn = companyData.inn;
        const detailsResponse = await fetch(`http://localhost:5000/rusprofile/companies/inn/${inn}`);
        
        if (!detailsResponse.ok) {
          throw new Error('Детали компании не найдены');
        }
        
        const detailsData = await detailsResponse.json();
        setCompany(detailsData);
        
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchCompany();
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="flex items-center justify-center">
          <div className="text-lg">Загрузка данных компании...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="text-red-600 mb-4">Ошибка: {error}</div>
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="text-gray-600">Компания не найдена</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
          <p className="text-gray-600 mt-2">ИНН: {company.inn}</p>
        </div>

        <div className="bg-white rounded-[30px] shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Основная информация</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-500">ОГРН</label>
                <p className="mt-1 text-sm text-gray-900">{company.ogrn}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">КПП</label>
                <p className="mt-1 text-sm text-gray-900">{company.kpp}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Статус</label>
                <p className="mt-1 text-sm text-gray-900">{company.status}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Дата регистрации</label>
                <p className="mt-1 text-sm text-gray-900">{company.registration_date || 'Не указана'}</p>
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-500">Уставный капитал</label>
                <p className="mt-1 text-sm text-gray-900">{company.authorized_capital}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Основной вид деятельности</label>
                <p className="mt-1 text-sm text-gray-900">{company.main_activity || 'Не указан'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Налоги</label>
                <p className="mt-1 text-sm text-gray-900">{company.taxes_full}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">В реестре</label>
                <span className={`inline-flex mt-1 px-3 py-1 text-sm font-semibold rounded-full ${
                  company.in_reestr 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {company.in_reestr ? "Да" : "Нет"}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-[30px] shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Адрес и дополнительные сведения</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-500">Юридический адрес</label>
              <p className="mt-1 text-sm text-gray-900">{company.address}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-500">Источник данных</label>
                <p className="mt-1 text-sm text-gray-900">{company.source}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyPage;