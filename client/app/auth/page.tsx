
"use client"
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';


export default function AuthPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('userEmail', email);
    
    
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-[#ECEDF0] from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-[50px] shadow-xl p-8">
        <div className="text-center mb-8 ">
          <div className='w-[60px] h-[70px] rounded-[20px] bg-[#5D39F50D] flex justify-center m-auto'><Image src="/login_24.svg" alt="door" width={30} height={30}/></div>  
          <h1 className="text-3xl font-bold text-gray-900 mb-2 mt-[15px]">Войдите в систему</h1>
          <p>Войдите, чтобы настроить обмен данными между системами</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-[50px] focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              placeholder="Почта"
              required
            />
          </div>

          <div>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-[50px] focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              placeholder="Пароль"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-[#5D39F5] text-white py-3 px-4 rounded-[50px] hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Войти
          </button>
        </form>
      </div>
    </div>
  );
}