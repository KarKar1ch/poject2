"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function Header(){
    const [searchValue, setSearchValue] = useState('');
    const router = useRouter();

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        
        
        if (searchValue.trim()) {
           
            router.push(`/companies/inn/${searchValue.trim()}`);
        }
    };

    return(
        <header className="">
            <div className="p-[10px] w-full flex">
                <form onSubmit={handleSearch} className="w-full">
                    <input 
                        value={searchValue}
                        onChange={(e) => setSearchValue(e.target.value)}
                        className="w-full bg-white rounded-[30px] border border-[#00000014] h-[45px] pl-[10px] shadow-sm" 
                        placeholder="Наименование, ИНН, ОРГН, Руководитель"
                    />
                </form>
                <div className="flex ml-[20px]">
                    <button className="w-[45px] h-[45px] rounded-[100%] bg-white p-[11px]">
                        <Image src="/bell_24.svg" alt="bell" width={24} height={24}/>
                    </button>
                    <button className="w-[45px] h-[45px] rounded-[100%] bg-[#5D39F5] ml-[10px] text-white">A</button>
                </div>
            </div>
        </header>
    )
}