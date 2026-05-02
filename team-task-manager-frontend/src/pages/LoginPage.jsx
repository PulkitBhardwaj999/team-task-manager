import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks';
import { useToast } from '../components/Toast';
import { LoadingSkeleton } from '../components/Skeleton';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, isAuthenticated, loading } = useAuth();
  const { showToast } = useToast();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.email || !formData.password) {
      showToast('Please fill in all fields', 'warning');
      return;
    }

    setIsLoading(true);
    const success = await login(formData.email, formData.password);
    setIsLoading(false);

    if (success) {
      showToast('Login successful!', 'success');
      navigate('/');
    } else {
      showToast('Login failed. Please check your credentials.', 'error');
    }
  };

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg mb-4">
            <span className="text-white font-bold text-xl">T</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            TaskFlow
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Organize your projects and tasks efficiently
          </p>
        </div>

        {/* Form */}
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="label">Email</label>
              <input
                id="email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                className="input"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="label">Password</label>
              <input
                id="password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="input"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6">
            <p className="text-center text-sm text-gray-600 dark:text-gray-400">
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/signup')}
                className="text-primary-600 dark:text-primary-400 font-semibold hover:underline"
              >
                Sign Up
              </button>
            </p>
          </div>
        </div>

        {/* Demo credentials */}
        <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-xs font-semibold text-blue-900 dark:text-blue-300 mb-2">
            Demo Credentials:
          </p>
          <p className="text-xs text-blue-700 dark:text-blue-400">
            Email: <code className="bg-white dark:bg-gray-800 px-1 rounded">admin@admin.com</code>
          </p>
          <p className="text-xs text-blue-700 dark:text-blue-400">
            Password: <code className="bg-white dark:bg-gray-800 px-1 rounded">admin@123</code>
          </p>
        </div>
      </div>
    </div>
  );
}
