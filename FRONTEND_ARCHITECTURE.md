# 🎨 Frontend Architecture Guide

## React Component Architecture

```
App
  ├── Router
  │   └── Routes
  │       ├── LoginPage
  │       ├── SignupPage
  │       └── Protected Routes
  │           ├── DashboardPage
  │           ├── ProjectsPage
  │           ├── ProjectTasksPage
  │           └── MyTasksPage
  │
  ├── AuthContext
  │   └── Manages auth state globally
  │
  ├── Services
  │   ├── api.js (Axios instance)
  │   └── index.js (API methods)
  │
  └── Components
      ├── Header
      ├── TaskCard
      ├── Modal
      ├── Charts
      ├── Toast
      └── ...
```

---

## Folder Structure Explained

### `src/pages/`
**Page components for routing**

- `LoginPage.jsx` - User login
- `SignupPage.jsx` - User registration
- `DashboardPage.jsx` - Main dashboard with stats
- `ProjectsPage.jsx` - List and manage projects
- `ProjectTasksPage.jsx` - Tasks within a project
- `MyTasksPage.jsx` - Tasks assigned to user

### `src/components/`
**Reusable UI components**

- `Header.jsx` - Top navigation
- `TaskCard.jsx` - Task display component
- `Modal.jsx` - Reusable modal dialog
- `Charts.jsx` - Recharts visualizations
- `Toast.jsx` - Notification system
- `Skeleton.jsx` - Loading skeletons
- `ThemeToggle.jsx` - Dark/light mode
- `ProtectedRoute.jsx` - Route protection

### `src/services/`
**API communication**

- `api.js` - Axios instance with interceptors
- `index.js` - API service methods

**Authentication Interceptors:**
```javascript
// Request: Add token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response: Handle 401, refresh token
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
    }
  }
);
```

### `src/context/`
**Global state management**

- `AuthContext.jsx` - Authentication context
  - Provides: user, loading, login, logout, signup
  - Wraps entire app for auth state access

### `src/hooks/`
**Custom React hooks**

- `index.js`:
  - `useAuth()` - Access auth context
  - `useLocalStorage()` - Persist state to localStorage

### `src/styles/`
**Global styles and CSS**

- `globals.css` - Tailwind imports, custom classes, animations

---

## State Management

### Global State (AuthContext)
```javascript
const { user, isAuthenticated, login, logout, loading } = useAuth();
```

### Local State (useState)
```javascript
const [tasks, setTasks] = useState([]);
const [filters, setFilters] = useState({ status: '', priority: '' });
```

### Side Effects (useEffect)
```javascript
useEffect(() => {
  fetchTasks(); // Fetch when component mounts
}, [projectId]); // Re-fetch when projectId changes
```

---

## Component Hierarchy Example

### Page Component
```jsx
function ProjectTasksPage() {
  const { projectId } = useParams();
  const [tasks, setTasks] = useState([]);
  
  useEffect(() => {
    fetchProjectAndTasks();
  }, [projectId]);
  
  return (
    <div>
      <Header />
      <main>
        {tasks.map(task => (
          <TaskCard key={task.id} task={task} onEdit={handleEdit} />
        ))}
      </main>
    </div>
  );
}
```

### Component Composition
```jsx
<ProjectTasksPage>
  <Header />
  <SearchBar />
  <TaskList>
    <TaskCard />
    <TaskCard />
    <TaskCard />
  </TaskList>
  <Modal>
    <TaskForm />
  </Modal>
</ProjectTasksPage>
```

---

## Data Flow

### Request Flow
```
User Action (click, submit)
    ↓
Event Handler triggered
    ↓
Call API Service
    ↓
Axios sends request with token
    ↓
Backend processes request
    ↓
Response received
    ↓
Update component state
    ↓
Component re-renders
    ↓
UI updates
```

### State Update Pattern
```javascript
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  fetchData();
}, []);

const fetchData = async () => {
  try {
    setLoading(true);
    const response = await apiService.getData();
    setData(response.data);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

---

## Styling Strategy

### Tailwind CSS Classes
```jsx
<button className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-white">
  Click me
</button>
```

### Custom Components
```css
@layer components {
  .card {
    @apply bg-white dark:bg-gray-900 rounded-lg shadow-sm;
  }
  
  .btn-primary {
    @apply px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600;
  }
}
```

### Responsive Design
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* 1 column on mobile, 2 on tablet, 3 on desktop */}
</div>
```

