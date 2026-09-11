import { 
  LayoutDashboard, 
  ScanLine, 
  History, 
  Users, 
  BarChart3, 
  Map as MapIcon,
  ShieldCheck,
  FileText,
  BookOpen
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { Role } from '../types';

export interface NavItem {
  name: string;
  path: string;
  icon: LucideIcon;
  roles: Role[];
}

export const NAVIGATION_CONFIG: NavItem[] = [
// User Routes
  { name: 'Dashboard', path: '/app/user/dashboard', icon: LayoutDashboard, roles: ['user'] },
  { name: 'New Scan', path: '/app/user/scan/new', icon: ScanLine, roles: ['user'] },
  { name: 'Scan History', path: '/app/user/scan', icon: History, roles: ['user'] },
  
  // Officer Routes
  { name: 'Dashboard', path: '/app', icon: LayoutDashboard, roles: ['officer'] },
  { name: 'New Inspection', path: '/app/inspection/new', icon: ShieldCheck, roles: ['officer'] },
  { name: 'Inspection Dossiers', path: '/app/history', icon: History, roles: ['officer'] },
  { name: 'Compliance Rules', path: '/app/rules', icon: BookOpen, roles: ['officer'] },
  { name: 'Verified Registry', path: '/app/manufacturer', icon: Users, roles: ['officer'] },
  { name: 'Reports', path: '/app/reports', icon: FileText, roles: ['officer'] },
  { name: 'Analytics', path: '/app/analytics', icon: BarChart3, roles: ['officer'] },
  { name: 'Map View', path: '/app/map', icon: MapIcon, roles: ['officer'] },
];

export const getNavigationForRole = (role: Role): NavItem[] => {
  return NAVIGATION_CONFIG.filter(item => item.roles.includes(role));
};
