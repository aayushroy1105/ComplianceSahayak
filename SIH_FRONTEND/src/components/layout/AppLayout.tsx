import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopHeader from './TopHeader';
import type { Role } from '../../types';

interface AppLayoutProps {
  role: Role;
}

const AppLayout: React.FC<AppLayoutProps> = ({ role }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="bg-background font-body text-on-background antialiased min-h-screen flex flex-col relative">
      <Sidebar 
        role={role} 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
      />
      {/* CONTENT WRAPPER */}
      <div className="main-pl-offset lg:pl-[260px] flex-1 flex flex-col min-w-0 transition-all duration-300">
        <TopHeader 
          role={role} 
          onMenuToggle={() => setIsSidebarOpen(true)} 
        />
        <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8 min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
