"use client"
import { ChartRadialText } from '@/model/Card/Card';
import Header from '@/model/Header/Header';
import React from 'react';
import { useRouter } from 'next/navigation';
import { ChartAreaStacked } from '@/model/Chart-reest/Chart-reest';



const MainPage: React.FC = () => {
  const router = useRouter();

  const handleButtonClick = () => {
    router.push('/tables');
  };

  return (
      <div className='bg-[#ECEDF0] pl-[15px] pr-[15px] h-full pb-[15px]'>
        <Header/>
        <main className='mt-[30px]'>
          <div className='flex justify-between'>
            <ChartRadialText/>
          </div>
          <div className='bg-white mt-[50px] shadow-sm rounded-lg p-[10px]'>
            <div className='mb-[20px] text-[1.2rem] text-bold'>Компаний в реесторе</div>
            <div className="flex justify-center mb-4 w-full">
               <ChartAreaStacked/>
            </div>
            
            <button 
              onClick={handleButtonClick} 
              className='w-full h-[35px] bg-[#3b82f6] rounded-lg transition-all hover:bg-[#2563eb] text-white font-medium'
            >
              Посмотреть в таблице
            </button>
          </div>
        </main>
      </div>
  );
};

export default MainPage;