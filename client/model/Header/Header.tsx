import Image from "next/image"


export default function Header(){
    return(
        <header>
            <div className="p-[10px] w-full flex">
                <div className=" w-full"><input className="w-full bg-white rounded-2xl border border-[#00000014] h-[35px] pl-[10px]" placeholder="Наименование, ИНН, ОРГН, Руководитель"/></div>
                <div className="flex ml-[20px]">
                    <button className="w-[35px] h-[35px] rounded-[100%] bg-white p-[6px]"><Image src="bell_24.svg" alt="bell" width={24} height={24}/></button>
                    <button className="w-[35px] h-[35px] rounded-[100%] bg-[#3b82f6] ml-[10px] text-white">A</button>
                </div>
            </div>
        </header>
    )
}