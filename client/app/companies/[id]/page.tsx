"use client";

import { useParams } from 'next/navigation';
import React from 'react';

const CompanyPage: React.FC = () => {
  const params = useParams();
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Страница компании</h1>
      <p className="mt-4">ID компании: {params.id}</p>
    </div>
  );
};

export default CompanyPage;