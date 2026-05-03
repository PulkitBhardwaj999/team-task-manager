// import { useEffect, useState, useContext } from 'react';
// import { useNavigate } from 'react-router-dom';
// import { Header } from '../components/Header';
// import { Modal } from '../components/Modal';
// import { useToast, ToastContainer } from '../components/Toast';
// import { LoadingSkeleton, ProjectSkeleton } from '../components/Skeleton';
// import { projectService, userService } from '../services';
// import { AuthContext } from '../context/AuthContext';
// import { Plus, Edit2, Trash2, Users, FolderOpen } from 'lucide-react';

// export function ProjectsPage() {
//   const navigate = useNavigate();
//   const { toasts, removeToast, showToast } = useToast();
  
//   const [projects, setProjects] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [isModalOpen, setIsModalOpen] = useState(false);
//   const [editingProject, setEditingProject] = useState(null);
//   const [allUsers, setAllUsers] = useState([]);
//   const [memberModalProject, setMemberModalProject] = useState(null);
//   const [isMemberModalOpen, setIsMemberModalOpen] = useState(false);
  
//   const [formData, setFormData] = useState({
//     name: '',
//     description: ''
//   });
//   const [selectedMembers, setSelectedMembers] = useState([]);
//   const { user: currentUser } = useContext(AuthContext);

//   useEffect(() => {
//     fetchProjects();
//   }, []);

//   const fetchProjects = async () => {
//     try {
//       setLoading(true);
//       const response = await projectService.getMyProjects();
//       setProjects(response.data);
//     } catch (error) {
//       showToast('Failed to load projects', 'error');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleAddProject = () => {
//     setEditingProject(null);
//     setFormData({ name: '', description: '' });
//     setSelectedMembers([]);
//     // fetch users for potential initial members
//     fetchAllUsers();
//     setIsModalOpen(true);
//   };

//   const fetchAllUsers = async () => {
//     try {
//       const res = await userService.getAllUsers();
//       if (res && res.data) setAllUsers(res.data);
//     } catch (err) {
//       // ignore
//     }
//   };

//   const handleEditProject = (project) => {
//     setEditingProject(project);
//     setFormData({
//       name: project.name,
//       description: project.description
//     });
//     setIsModalOpen(true);
//   };

//   const handleSaveProject = async () => {
//     if (!formData.name.trim()) {
//       showToast('Project name is required', 'warning');
//       return;
//     }

//     try {
//       if (editingProject) {
//         await projectService.updateProject(
//           editingProject.id,
//           formData.name,
//           formData.description
//         );
//         showToast('Project updated successfully', 'success');
//       } else {
//         const createRes = await projectService.createProject(formData.name, formData.description);
//         // add selected members after creation
//         if (selectedMembers && selectedMembers.length > 0 && createRes?.data?.id) {
//           const projectId = createRes.data.id;
//           for (const uid of selectedMembers) {
//             try {
//               await projectService.addProjectMember(projectId, uid);
//             } catch (err) {
//               // continue on individual add failures
//             }
//           }
//         }
//         showToast('Project created successfully', 'success');
//       }
//       setIsModalOpen(false);
//       fetchProjects();
//     } catch (error) {
//       showToast('Failed to save project', 'error');
//     }
//   };

//   const handleDeleteProject = async (projectId) => {
//     if (window.confirm('Are you sure you want to delete this project?')) {
//       try {
//         await projectService.deleteProject(projectId);
//         showToast('Project deleted successfully', 'success');
//         fetchProjects();
//       } catch (error) {
//         showToast('Failed to delete project', 'error');
//       }
//     }
//   };

//   if (loading) {
//     return (
//       <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
//         <Header />
//         <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
//           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
//             {[1, 2, 3].map(i => <ProjectSkeleton key={i} />)}
//           </div>
//         </main>
//       </div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
//       <Header />

//       <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
//         {/* Header */}
//         {/* <div className="flex items-center justify-between mb-8">
//           <div>
//             <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
//               Projects
//             </h1>
//             <p className="text-gray-600 dark:text-gray-400 mt-1">
//               Manage your projects and team collaboration
//             </p>
//           </div>
//           <button onClick={handleAddProject} className="btn-primary flex items-center gap-2">
//             <Plus size={20} />
//             New Project
//           </button>
//         </div> */}

