"use client"
import { ChartRadialText } from '@/model/Card/Card';
import Header from '@/model/Header/Header';
import React from 'react';
import { useRouter } from 'next/navigation';



const MainPage: React.FC = () => {
  const router = useRouter();

  const handleButtonClick = () => {
    router.push('/tables');
  };

  return (
    <div className='bg-[#ECEDF0] pl-[15px] pr-[15px] h-screen'>
      <Header/>
      <main className='mt-[30px] '>
        <div className='flex justify-between'>
          <ChartRadialText/>
        </div>
        <div className='bg-white mt-[50px] shadow-sm rounded-lg p-[10px]'>
          <div className='mb-[20px] text-[1.2rem]'>Компании в реесторе</div>
          <button onClick={handleButtonClick} className='w-[200px] h-[30px] bg-[#3b82f6] rounded-lg transition-all  hover:bg-[#2563eb] '>Посмотреть в таблице</button>
        </div>
      </main>
    </div>
  );
};

export default MainPage;