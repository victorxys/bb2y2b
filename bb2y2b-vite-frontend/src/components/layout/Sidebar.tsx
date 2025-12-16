import React from 'react';
import { Users, Video, Settings, Cpu, Download } from 'lucide-react';

interface MenuItem {
  name: string;
  icon: React.ReactNode;
  page: string;
}

const menuItems: MenuItem[] = [
  { name: 'UP主空间', icon: <Users className="h-5 w-5" />, page: 'spaces' },
  { name: '视频管理', icon: <Video className="h-5 w-5" />, page: 'videos' },
  { name: '下载管理', icon: <Download className="h-5 w-5" />, page: 'downloads' },
  { name: 'AI配置', icon: <Cpu className="h-5 w-5" />, page: 'ai' },
  { name: '系统设置', icon: <Settings className="h-5 w-5" />, page: 'settings' },
];

interface SidebarProps {
  currentPage?: string;
  onNavigate?: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage = 'spaces', onNavigate }) => {
  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">BB2Y2B</h1>
        <p className="text-sm text-gray-400">B站视频管理系统</p>
      </div>
      <nav className="p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.name}>
              <button
                onClick={() => onNavigate?.(item.page)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  currentPage === item.page
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
              >
                {item.icon}
                <span>{item.name}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};