//         {/* Projects Grid */}
//             {/* Header + Hero */}
//             <div className="mb-8">
//               <div className="flex items-center justify-between mb-6">
//                 <div>
//                   <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1>
//                   <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your projects and team collaboration</p>
//                 </div>
//                 <div className="flex items-center gap-3">
//                   <button onClick={handleAddProject} className="btn-primary flex items-center gap-2">
//                     <Plus size={20} /> New Project
//                   </button>
//                   <button onClick={() => { setMemberModalProject(null); fetchAllUsers(); setIsMemberModalOpen(true); }} className="btn-secondary">Manage Members</button>
//                 </div>
//               </div>

//               <div className="rounded-lg overflow-hidden mb-8">
//                 <img src="/images/hero.svg" alt="hero" className="w-full h-40 object-cover block" />
//               </div>
//             </div>
//         {projects.length > 0 ? (
//           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
//             {projects.map(project => (
//               <div key={project.id} className="card p-6 hover:shadow-lg transition-shadow">
//                 <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
//                   {project.name}
//                 </h3>
//                 {project.description && (
//                   <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
//                     {project.description}
//                   </p>
//                 )}
                
//                 <div className="flex items-center gap-2 mb-4 text-sm text-gray-600 dark:text-gray-400">
//                   <Users size={16} />
//                   <span>{project.members?.length || 0} members</span>
//                 </div>

//                 <div className="flex gap-2">
//                   <button
//                     onClick={() => navigate(`/projects/${project.id}/tasks`) }
//                     className="flex-1 px-4 py-2 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-200 rounded-lg hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors text-sm font-medium flex items-center justify-center gap-2"
//                   >
//                     <FolderOpen size={16} />
//                     View Tasks
//                   </button>
//                   <button
//                     onClick={() => { setMemberModalProject(project); fetchAllUsers(); setIsMemberModalOpen(true); }}
//                     title="Manage members"
//                     className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
//                   >
//                     <Users size={18} />
//                   </button>
//                   <button
//                     onClick={() => handleEditProject(project)}
//                     className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
//                   >
//                     <Edit2 size={18} />
//                   </button>
//                   <button
//                     onClick={() => handleDeleteProject(project.id)}
//                     className="p-2 rounded-lg text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900 transition-colors"
//                   >
//                     <Trash2 size={18} />
//                   </button>
//                 </div>
//               </div>
//             ))}
//           </div>
//         ) : (
//           <div className="text-center py-12">
//             <FolderOpen size={48} className="mx-auto text-gray-400 mb-4" />
//             <p className="text-gray-600 dark:text-gray-400 mb-4">
//               No projects yet. Create one to get started!
//             </p>
//             <button onClick={handleAddProject} className="btn-primary">
//               <Plus size={20} className="inline mr-2" />
//               Create First Project
//             </button>
//           </div>
//         )}
//       </main>

//       {/* Project Modal */}
//       <Modal
//         isOpen={isModalOpen}
//         title={editingProject ? 'Edit Project' : 'New Project'}
//         onClose={() => setIsModalOpen(false)}
//         actions={[
//           { label: 'Cancel', onClick: () => setIsModalOpen(false) },
//           { label: editingProject ? 'Update' : 'Create', variant: 'primary', onClick: handleSaveProject }
//         ]}
//       >
//         <div className="space-y-4">
//           <div>
//             <label htmlFor="name" className="label">Project Name *</label>
//             <input
//               id="name"
//               type="text"
//               value={formData.name}
//               onChange={(e) => setFormData({ ...formData, name: e.target.value })}
//               placeholder="My Awesome Project"
//               className="input"
//             />
//           </div>
//           <div>
//             <label htmlFor="description" className="label">Description</label>
//             <textarea
//               id="description"
//               value={formData.description}
//               onChange={(e) => setFormData({ ...formData, description: e.target.value })}
//               placeholder="Project description..."
//               className="input min-h-24"
//             />
//           </div>
//           {/* Initial members selection when creating project */}
//           {!editingProject && (
//             <div>
//               <label className="label">Add initial members</label>
//               <select
//                 multiple
//                 value={selectedMembers.map(String)}
//                 onChange={(e) => setSelectedMembers(Array.from(e.target.selectedOptions).map(o => Number(o.value)))}
//                 className="input h-32"
//               >
//                 {allUsers.map(u => (
//                   <option key={u.id} value={u.id}>{u.full_name} ({u.email})</option>
//                 ))}
//               </select>
//               <p className="text-xs text-gray-500 mt-1">Select one or more users to add as project members.</p>
//             </div>
//           )}
//         </div>
//       </Modal>

