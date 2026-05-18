import React from 'react';
import Link from 'next/link';
import { Bus } from 'lucide-react';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex w-full bg-background">
      {/* Left side - Illustration/Brand */}
      <div className="hidden lg:flex w-1/2 bg-primary-900 text-white relative overflow-hidden items-center justify-center">
        <div className="absolute inset-0 bg-[linear-gradient(to_bottom_right,var(--color-primary-800),var(--color-primary-900))] opacity-90 z-0"></div>
        
        {/* Subtle decorative circles */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary-700/30 blur-3xl"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-primary-600/20 blur-3xl"></div>
        
        <div className="relative z-10 p-12 max-w-lg flex flex-col items-center text-center">
          <div className="w-20 h-20 bg-primary-500 rounded-2xl flex items-center justify-center mb-8 shadow-xl">
            <Bus className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-display font-bold mb-4 leading-tight">Your Journey Begins With BusYatra</h1>
          <p className="text-primary-100 text-lg">Experience premium bus travel across India. Book tickets seamlessly, track your ride, and travel in comfort.</p>
        </div>
      </div>
      
      {/* Right side - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 lg:p-24 relative">
        <Link href="/" className="absolute top-8 left-8 lg:hidden flex items-center gap-2 font-display font-semibold text-primary-700">
           <Bus className="w-6 h-6" />
           <span className="text-xl tracking-tight">BusYatra</span>
        </Link>
        <div className="w-full max-w-md mx-auto">
          {children}
        </div>
      </div>
    </div>
  )
}
