"use client"
import PieDonutText from '@/model/Card/Card';
import { ChartRadialText2 } from '@/model/Card/Card2';
import { ChartRadialText3 } from '@/model/Card/Card3';
import Header from '@/model/Header/Header';
import React from 'react';
import { useRouter } from 'next/navigation';
import { ChartAreaStacked } from '@/model/Chart-reest/Chart-reest';



const MainPage: React.FC = () => {
  const router = useRouter();

  const handleButtonClick = () => {
    router.push('/tables');
  };


  const data = [
    { name: "Chrome", value: 375, color: "#10b98120" },
    { name: "Safari", value: 50, color: "#10b981" },
  ]


  return (
      <div className='bg-[#ECEDF0] pl-[15px] pr-[15px] h-full pb-[15px]'>
        <Header/>        
        <main className='mt-[30px]'>
          <div className='flex justify-between'>
            <PieDonutText data={data}/>
            <ChartRadialText2/>
            <ChartRadialText3/>
          </div>
          <div className='bg-white mt-[50px] shadow-sm rounded-[30px] p-[15px]'>
            <div className='mb-[20px] text-[1.4rem] font-semibold'>Компаний в реестре</div>
            <div className="flex justify-center mb-4 w-full">
               <ChartAreaStacked/>
            </div>
            
            <button 
              onClick={handleButtonClick} 
              className='w-full h-[40px] bg-[#5D39F5] rounded-[30px] transition-all hover:bg-[#2563eb] text-white font-medium'
            >
              Посмотреть в таблице
            </button>
          </div>
        </main>
      </div>
  );
};

export default MainPage;