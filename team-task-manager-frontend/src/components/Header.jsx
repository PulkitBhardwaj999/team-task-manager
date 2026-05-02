import { useState } from 'react';
import { Menu, LogOut, LayoutDashboard, FolderOpen, Users, Settings } from 'lucide-react';
import { useAuth } from '../hooks';
import { ThemeToggle } from './ThemeToggle';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export function Header() {
  const { user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', icon: LayoutDashboard, href: '/' },
    { label: 'Projects', icon: FolderOpen, href: '/projects' },
    { label: 'My Tasks', icon: Users, href: '/tasks' },
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <img src="/images/logo.svg" alt="TaskFlow" className="w-10 h-10" />
            <div>
              <span className="font-bold text-lg text-gray-900 dark:text-white leading-none">TaskFlow</span>
              <div className="text-xs text-gray-500">Team Task Manager</div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                  isActive(item.href)
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-200'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                <item.icon size={18} />
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Right side */}
          <div className="flex items-center gap-4">
            <ThemeToggle />
            
            {/* User menu */}
            <div className="flex items-center gap-3">
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {user?.full_name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {user?.role}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <Menu size={20} />
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <nav className="md:hidden pb-4 space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.href)
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-200'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                <span className="flex items-center gap-2">
                  <item.icon size={18} />
                  {item.label}
                </span>
              </Link>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
}
