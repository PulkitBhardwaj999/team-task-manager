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
      todo: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300',
      in_progress: 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200',
      done: 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200',
    };
    return colors[status] || '';
  };

  const isOverdue = task.is_overdue && task.status !== 'done';

  return (
    <div
      className={`card p-4 cursor-pointer transition-all ${
        isHovered ? 'shadow-md' : ''
      } ${
        isOverdue
          ? 'border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-900/10'
          : ''
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-4 flex-1">
          <img src="/images/avatar-placeholder.svg" alt="avatar" className="w-10 h-10 rounded-full flex-shrink-0" />
          <div className="flex-1">
          <h3 className="font-semibold text-gray-900 dark:text-white text-sm">
            {task.title}
          </h3>

          {task.description && (
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
              {task.description}
            </p>
          )}

          {/*  ASSIGNED USER (CORRECT PLACE) */}
          {task.assigned_user_name && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Assigned to: {task.assigned_user_name}
            </p>
          )}

          <div className="flex gap-2 mt-3 flex-wrap">
            <span className={`badge ${getPriorityColor(task.priority)} capitalize text-xs`}>
              {task.priority}
            </span>

            <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(task.status)}`}>
              {task.status.replace('_', ' ')}
            </span>

            {isOverdue && (
              <span className="badge badge-danger text-xs">Overdue</span>
            )}
          </div>

          {task.due_date && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Due: {new Date(task.due_date).toLocaleDateString()}
            </p>
          )}
          </div>
        </div>

        {isHovered && (
          <div className="flex gap-1">
            {canMarkDone && task.status !== 'done' && (
              <button
                onClick={() => onUpdate({ status: 'done' })}
                className="p-2 rounded hover:bg-green-100 dark:hover:bg-green-900 text-green-600 dark:text-green-400 transition-colors"
                title="Mark as done"
              >
                <Check size={18} />
              </button>
            )}

            {canEdit && (
              <button
                onClick={() => onEdit(task)}
                className="p-2 rounded hover:bg-blue-100 dark:hover:bg-blue-900 text-blue-600 dark:text-blue-400 transition-colors"
                title="Edit task"
              >
                <Edit2 size={18} />
              </button>
            )}

            {canDelete && (
              <button
                onClick={() => onDelete(task.id)}
                className="p-2 rounded hover:bg-red-100 dark:hover:bg-red-900 text-red-600 dark:text-red-400 transition-colors"
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