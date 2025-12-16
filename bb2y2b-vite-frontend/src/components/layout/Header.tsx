import React from 'react';
import { Bell, User } from 'lucide-react';

const pageTitles: Record<string, string> = {
  spaces: 'UP主空间管理',
  videos: '视频管理',
  ai: 'AI配置',
  settings: '系统设置',
};

interface HeaderProps {
  currentPage?: string;
}

export const Header: React.FC<HeaderProps> = ({ currentPage = 'spaces' }) => {
  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-800">
          {pageTitles[currentPage] || 'BB2Y2B'}
        </h2>
      </div>
      <div className="flex items-center space-x-4">
        <button className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100">
          <Bell className="h-5 w-5" />
        </button>
        <button className="flex items-center space-x-2 p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100">
          <User className="h-5 w-5" />
          <span className="text-sm">管理员</span>
        </button>
      </div>
    </header>
  );
};