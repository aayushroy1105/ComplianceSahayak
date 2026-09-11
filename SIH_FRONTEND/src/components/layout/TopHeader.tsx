import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Role } from '../../types';
import Icon from '../ui/Icon';
import { useAuth } from '../../contexts/AuthContext';

interface TopHeaderProps {
  role: Role;
  onMenuToggle: () => void;
}

const TopHeader: React.FC<TopHeaderProps> = ({ role, onMenuToggle }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  return (
    <>
      {/* TABLET & MOBILE UNIFIED TOP NAV BAR (< 1024px) */}
      <header className="tablet-mobile-header lg:hidden sticky z-30 bg-surface-container-lowest text-on-surface border-b border-outline/20 shadow-sm px-4 py-3 flex items-center justify-between gap-3 top-0">
        <div className="flex items-center gap-3 min-w-0">
          <button 
            aria-label="Toggle navigation" 
            className="p-1.5 -ml-1 text-on-surface/70 hover:text-on-surface rounded-lg hover:bg-surface-container focus:outline-none" 
            onClick={onMenuToggle}
          >
            <Icon name="menu" className="text-[22px]" />
          </button>
          <div className="w-8 h-8 rounded-md bg-primary p-1 border border-outline/30 shrink-0 flex items-center justify-center shadow-sm">
            <img alt="ComplianceSahayak Logo" className="w-full h-full object-contain" src="/brand/compliancesahayak-logo.png" />
          </div>
          <div className="flex flex-col truncate">
            <span className="font-bold text-sm tracking-tight truncate">ComplianceSahayak</span>
            <span className="text-[11px] text-on-surface/60 truncate">AI-Assisted Legal Metrology</span>
          </div>
        </div>
        <div className="flex items-center gap-2.5 shrink-0">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-compliance-compliant/10 border border-compliance-compliant/20 text-compliance-compliant text-[11px] font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-compliance-compliant animate-pulse"></span>
            <span className="hidden sm:inline">System Operational</span>
          </div>
          <div className="relative flex items-center justify-center">
            <div className="w-8 h-8 rounded-full bg-primary text-on-primary border border-outline/20 flex items-center justify-center text-xs font-semibold" title={role === 'officer' ? "Inspector #OP-408" : "User Profile"}>
              <Icon name="person" className="text-[17px]" />
            </div>
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-compliance-compliant border-2 border-surface-container-lowest"></span>
          </div>
          <button 
            onClick={handleLogout}
            className="p-1.5 text-slate-500 hover:text-rose-600 rounded-lg hover:bg-slate-100 transition-colors"
            title="Sign Out"
            type="button"
          >
            <Icon name="logout" className="text-[18px]" />
          </button>
        </div>
      </header>

      {/* DESKTOP TOP HEADER (≥ 1024px) */}
      <header className="desktop-header-pane hidden lg:flex sticky bg-surface-container-lowest border-b border-outline/20 z-30 px-8 py-4 items-center justify-between shadow-sm top-0">
        <div className="flex items-center gap-3.5 min-w-0">
          <div className="w-8 h-8 rounded-md bg-primary p-1 border border-outline/30 flex items-center justify-center shrink-0 shadow-sm">
            <img alt="ComplianceSahayak Logo" className="w-full h-full object-contain" src="/brand/compliancesahayak-logo.png" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-on-surface tracking-tight text-base leading-tight">ComplianceSahayak</span>
            <span className="text-xs text-on-surface/60 font-normal">AI-Assisted Legal Metrology Compliance Platform</span>
          </div>
        </div>
        <div className="flex items-center gap-4 shrink-0">
          {/* Status Pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-compliance-compliant/10 border border-compliance-compliant/20 text-compliance-compliant text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-compliance-compliant animate-pulse"></span>
            <span>System Operational</span>
          </div>
          <div className="h-6 w-px bg-outline/20"></div>
          {/* Officer Profile Pill */}
          <div className="flex items-center gap-3 pl-1">
            <div className="flex flex-col text-right">
              <span className="text-xs font-semibold text-on-surface">{role === 'officer' ? 'Compliance Officer' : 'Citizen Access'}</span>
              <span className="text-[11px] font-mono text-on-surface/60">{role === 'officer' ? 'Inspector #OP-408' : 'Verified User'}</span>
            </div>
            <div className="relative">
              <div className="w-9 h-9 rounded-full bg-primary text-on-primary flex items-center justify-center font-semibold text-xs shadow-sm">
                <Icon name="person" className="text-[18px]" />
              </div>
              <span className="absolute top-0 right-0 w-2.5 h-2.5 rounded-full bg-compliance-compliant border-2 border-surface-container-lowest"></span>
            </div>
            <button 
              onClick={handleLogout}
              className="flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-rose-50 hover:text-rose-600 text-slate-600 rounded-lg text-xs font-semibold border border-slate-200 transition-colors ml-2"
              title="Sign Out"
              type="button"
            >
              <Icon name="logout" className="text-[16px]" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </header>
    </>
  );
};

export default TopHeader;