### Dark Mode
```jsx
// Tailwind automatically applies dark: classes
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Content adapts to dark mode
</div>
```

---

## Performance Optimization

### Code Splitting
```javascript
// React Router lazy loading
const DashboardPage = lazy(() => import('./pages/DashboardPage'));

// With Suspense
<Suspense fallback={<LoadingSkeleton />}>
  <DashboardPage />
</Suspense>
```

### Memoization
```javascript
// Prevent unnecessary re-renders
const TaskCard = React.memo(({ task, onEdit }) => {
  return <div>{task.title}</div>;
});
```

### useMemo for expensive calculations
```javascript
const filteredTasks = useMemo(() => {
  return tasks.filter(task => task.status === filter);
}, [tasks, filter]);
```

### useCallback for stable function references
```javascript
const handleEdit = useCallback((task) => {
  // Won't recreate on every render
}, []);
```

---

## Error Handling

### API Error Handling
```javascript
try {
  const response = await taskService.createTask(data);
  showToast('Task created!', 'success');
} catch (error) {
  const message = error.response?.data?.detail || 'Failed to create task';
  showToast(message, 'error');
}
```

### Form Validation
```javascript
if (!formData.title.trim()) {
  showToast('Title is required', 'warning');
  return;
}
```

### Authentication Errors
```javascript
// Auto-handled by interceptor
// On 401: Try refresh token
// If fails: Redirect to login
```

---

## Real-time Features

### Polling (Simple)
```javascript
useEffect(() => {
  const interval = setInterval(() => {
    fetchTasks(); // Poll every 5 seconds
  }, 5000);
  
  return () => clearInterval(interval);
}, []);
```

### Real-time with WebSocket (Advanced)
```javascript
useEffect(() => {
  const socket = io('http://localhost:8000');
  socket.on('task-updated', (task) => {
    setTasks(prev => prev.map(t => t.id === task.id ? task : t));
  });
}, []);
```

---

## Accessibility Features

### Semantic HTML
```jsx
<button aria-label="Close menu" onClick={close}>
  <X size={20} />
</button>
```

### ARIA Attributes
```jsx
<div role="alert" className="bg-red-100">
  Error message
</div>
```

### Keyboard Navigation
```jsx
<input
  type="text"
  onKeyDown={(e) => {
    if (e.key === 'Escape') close();
  }}
/>
```

---

## Testing Patterns

### Component Test
```javascript
import { render, screen } from '@testing-library/react';
import { TaskCard } from './TaskCard';

test('renders task title', () => {
  render(<TaskCard task={{ title: 'Test Task' }} />);
  expect(screen.getByText('Test Task')).toBeInTheDocument();
});
```

### Hook Test
```javascript
import { renderHook, act } from '@testing-library/react';
import { useAuth } from './hooks';

test('login changes auth state', () => {
  const { result } = renderHook(() => useAuth());
  
  act(() => {
    result.current.login('test@example.com', 'password');
  });
  
  expect(result.current.isAuthenticated).toBe(true);
});
```

---

## Deployment Optimization

### Build Output
```bash
npm run build
# Output: dist/ folder optimized for production
```

### Environment Variables
```javascript
// Production API URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
```

### Bundle Size
- Recharts: ~50KB
- Axios: ~14KB
- React Router: ~13KB
- Total: ~200KB (gzipped ~60KB)

---

## Best Practices

✅ **Do:**
- Use functional components with hooks
- Keep components small and focused
- Use Context for global state
- Memoize expensive computations
- Handle errors gracefully
- Use TypeScript (optional but recommended)
- Test critical functionality
- Optimize bundle size

❌ **Don't:**
- Over-use useState at top level
- Mix UI logic and business logic
- Create deeply nested components
- Use inline functions in renders
- Forget error boundaries
- Make API calls in render

---

## Future Enhancements

1. **TypeScript** - Add type safety
2. **Storybook** - Component library
3. **Testing** - Vitest + React Testing Library
4. **Performance** - Web Workers, Virtual Scrolling
5. **Offline** - Service Workers, IndexedDB
6. **i18n** - Multi-language support
7. **E2E Testing** - Cypress or Playwright
8. **State Management** - Redux or Zustand if needed

---

**This frontend is built for scalability and maintainability.** 🚀