//       {/* Manage Members Modal (Projects page) */}
//       <Modal
//         isOpen={isMemberModalOpen}
//         title={memberModalProject ? `Manage Members - ${memberModalProject.name}` : 'Manage Members'}
//         onClose={() => { setIsMemberModalOpen(false); setMemberModalProject(null); }}
//         actions={[{ label: 'Close', onClick: () => { setIsMemberModalOpen(false); setMemberModalProject(null); } }]}
//       >
//         <div className="space-y-4">
//           <div>
//             <h4 className="font-medium">Current Members ({memberModalProject?.members?.length || 0})</h4>
//             <ul className="mt-2 space-y-2">
//               {memberModalProject?.members?.map(m => (
//                 <li key={m.id} className="flex items-center justify-between">
//                   <div>{m.full_name} <span className="text-xs text-gray-500 ml-2">({m.email})</span></div>
//                   {(memberModalProject?.creator_id === currentUser?.id) ? (
//                     <button onClick={async () => { await projectService.removeProjectMember(memberModalProject.id, m.id); showToast('Member removed','success'); fetchProjects(); setMemberModalProject(await projectService.getProjectById(memberModalProject.id).then(r=>r.data)); }} className="text-red-600">Remove</button>
//                   ) : null}
//                 </li>
//               ))}
//             </ul>
//           </div>

//           <div>
//             <h4 className="font-medium">Add Member</h4>
//             <div className="mt-2 flex gap-2">
//               <select id="projectsAddMemberSelect" className="input w-full">
//                 <option value="">Select user</option>
//                 {allUsers.filter(u => !(memberModalProject?.members || []).some(m => m.id === u.id)).map(u => (
//                   <option key={u.id} value={u.id}>{u.full_name} ({u.email})</option>
//                 ))}
//               </select>
//               <button className="btn-primary" onClick={async () => {
//                 const sel = document.getElementById('projectsAddMemberSelect');
//                 const userId = sel?.value ? Number(sel.value) : null;
//                 if (!userId) { showToast('Select a user', 'warning'); return; }
//                 try {
//                   await projectService.addProjectMember(memberModalProject.id, userId);
//                   showToast('Member added', 'success');
//                   const updated = await projectService.getProjectById(memberModalProject.id);
//                   setMemberModalProject(updated.data);
//                   fetchProjects();
//                 } catch (err) {
//                   showToast(err?.response?.data?.detail || 'Failed to add member', 'error');
//                 }
//               }}>Add</button>
//             </div>
//           </div>
//         </div>
//       </Modal>

//       <ToastContainer toasts={toasts} removeToast={removeToast} />
//     </div>
//   );
// }

import { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { Modal } from '../components/Modal';
import { useToast, ToastContainer } from '../components/Toast';
import { LoadingSkeleton, ProjectSkeleton } from '../components/Skeleton';
import { projectService, userService } from '../services';
import { AuthContext } from '../context/AuthContext';
import { Plus, Edit2, Trash2, Users, FolderOpen } from 'lucide-react';

export function ProjectsPage() {
  const navigate = useNavigate();
  const { toasts, removeToast, showToast } = useToast();

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  // ── Project create / edit modal ───────────────────────────────────────────
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [selectedMembers, setSelectedMembers] = useState([]);

  // ── Members modal ─────────────────────────────────────────────────────────
  // memberModalProject must ALWAYS be a real project object (never null)
  // when the modal is open. We enforce this below.
  const [isMemberModalOpen, setIsMemberModalOpen] = useState(false);
  const [memberModalProject, setMemberModalProject] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  const [addMemberUserId, setAddMemberUserId] = useState('');

  const { user: currentUser } = useContext(AuthContext);

  // ── Data fetching ─────────────────────────────────────────────────────────
  useEffect(() => { fetchProjects(); }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await projectService.getMyProjects();
      setProjects(response.data);
    } catch {
      showToast('Failed to load projects', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllUsers = async () => {
    try {
      const res = await userService.getAllUsers();
      if (res?.data) setAllUsers(res.data);
    } catch { /* ignore */ }
  };

  // ── Project CRUD ──────────────────────────────────────────────────────────
  const handleAddProject = () => {
    setEditingProject(null);
    setFormData({ name: '', description: '' });
    setSelectedMembers([]);
    fetchAllUsers();
    setIsModalOpen(true);
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setFormData({ name: project.name, description: project.description || '' });
    setIsModalOpen(true);
  };

  const handleSaveProject = async () => {
    if (!formData.name.trim()) {
      showToast('Project name is required', 'warning');
      return;
    }
    try {
      if (editingProject) {
        await projectService.updateProject(editingProject.id, formData.name, formData.description);
        showToast('Project updated successfully', 'success');
      } else {
        const createRes = await projectService.createProject(formData.name, formData.description);
        if (selectedMembers.length > 0 && createRes?.data?.id) {
          for (const uid of selectedMembers) {
            try { await projectService.addProjectMember(createRes.data.id, uid); } catch { /* continue */ }
          }
        }
        showToast('Project created successfully', 'success');
      }
      setIsModalOpen(false);
      fetchProjects();
    } catch {
      showToast('Failed to save project', 'error');
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!window.confirm('Are you sure you want to delete this project?')) return;
    try {
      await projectService.deleteProject(projectId);
      showToast('Project deleted successfully', 'success');
      fetchProjects();
    } catch {
      showToast('Failed to delete project', 'error');
    }
  };

  // ── Members modal helpers ─────────────────────────────────────────────────

  /**
   * Open the members modal for a specific project.
   * ALWAYS requires a real project object.
   */
  const openMembersModal = async (project) => {
    if (!project) {
      showToast('Please select a project first', 'warning');
      return;
    }
    await fetchAllUsers();
    // Refresh the project so member list is current
    try {
      const fresh = await projectService.getProjectById(project.id);
      setMemberModalProject(fresh.data);
    } catch {
      setMemberModalProject(project);
    }
    setAddMemberUserId('');
    setIsMemberModalOpen(true);
  };

  const closeMembersModal = () => {
    setIsMemberModalOpen(false);
    setMemberModalProject(null);
    setAddMemberUserId('');
  };

  const handleAddMember = async () => {
    if (!memberModalProject) return;
    const userId = addMemberUserId ? Number(addMemberUserId) : null;
    if (!userId) {
      showToast('Please select a user to add', 'warning');
      return;
    }
    try {
      await projectService.addProjectMember(memberModalProject.id, userId);
      showToast('Member added successfully', 'success');
      // Refresh member list inside modal
      const fresh = await projectService.getProjectById(memberModalProject.id);
      setMemberModalProject(fresh.data);
      setAddMemberUserId('');
      fetchProjects(); // keep project cards in sync
    } catch (err) {
      showToast(err?.response?.data?.detail || 'Failed to add member', 'error');
    }
  };

  const handleRemoveMember = async (memberId) => {
    if (!memberModalProject) return;
    if (!window.confirm('Remove this member from the project?')) return;
    try {
      await projectService.removeProjectMember(memberModalProject.id, memberId);
      showToast('Member removed', 'success');
      const fresh = await projectService.getProjectById(memberModalProject.id);
      setMemberModalProject(fresh.data);
      fetchProjects();
    } catch (err) {
      showToast(err?.response?.data?.detail || 'Failed to remove member', 'error');
    }
  };

  // ── Derived values for the members modal ──────────────────────────────────
  const currentMembers = memberModalProject?.members || [];
  const currentMemberIds = new Set(currentMembers.map((m) => m.id));
  const addableUsers = allUsers.filter((u) => !currentMemberIds.has(u.id));
  const isProjectOwner = memberModalProject?.creator_id === currentUser?.id;

  // ─────────────────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => <ProjectSkeleton key={i} />)}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Page header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Manage your projects and team collaboration
              </p>
            </div>
            {/* Only "New Project" in the header — Manage Members requires a project */}
            <button onClick={handleAddProject} className="btn-primary flex items-center gap-2">
              <Plus size={20} /> New Project
            </button>
          </div>

          <div className="rounded-lg overflow-hidden mb-8">
            <img src="/images/hero.svg" alt="hero" className="w-full h-40 object-cover block" />
          </div>
        </div>

        {/* Projects grid */}
        {projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div key={project.id} className="card p-6 hover:shadow-lg transition-shadow">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {project.name}
                </h3>
                {project.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                    {project.description}
                  </p>
                )}
                <div className="flex items-center gap-2 mb-4 text-sm text-gray-600 dark:text-gray-400">
                  <Users size={16} />
                  <span>{project.members?.length || 0} members</span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => navigate(`/projects/${project.id}/tasks`)}
                    className="flex-1 px-4 py-2 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-200 rounded-lg hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <FolderOpen size={16} /> View Tasks
                  </button>

                  {/* ✅ Members button — always passes the project object */}
                  <button
                    onClick={() => openMembersModal(project)}
                    title="Manage members"
                    className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                  >
                    <Users size={18} />
                  </button>

                  <button
                    onClick={() => handleEditProject(project)}
                    className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                  >
                    <Edit2 size={18} />
                  </button>

                  <button
                    onClick={() => handleDeleteProject(project.id)}
                    className="p-2 rounded-lg text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900 transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FolderOpen size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No projects yet. Create one to get started!
            </p>
            <button onClick={handleAddProject} className="btn-primary">
              <Plus size={20} className="inline mr-2" />
              Create First Project
            </button>
          </div>
        )}
      </main>

      {/* ── Project create / edit modal ────────────────────────────────────── */}
      <Modal
        isOpen={isModalOpen}
        title={editingProject ? 'Edit Project' : 'New Project'}
        onClose={() => setIsModalOpen(false)}
        actions={[
          { label: 'Cancel', onClick: () => setIsModalOpen(false) },
          { label: editingProject ? 'Update' : 'Create', variant: 'primary', onClick: handleSaveProject },
        ]}
      >
        <div className="space-y-4">
          <div>
            <label className="label">Project Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="My Awesome Project"
              className="input"
            />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Project description..."
              className="input min-h-24"
            />
          </div>
          {/* Initial member selection — only when creating */}
          {!editingProject && allUsers.length > 0 && (
            <div>
              <label className="label">Add initial members</label>
              <select
                multiple
                value={selectedMembers.map(String)}
                onChange={(e) =>
                  setSelectedMembers(Array.from(e.target.selectedOptions).map((o) => Number(o.value)))
                }
                className="input h-32"
              >
                {allUsers.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.full_name} ({u.email})
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">Hold Ctrl / Cmd to select multiple users.</p>
            </div>
          )}
        </div>
      </Modal>

      {/* ── Manage Members modal ───────────────────────────────────────────── */}
      <Modal
        isOpen={isMemberModalOpen}
        title={memberModalProject ? `Members — ${memberModalProject.name}` : 'Manage Members'}
        onClose={closeMembersModal}
        actions={[{ label: 'Close', onClick: closeMembersModal }]}
      >
        <div className="space-y-6">

          {/* Current members list */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
              Current Members ({currentMembers.length})
            </h4>

            {currentMembers.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">No members yet.</p>
            ) : (
              <ul className="space-y-2">
                {currentMembers.map((m) => (
                  <li
                    key={m.id}
                    className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-50 dark:bg-gray-800"
                  >
                    <div>
                      <span className="font-medium text-sm text-gray-900 dark:text-white">
                        {m.full_name}
                      </span>
                      <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                        ({m.email})
                      </span>
                      {memberModalProject?.creator_id === m.id && (
                        <span className="ml-2 text-xs font-semibold text-blue-600 dark:text-blue-400">
                          Owner
                        </span>
                      )}
                    </div>
                    {/* Only the project owner can remove members */}
                    {isProjectOwner && memberModalProject?.creator_id !== m.id && (
                      <button
                        onClick={() => handleRemoveMember(m.id)}
                        className="text-xs text-red-600 dark:text-red-400 hover:underline"
                      >
                        Remove
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Add member — only for project owners */}
          {isProjectOwner && (
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Add Member</h4>
              {addableUsers.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  All registered users are already members.
                </p>
              ) : (
                <div className="flex gap-2">
                  <select
                    value={addMemberUserId}
                    onChange={(e) => setAddMemberUserId(e.target.value)}
                    className="input flex-1"
                  >
                    <option value="">Select a user…</option>
                    {addableUsers.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.full_name} ({u.email})
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={handleAddMember}
                    disabled={!addMemberUserId}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Add
                  </button>
                </div>
              )}
            </div>
          )}

          {!isProjectOwner && (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Only the project owner can add or remove members.
            </p>
          )}
        </div>
      </Modal>

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
}