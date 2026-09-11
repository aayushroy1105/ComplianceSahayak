import React from 'react';
import * as LucideIcons from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface IconProps {
  name: string;
  className?: string;
  onClick?: () => void;
}

const iconMap: Record<string, keyof typeof LucideIcons> = {
  description: 'FileText',
  error: 'AlertCircle',
  visibility: 'Eye',
  visibility_off: 'EyeOff',
  check_circle: 'CheckCircle2',
  document_scanner: 'ScanLine',
  photo_camera_front: 'Camera',
  cloud_upload: 'UploadCloud',
  radio_button_checked: 'CheckCircle',
  auto_fix_high: 'Wand2',
  gavel: 'Gavel',
  arrow_forward: 'ArrowRight',
  search: 'Search',
  calendar_today: 'Calendar',
  filter_list: 'Filter',
  picture_as_pdf: 'FileText',
  task_alt: 'CheckCircle2',
  query_stats: 'LineChart',
  bookmark_border: 'Bookmark',
  restart_alt: 'RotateCcw',
  lock: 'Lock',
  grid_on: 'Grid',
  crop: 'Crop',
  add_a_photo: 'Camera',
  photo_camera_back: 'Camera',
  folder_open: 'FolderOpen',
  pending_actions: 'Clock',
  verified: 'CheckCircle2',
  refresh: 'RefreshCw',
  download: 'Download',
  add: 'Plus',
  warning: 'AlertTriangle',
  center_focus_strong: 'Focus',
  schedule: 'Clock',
  info: 'Info',
  fact_check: 'ListChecks',
  wb_sunny: 'Sun',
  straighten: 'Ruler',
  summarize: 'FileSpreadsheet',
  archive: 'Archive',
  expand_more: 'ChevronDown',
  inventory_2: 'Package',
  history: 'History',
  menu: 'Menu',
  close: 'X',
  more_vert: 'MoreVertical',
  notifications: 'Bell',
  account_circle: 'User',
  logout: 'LogOut',
  dashboard: 'LayoutDashboard',
  assignment: 'ClipboardList',
  map: 'Map',
  business: 'Building2',
  timeline: 'TrendingUp',
  gavel_outline: 'Gavel',
  rule: 'ShieldAlert',
  policy: 'ShieldCheck',
  view_in_ar: 'Box',
  zoom_in: 'ZoomIn',
  zoom_out: 'ZoomOut',
  open_in_new: 'ExternalLink',
  cancel: 'XCircle',
  verified_user: 'ShieldCheck',
  share: 'Share2',
  alternate_email: 'Mail',
  lock_open: 'Unlock'
};

const Icon: React.FC<IconProps> = ({ name, className, onClick }) => {
  const lucideName = iconMap[name.trim()] || 'Circle';
  const LucideIconComponent = LucideIcons[lucideName] as LucideIcon;
  
  if (!LucideIconComponent) {
    console.warn(`Icon not found: ${name} (mapped to ${lucideName})`);
    const FallbackIcon = LucideIcons.Circle as LucideIcon;
    return <FallbackIcon className={className} onClick={onClick} />;
  }
  
  return <LucideIconComponent className={className} onClick={onClick} />;
};

export default Icon;
