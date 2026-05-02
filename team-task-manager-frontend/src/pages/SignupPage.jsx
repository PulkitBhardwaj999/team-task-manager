import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks';
import { useToast } from '../components/Toast';
import { LoadingSkeleton } from '../components/Skeleton';

export function SignupPage() {
  const navigate = useNavigate();
  const { signup, isAuthenticated, loading } = useAuth();
  const { showToast } = useToast();

  const [formData, setFormData] = useState({
    email: '',
    fullName: '',
    password: '',
    confirmPassword: '',
    role: 'member' // default role
  });

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

    if (!formData.email || !formData.fullName || !formData.password) {
      showToast('Please fill in all fields', 'warning');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      showToast('Passwords do not match', 'error');
      return;
    }

    if (formData.password.length < 8) {
      showToast('Password must be at least 8 characters', 'warning');
      return;
    }

    setIsLoading(true);

    // Debug: log the data being sent
    console.log('Signup data:', {
      email: formData.email,
      fullName: formData.fullName,
      role: formData.role.toLowerCase()
    });

    // Pass role to backend
    const success = await signup(
      formData.email,
      formData.fullName,
      formData.password,
      formData.role.toLowerCase()
    );

    setIsLoading(false);

    if (success) {
      showToast('Account created successfully!', 'success');
      navigate('/');
    } else {
      showToast('Signup failed. Please try again.', 'error');
    }
  };

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        {/* Logo Section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl mb-4 shadow-lg">
            <span className="text-white font-bold text-2xl">T</span>
          </div>
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-100">
            Create Account
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2 font-medium">
            Join Team Task Manager today
          </p>
        </div>

        {/* Form Card */}
        <div className="card p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* Full Name */}
            <div>
              <label className="label">Full Name</label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                placeholder="John Doe"
                className="input"
                required
              />
            </div>

            {/* Email */}
            <div>
              <label className="label">Email Address</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                className="input"
                required
              />
            </div>

            {/* Role */}
            <div>
              <label className="label">Account Role</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="input"
              >
                <option value="member">👤 Member - Regular user access</option>
                <option value="admin">👑 Admin - Full access</option>
              </select>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 font-medium">
                Select Admin for elevated permissions in projects
              </p>
            </div>

            {/* Password */}
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="input"
                required
                autoComplete="new-password"
              />
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
                Minimum 8 characters required
              </p>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="label">Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="input"
                required
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full mt-2"
            >
              {isLoading ? '🔄 Creating account...' : '✨ Create Account'}
            </button>

          </form>

          {/* Divider */}
          <div className="my-6 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-800"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400">
                Already have an account?
              </span>
            </div>
          </div>

          {/* Login Link */}
          <button
            onClick={() => navigate('/login')}
            className="btn-secondary w-full"
          >
            Sign In Instead
          </button>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-slate-600 dark:text-slate-400 mt-6">
          By signing up, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}