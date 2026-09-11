import React from 'react';
import { NavLink } from 'react-router-dom';
import type { Role } from '../../types';
import { getNavigationForRole } from '../../config/navigation';
import Icon from '../ui/Icon';

interface SidebarProps {
  role: Role;
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ role, isOpen, onClose }) => {
  const routes = getNavigationForRole(role);

  return (
    <>
      {/* DESKTOP PERSISTENT 260px SIDEBAR (>= 1024px) */}
      <aside className="desktop-sidebar-pane hidden lg:flex fixed left-0 bottom-0 w-[260px] bg-primary text-on-primary z-40 flex-col justify-between border-r border-outline/20 shadow-xl top-0">
        <div className="flex flex-col flex-1 overflow-y-auto">
          <div className="h-20 px-5 flex items-center gap-3 border-b border-outline/20 bg-primary-container/40 shrink-0">
            <div className="w-9 h-9 rounded-md bg-primary p-1 border border-outline/30 shrink-0 flex items-center justify-center shadow-sm">
              <img alt="ComplianceSahayak Logo" className="w-full h-full object-contain" src="/brand/compliancesahayak-logo.png" />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-bold tracking-tight text-sm leading-tight truncate">ComplianceSahayak</span>
              <span className="text-[11px] text-on-primary/60 font-normal leading-tight truncate">AI-Assisted Legal Metrology</span>
            </div>
          </div>
          <div className="px-5 pt-5 pb-2 shrink-0">
            <span className="text-[11px] font-semibold tracking-wider text-on-primary/60 uppercase">Operations</span>
          </div>
          <nav className="flex flex-col px-3 space-y-1 pb-4">
            {routes.map((route) => (
              <NavLink
                key={route.path}
                to={route.path}
                end={route.path === '/app/user/scan' || route.path === '/app/history'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg font-semibold text-sm transition-all ${
                    isActive 
                      ? 'bg-primary-fixed text-on-primary-fixed border-l-4 border-traceability' 
                      : 'text-on-primary/70 hover:text-on-primary hover:bg-primary-container/60'
                  }`
                }
              >
                <route.icon className="h-[20px] w-[20px] shrink-0" />
                <span>{route.name}</span>
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="p-4 border-t border-outline/20 bg-primary-container/40 shrink-0">
          <div className="p-3 rounded-lg bg-primary-container/60 border border-outline/20 flex flex-col gap-1.5">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-compliance-compliant shrink-0 animate-pulse"></span>
              <span className="text-[11px] font-bold tracking-wider uppercase truncate">Platform Status: ONLINE</span>
            </div>
            <div className="flex items-center justify-between text-[10px] text-on-primary/60 border-t border-outline/20 pt-1.5 mt-0.5">
              <span>Regulatory Spec</span>
              <span className="font-mono font-medium text-on-primary/80">PCR 2011 / LM Act</span>
            </div>
          </div>
        </div>
      </aside>

      {/* COLLAPSIBLE MOBILE/TABLET SLIDE-OUT DRAWER */}
      {/* Backdrop Overlay */}
      <div 
        className={`fixed inset-0 bg-primary/60 z-50 lg:hidden transition-opacity ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
      />
      
      {/* Mobile Drawer */}
      <nav 
        className={`fixed top-0 bottom-0 left-0 w-[260px] max-w-[80vw] bg-primary border-r border-outline/20 flex flex-col justify-between shadow-2xl z-50 text-on-primary overflow-y-auto lg:hidden transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex flex-col">
          <div className="h-16 px-4 flex items-center justify-between border-b border-outline/20 bg-primary-container/40">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-md bg-primary p-1 border border-outline/30 shrink-0 flex items-center justify-center">
                <img alt="ComplianceSahayak Logo" className="w-full h-full object-contain" src="/brand/compliancesahayak-logo.png" />
              </div>
              <span className="font-bold text-sm tracking-tight truncate">ComplianceSahayak</span>
            </div>
            <button 
              aria-label="Close navigation" 
              className="text-on-primary/60 hover:text-on-primary p-1 rounded-lg hover:bg-primary-container focus:outline-none shrink-0"
              onClick={onClose}
            >
              <Icon name="close" className="text-[20px]" />
            </button>
          </div>
          <div className="px-4 pt-4 pb-2">
            <span className="text-[11px] font-semibold tracking-wider text-on-primary/60 uppercase">Operations</span>
          </div>
          <div className="flex flex-col px-3 space-y-1">
            {routes.map((route) => (
              <NavLink
                key={route.path}
                to={route.path}
                end={route.path === '/app/user/scan' || route.path === '/app/history'}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-2 rounded-lg font-semibold text-xs transition-colors ${
                    isActive 
                      ? 'bg-primary-fixed text-on-primary-fixed' 
                      : 'text-on-primary/70 hover:bg-primary-container/60 hover:text-on-primary'
                  }`
                }
              >
                <route.icon className="h-[18px] w-[18px] shrink-0" />
                <span>{route.name}</span>
              </NavLink>
            ))}
          </div>
        </div>
        <div className="p-4 border-t border-outline/20 bg-primary-container/40">
          <div className="p-2.5 rounded-lg bg-primary-container/60 border border-outline/20 flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-compliance-compliant shrink-0 animate-pulse"></span>
              <span className="text-[11px] font-bold uppercase tracking-wide">Platform Status: ONLINE</span>
            </div>
            <div className="flex items-center justify-between text-[10px] text-on-primary/60 border-t border-outline/20 pt-1 mt-0.5">
              <span>{role === 'officer' ? 'Inspector #OP-408' : 'User Account'}</span>
              <span className="font-mono font-medium text-on-primary/80">PCR 2011 / LM Act</span>
            </div>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Sidebar;
