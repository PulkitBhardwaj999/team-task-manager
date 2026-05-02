import axiosInstance from './api';

// ── Auth ───────────────────────────────────────────────────────────────────────
export const authService = {
  signup: (email, fullName, password, role = 'member') => {
    // Normalise on the client side too — belt-and-suspenders.
    // The backend validator handles bad casing, but this prevents any
    // accidental capitalisation from ever reaching the wire.
    const safeRole = ['admin', 'member'].includes(String(role).toLowerCase())
      ? String(role).toLowerCase()
      : 'member';

    const payload = {
      email,
      full_name: fullName,   // ← snake_case — matches FastAPI UserCreate
      password,
      role: safeRole,        // ← always lowercase: "admin" or "member"
    };

    console.log('[authService.signup] payload →', payload);
    return axiosInstance.post('/auth/signup', payload);
  },

  login: (email, password) =>
    axiosInstance.post('/auth/login', { email, password }),

  getCurrentUser: () =>
    axiosInstance.get('/auth/me'),

  refreshToken: (refreshToken) =>
    axiosInstance.post('/auth/refresh', { refresh_token: refreshToken }),
};

// ── Users ──────────────────────────────────────────────────────────────────────
export const userService = {
  getAllUsers: () =>
    axiosInstance.get('/users/'),

  getUserById: (userId) =>
    axiosInstance.get(`/users/${userId}`),
};

// ── Projects ───────────────────────────────────────────────────────────────────
export const projectService = {
  createProject: (name, description) =>
    axiosInstance.post('/projects/', { name, description }),

  getMyProjects: (skip = 0, limit = 100) =>
    axiosInstance.get('/projects/', { params: { skip, limit } }),

  getProjectById: (projectId) =>
    axiosInstance.get(`/projects/${projectId}`),

  updateProject: (projectId, name, description) =>
    axiosInstance.put(`/projects/${projectId}`, { name, description }),

  deleteProject: (projectId) =>
    axiosInstance.delete(`/projects/${projectId}`),

  addProjectMember: (projectId, userId, role = 'member') =>
    axiosInstance.post(`/projects/${projectId}/members`, { user_id: userId, role }),

  removeProjectMember: (projectId, memberId) =>
    axiosInstance.delete(`/projects/${projectId}/members/${memberId}`),

  getProjectProgress: (projectId) =>
    axiosInstance.get(`/projects/${projectId}/progress`),
};

// ── Tasks ──────────────────────────────────────────────────────────────────────
export const taskService = {
  createTask: (projectId, title, description, priority, dueDate, assignedTo) => {
    const pid = Number(projectId);
    const payloadDueDate = dueDate ? new Date(dueDate).toISOString() : null;
    return axiosInstance.post('/tasks/', {
      project_id: pid,
      title,
      description,
      priority,
      due_date: payloadDueDate,
      assigned_to_id: assignedTo ? Number(assignedTo) : null,
    });
  },

  getTaskById: (taskId) =>
    axiosInstance.get(`/tasks/${taskId}`),

  getProjectTasks: (projectId, skip = 0, limit = 100, status = null, priority = null) =>
    axiosInstance.get(`/tasks/project/${projectId}`, {
      params: { skip, limit, status, priority },
    }),

  updateTask: (taskId, updates) => {
    const body = { ...updates };

    // Normalise due_date
    if (Object.prototype.hasOwnProperty.call(body, 'due_date')) {
      body.due_date = body.due_date
        ? new Date(body.due_date).toISOString()
        : null;
    }

    // Normalise assigned_to → assigned_to_id
    if (Object.prototype.hasOwnProperty.call(body, 'assigned_to')) {
      body.assigned_to_id = body.assigned_to ? Number(body.assigned_to) : null;
      delete body.assigned_to;
    }

    return axiosInstance.put(`/tasks/${taskId}`, body);
  },

  deleteTask: (taskId) =>
    axiosInstance.delete(`/tasks/${taskId}`),

  getMyTasks: (skip = 0, limit = 100) =>
    axiosInstance.get('/tasks/', { params: { skip, limit } }),

  searchTasks: (projectId, query, skip = 0, limit = 100) =>
    axiosInstance.get(`/tasks/search/${projectId}`, {
      params: { q: query, skip, limit },
    }),

  getOverdueTasks: () =>
    axiosInstance.get('/tasks/overdue'),
};

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashboardService = {
  getStats: () => axiosInstance.get('/dashboard/stats'),
};