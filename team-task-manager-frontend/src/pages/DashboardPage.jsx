import { useEffect, useRef, useState } from 'react';
import { Header } from '../components/Header';
import { useToast, ToastContainer } from '../components/Toast';
import { TaskStatsChart, PriorityChart } from '../components/Charts';
import { LoadingSkeleton } from '../components/Skeleton';
import { dashboardService } from '../services';
import { useAuth } from '../hooks';
import { BarChart3, CheckCircle, AlertCircle, Zap } from 'lucide-react';

export function DashboardPage() {
  const { user } = useAuth();
  const { toasts, removeToast } = useToast();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const fetchedStatsRef = useRef(false);

  useEffect(() => {
    if (fetchedStatsRef.current) {
      return;
    }

    fetchedStatsRef.current = true;
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await dashboardService.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.full_name.split(' ')[0]}! 👋
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Here's your task overview for today
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Tasks
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats?.total_tasks || 0}
                </p>
              </div>
              <div className="p-3 bg-primary-100 dark:bg-primary-900 rounded-lg">
                <BarChart3 size={24} className="text-primary-600 dark:text-primary-400" />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Completed
                </p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                  {stats?.completed_tasks || 0}
                </p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <CheckCircle size={24} className="text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Pending
                </p>
                <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-2">
                  {stats?.pending_tasks || 0}
                </p>
              </div>
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <Zap size={24} className="text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Overdue
                </p>
                <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
                  {stats?.overdue_tasks || 0}
                </p>
              </div>
              <div className="p-3 bg-red-100 dark:bg-red-900 rounded-lg">
                <AlertCircle size={24} className="text-red-600 dark:text-red-400" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Task Overview
            </h2>
            {stats && <TaskStatsChart data={stats} />}
          </div>

          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Priority Distribution
            </h2>
            {stats && <PriorityChart data={stats.tasks_by_priority} />}
          </div>
        </div>

        {/* Project Stats */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Project Summary
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Projects</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {stats?.total_projects || 0}
              </p>
            </div>
            {Object.entries(stats?.tasks_by_status || {}).map(([status, count]) => (
              <div key={status}>
                <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                  {status.replace('_', ' ')}
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {count}
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
}
