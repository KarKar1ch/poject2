'use client'
import { useCompanies } from "@/hook/useCompanies";
import Tables from "@/model/Tables/Tables";


export default function TablesPage(){
    const { data, loading, error } = useCompanies();

    return(
        <div>
            <div>
                <Tables data={data} />
            </div>
        </div>
    )

};