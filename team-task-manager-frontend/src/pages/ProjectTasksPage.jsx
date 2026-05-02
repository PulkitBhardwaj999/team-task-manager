import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Header } from '../components/Header';
import { TaskCard } from '../components/TaskCard';
import { Modal } from '../components/Modal';
import { useToast, ToastContainer } from '../components/Toast';
import { LoadingSkeleton, TaskSkeleton } from '../components/Skeleton';
import { taskService, projectService, userService } from '../services';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { ArrowLeft, Plus, Search, Filter } from 'lucide-react';

export function ProjectTasksPage() {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const { toasts, removeToast, showToast } = useToast();
  
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({ status: '', priority: '' });
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
    assignedTo: null
  });
  const [allUsers, setAllUsers] = useState([]);
  const [isMemberModalOpen, setIsMemberModalOpen] = useState(false);
  const { user: currentUser } = useContext(AuthContext);

  useEffect(() => {
    fetchProjectAndTasks();
  }, [projectId]);

  const fetchProjectAndTasks = async () => {
    try {
      setLoading(true);
      const [projectRes, tasksRes] = await Promise.all([
        projectService.getProjectById(projectId),
        taskService.getProjectTasks(projectId, 0, 100, filters.status || null, filters.priority || null)
      ]);
      const proj = projectRes.data;
      // enrich tasks with assignee name when available
      const members = proj.members || [];
      const tasksWithAssignee = tasksRes.data.map(t => ({
        ...t,
        assigned_user_name: members.find(m => m.id === t.assigned_to)?.full_name || null
      }));
      setProject(proj);
      // annotate tasks with permission flags used by TaskCard
      const isMember = (proj.members || []).some(m => m.id === currentUser?.id);
      const isProjectAdmin = proj.creator_id === currentUser?.id || (proj.members || []).some(m => m.id === currentUser?.id && m.role === 'admin');
      const tasksWithPerms = tasksWithAssignee.map(t => ({
        ...t,
        __canEdit: isMember || proj.creator_id === currentUser?.id || t.assigned_to === currentUser?.id,
        __canDelete: proj.creator_id === currentUser?.id,
        __canMarkDone: isMember || t.assigned_to === currentUser?.id,
      }));
      setTasks(tasksWithPerms);
    } catch (error) {
      showToast('Failed to load project tasks', 'error');
      navigate('/projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllUsers = async () => {
    try {
      const res = await userService.getAllUsers();
      setAllUsers(res.data || []);
    } catch (err) {
      // ignore silently; users may not be needed
    }
  };

  const handleAddTask = () => {
    setEditingTask(null);
    setFormData({
      title: '',
      description: '',
      priority: 'medium',
      dueDate: '',
      assignedTo: currentUser ? currentUser.id : null
    });
    setIsModalOpen(true);
  };

  const openMemberModal = async () => {
    await fetchAllUsers();
    setIsMemberModalOpen(true);
  };

  const handleAddMember = async (userId) => {
    try {
      await projectService.addProjectMember(projectId, userId);
      showToast('Member added', 'success');
      // refresh project and tasks
      fetchProjectAndTasks();
      setIsMemberModalOpen(false);
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to add member';
      showToast(msg, 'error');
    }
  };

  const handleRemoveMember = async (userId) => {
    if (!window.confirm('Remove this member from the project?')) return;
    try {
      await projectService.removeProjectMember(projectId, userId);
      showToast('Member removed', 'success');
      fetchProjectAndTasks();
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to remove member';
      showToast(msg, 'error');
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
    if (!formData.title.trim()) {
      showToast('Task title is required', 'warning');
      return;
    }

    try {
      if (editingTask) {
        await taskService.updateTask(editingTask.id, {
          title: formData.title,
          description: formData.description,
          priority: formData.priority,
          due_date: formData.dueDate || null,
          assigned_to: formData.assignedTo
        });
        showToast('Task updated successfully', 'success');
      } else {
        await taskService.createTask(
          projectId,
          formData.title,
          formData.description,
          formData.priority,
          formData.dueDate || null,
          formData.assignedTo
        );
        showToast('Task created successfully', 'success');
      }
      setIsModalOpen(false);
      fetchProjectAndTasks();
    } catch (error) {
      // Prefer backend validation messages when available
      const resp = error?.response?.data;
      if (resp) {
        // FastAPI validation errors usually in `detail` (array) or `detail` string
        const detail = resp.detail || resp.errors || resp.message || resp;
        try {
          const msg = typeof detail === 'string' ? detail : JSON.stringify(detail);
          showToast(msg, 'error');
        } catch {
          showToast('Failed to save task', 'error');
        }
      } else {
        showToast('Failed to save task', 'error');
      }
    }
  };

  const handleAssignToMe = async () => {
    if (!currentUser) {
      showToast('You must be logged in to assign a task', 'warning');
      return;
    }

    try {
      if (editingTask) {
        // Update existing task to assign to current user
        await taskService.updateTask(editingTask.id, { assigned_to: currentUser.id });
        showToast('Task assigned to you', 'success');
        setIsModalOpen(false);
        fetchProjectAndTasks();
      } else {
        // For new task, set the form assignedTo to current user so Create will include it
        setFormData({ ...formData, assignedTo: currentUser.id });
        showToast('Assigned to you (will be saved on create)', 'info');
      }
    } catch (error) {
      showToast('Failed to assign task', 'error');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await taskService.deleteTask(taskId);
        showToast('Task deleted successfully', 'success');
        fetchProjectAndTasks();
      } catch (error) {
        showToast('Failed to delete task', 'error');
      }
    }
  };

  const handleUpdateTaskStatus = async (taskId, newStatus) => {
    try {
      await taskService.updateTask(taskId, { status: newStatus });
      showToast('Task updated', 'success');
      fetchProjectAndTasks();
    } catch (error) {
      showToast('Failed to update task', 'error');
    }
  };

  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate('/projects')}
            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {project?.name}
            </h1>
            {project?.description && (
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                {project.description}
              </p>
            )}
          </div>
        </div>

        {/* Controls */}
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
          <button onClick={handleAddTask} className="btn-primary flex items-center gap-2">
            <Plus size={20} />
            Add Task
          </button>
          <button onClick={openMemberModal} className="btn-secondary flex items-center gap-2">
            Manage Members
          </button>
        </div>

        {/* Tasks Grid */}
        <div className="space-y-4">
          {filteredTasks.length > 0 ? (
            filteredTasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onUpdate={(updates) => handleUpdateTaskStatus(task.id, updates.status)}
                onDelete={handleDeleteTask}
                onEdit={handleEditTask}
                canEdit={task.__canEdit}
                canDelete={task.__canDelete}
                canMarkDone={task.__canMarkDone}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400">
                {searchTerm ? 'No tasks match your search' : 'No tasks yet. Create one to get started!'}
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Task Modal */}
      <Modal
        isOpen={isModalOpen}
        title={editingTask ? 'Edit Task' : 'New Task'}
        onClose={() => setIsModalOpen(false)}
        actions={(() => {
          const base = [
            { label: 'Cancel', onClick: () => setIsModalOpen(false) }
          ];
          // Show 'Assign to me' when user is a project member (or admin)
          const isMember = project?.members?.some(m => m.id === currentUser?.id);
          const showAssignAction = Boolean(currentUser && isMember && ((editingTask && editingTask.assigned_to !== currentUser.id) || (!editingTask && formData.assignedTo !== currentUser.id)));
          if (showAssignAction) {
            base.push({ label: 'Assign to me', onClick: handleAssignToMe });
          }
          base.push({ label: editingTask ? 'Update' : 'Create', variant: 'primary', onClick: handleSaveTask });
          return base;
        })()}
      >
        <div className="space-y-4">
          <div>
            <label htmlFor="title" className="label">Title *</label>
            <input
              id="title"
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Task title"
              className="input"
            />
          </div>
          <div>
            <label htmlFor="description" className="label">Description</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Task description"
              className="input min-h-24"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="priority" className="label">Priority</label>
              <select
                id="priority"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="input"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label htmlFor="dueDate" className="label">Due Date</label>
              <input
                id="dueDate"
                type="date"
                value={formData.dueDate}
                onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
                className="input"
              />
            </div>
          </div>
          {/* Assignment dropdown: visible to all but editable only by admins */}
          {project?.members && project.members.length > 0 && (
            <div>
              <label htmlFor="assignedTo" className="label">Assign To</label>
              <select
                id="assignedTo"
                value={formData.assignedTo ?? (currentUser ? currentUser.id : '')}
                onChange={(e) => setFormData({ ...formData, assignedTo: e.target.value ? Number(e.target.value) : null })}
                className="input"
                disabled={!((project?.creator_id === currentUser?.id) || (project?.members || []).some(m => m.id === currentUser?.id && m.role === 'admin'))}
              >
                <option value="">Unassigned</option>
                {project.members.map(user => (
                  <option key={user.id} value={user.id}>{user.full_name}</option>
                ))}
              </select>
              {!(project?.creator_id === currentUser?.id || (project?.members || []).some(m => m.id === currentUser?.id && m.role === 'admin')) && (
                <p className="text-xs text-gray-500 mt-1">Only project admins can assign tasks to other members</p>
              )}
            </div>
          )}
        </div>
      </Modal>

      {/* Manage Members Modal */}
      <Modal
        isOpen={isMemberModalOpen}
        title="Manage Members"
        onClose={() => setIsMemberModalOpen(false)}
        actions={[
          { label: 'Close', onClick: () => setIsMemberModalOpen(false) }
        ]}
      >
        <div className="space-y-4">
          <div>
            <h4 className="font-medium">Current Members ({project?.members?.length || 0})</h4>
            <ul className="mt-2 space-y-2">
              {project?.members?.map(m => (
                <li key={m.id} className="flex items-center justify-between">
                  <div>{m.full_name} <span className="text-xs text-gray-500 ml-2">({m.email})</span></div>
                  {currentUser?.id === project?.creator_id || currentUser?.role === 'admin' ? (
                    <button onClick={() => handleRemoveMember(m.id)} className="text-red-600">Remove</button>
                  ) : null}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-medium">Add Member</h4>
            <div className="mt-2 flex gap-2">
              <select id="addMemberSelect" className="input w-full">
                <option value="">Select user</option>
                {allUsers.filter(u => !(project?.members || []).some(m => m.id === u.id)).map(u => (
                  <option key={u.id} value={u.id}>{u.full_name} ({u.email})</option>
                ))}
              </select>
              <button className="btn-primary" onClick={() => {
                const sel = document.getElementById('addMemberSelect');
                const userId = sel?.value ? Number(sel.value) : null;
                if (!userId) { showToast('Select a user', 'warning'); return; }
                handleAddMember(userId);
              }}>Add</button>
            </div>
          </div>
        </div>
      </Modal>

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
}
