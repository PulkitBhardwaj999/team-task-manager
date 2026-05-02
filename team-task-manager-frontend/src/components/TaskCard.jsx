import { useState } from 'react';
import { Check, Trash2, Edit2 } from 'lucide-react';

export function TaskCard({ task, onUpdate, onDelete, onEdit, canEdit = true, canDelete = false, canMarkDone = true }) {
  const [isHovered, setIsHovered] = useState(false);

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'badge-danger',
      medium: 'badge-warning',
      low: 'badge-success',
    };
    return colors[priority] || 'badge-primary';
  };

  const getStatusColor = (status) => {
    const colors = {
      todo: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300',
      in_progress: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-200',
      done: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-200',
    };
    return colors[status] || '';
  };

  const isOverdue = task.is_overdue && task.status !== 'done';

  return (
    <div
      className={`card p-5 cursor-default transition-all duration-300 ${
        isHovered ? 'shadow-lg scale-105' : ''
      } ${
        isOverdue
          ? 'border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-900/5'
          : ''
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Avatar + Content */}
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <img src="/images/avatar-placeholder.svg" alt="avatar" className="w-10 h-10 rounded-full flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm line-clamp-2">
              {task.title}
            </h3>

            {task.description && (
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                {task.description}
              </p>
            )}

            {task.assigned_user_name && (
              <p className="text-xs text-blue-600 dark:text-blue-300 mt-1 font-medium">
                👤 {task.assigned_user_name}
              </p>
            )}

            {/* Badges */}
            <div className="flex gap-2 mt-3 flex-wrap">
              <span className={`badge ${getPriorityColor(task.priority)} capitalize text-xs`}>
                {task.priority}
              </span>

              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(task.status)}`}>
                {task.status.replace('_', ' ')}
              </span>

              {isOverdue && (
                <span className="badge badge-danger text-xs">🚨 Overdue</span>
              )}
            </div>

            {task.due_date && (
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 font-medium">
                📅 Due: {new Date(task.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        {isHovered && (
          <div className="flex gap-1 flex-shrink-0">
            {canMarkDone && task.status !== 'done' && (
              <button
                onClick={() => onUpdate({ status: 'done' })}
                className="p-2.5 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 text-green-600 dark:text-green-400 transition-all hover:shadow-md"
                title="Mark as done"
              >
                <Check size={18} />
              </button>
            )}

            {canEdit && (
              <button
                onClick={() => onEdit(task)}
                className="p-2.5 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 text-blue-600 dark:text-blue-400 transition-all hover:shadow-md"
                title="Edit task"
              >
                <Edit2 size={18} />
              </button>
            )}

            {canDelete && (
              <button
                onClick={() => onDelete(task.id)}
                className="p-2.5 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 transition-all hover:shadow-md"
                title="Delete task"
              >
                <Trash2 size={18} />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}