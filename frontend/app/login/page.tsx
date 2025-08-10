"use client";
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to landing page - auth modal will handle authentication
    router.replace('/');
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-navy via-darker-navy to-dark-navy flex items-center justify-center">
      <div className="text-white text-center">
        <h1 className="text-2xl mb-4">Redirecting to CoinGrok...</h1>
        <div className="animate-spin w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full mx-auto"></div>
      </div>
    </div>
  );
}