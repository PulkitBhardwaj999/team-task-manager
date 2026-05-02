import { useEffect, useState, useContext } from 'react';
import { Header } from '../components/Header';
import { Modal } from '../components/Modal';
import { TaskCard } from '../components/TaskCard';
import { useToast, ToastContainer } from '../components/Toast';
import { LoadingSkeleton, TaskSkeleton } from '../components/Skeleton';
import { taskService } from '../services';
import { AuthContext } from '../context/AuthContext';
import { Search, AlertCircle } from 'lucide-react';

export function MyTasksPage() {
  const { toasts, removeToast, showToast } = useToast();
  const [tasks, setTasks] = useState([]);
  const [overdueTasks, setOverdueTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOverdue, setFilterOverdue] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [formData, setFormData] = useState({ title: '', description: '', priority: 'medium', dueDate: '', assignedTo: null });
  const { user: currentUser } = useContext(AuthContext);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const [tasksRes, overdueRes] = await Promise.all([
        taskService.getMyTasks(),
        taskService.getOverdueTasks()
      ]);
      setTasks(tasksRes.data);
      setOverdueTasks(overdueRes.data);
    } catch (error) {
      showToast('Failed to load tasks', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTask = async (taskId, updates) => {
    try {
      await taskService.updateTask(taskId, updates);
      showToast('Task updated', 'success');
      fetchTasks();
    } catch (error) {
      showToast('Failed to update task', 'error');
    }
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description,
      priority: task.priority,
      dueDate: task.due_date ? task.due_date.split('T')[0] : '',
      assignedTo: task.assigned_to
    });
    setIsModalOpen(true);
  };

  const handleSaveTask = async () => {
    if (!formData.title.trim()) return showToast('Task title required', 'warning');
    try {
      await taskService.updateTask(editingTask.id, {
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        due_date: formData.dueDate || null,
        assigned_to: formData.assignedTo
      });
      showToast('Task updated', 'success');
      setIsModalOpen(false);
      fetchTasks();
    } catch (err) {
      showToast(err?.response?.data?.detail || 'Failed to update task', 'error');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await taskService.deleteTask(taskId);
        showToast('Task deleted successfully', 'success');
        fetchTasks();
      } catch (error) {
        showToast('Failed to delete task', 'error');
      }
    }
  };

  const filteredTasks = (filterOverdue ? overdueTasks : tasks).filter(task =>
    task.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-4">
            {[1, 2, 3].map(i => <TaskSkeleton key={i} />)}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            My Tasks
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Track and manage your assigned tasks
          </p>
        </div>

        {/* Overdue Alert */}
        {overdueTasks.length > 0 && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
            <AlertCircle size={20} className="text-red-600 dark:text-red-400 flex-shrink-0" />
            <div>
              <p className="font-semibold text-red-900 dark:text-red-200">
                {overdueTasks.length} overdue {overdueTasks.length === 1 ? 'task' : 'tasks'}
              </p>
              <p className="text-sm text-red-700 dark:text-red-300">
                Please complete these tasks as soon as possible
              </p>
            </div>
          </div>
        )}

        {/* Search & Filter */}
        <div className="flex gap-4 mb-6 flex-wrap">
          <div className="flex-1 min-w-80">
            <div className="relative">
              <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10 w-full"
              />
            </div>
          </div>
          <button
            onClick={() => setFilterOverdue(!filterOverdue)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filterOverdue
                ? 'bg-red-500 text-white'
                : 'bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            Overdue Only
          </button>
        </div>

        {/* Tasks List */}
        <div className="space-y-4">
          {filteredTasks.length > 0 ? (
            filteredTasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onUpdate={(updates) => handleUpdateTask(task.id, updates)}
                onDelete={handleDeleteTask}
                onEdit={(t) => handleEditTask(t)}
                canEdit={true}
                canDelete={false}
                canMarkDone={true}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400">
                {searchTerm ? 'No tasks match your search' : filterOverdue ? 'No overdue tasks' : 'No tasks assigned yet'}
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Edit Task Modal */}
      <Modal
        isOpen={isModalOpen}
        title={editingTask ? 'Edit Task' : 'Task'}
        onClose={() => setIsModalOpen(false)}
        actions={[
          { label: 'Cancel', onClick: () => setIsModalOpen(false) },
          { label: 'Save', variant: 'primary', onClick: handleSaveTask }
        ]}
      >
        <div className="space-y-4">
          <div>
            <label className="label">Title *</label>
            <input className="input" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea className="input" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Priority</label>
              <select className="input" value={formData.priority} onChange={(e) => setFormData({ ...formData, priority: e.target.value })}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label className="label">Due Date</label>
              <input type="date" className="input" value={formData.dueDate} onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })} />
            </div>
          </div>
        </div>
      </Modal>

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
}
