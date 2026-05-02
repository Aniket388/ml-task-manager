import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, LogOut, Brain } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const statuses = ["Todo", "InProgress", "Done"];

export default function Dashboard() {
  const { token, user, logout } = useAuth();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [tasks, setTasks] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [newTask, setNewTask] = useState({ title: "", description: "", status: "Todo", priority: "Medium" });

  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const loadProjects = async () => {
    const { data } = await axios.get(`${API_BASE}/api/projects`, { headers });
    setProjects(data);
    if (data.length && !selectedProject) setSelectedProject(data[0].id);
  };

  const loadTasks = async (projectId) => {
    if (!projectId) return;
    const { data } = await axios.get(`${API_BASE}/api/tasks`, { headers, params: { project_id: projectId } });
    setTasks(data);
  };

  useEffect(() => { loadProjects(); }, []);
  useEffect(() => { loadTasks(selectedProject); }, [selectedProject]);

  const createProjectIfNone = async () => {
    if (projects.length) return;
    const { data } = await axios.post(`${API_BASE}/api/projects`, { name: "Default Project", description: "Starter workspace" }, { headers });
    setProjects([data]);
    setSelectedProject(data.id);
  };

  useEffect(() => { createProjectIfNone(); }, [projects.length]);

  const onDescriptionChange = async (description) => {
    setNewTask((p) => ({ ...p, description }));
    if (description.trim().length < 5) return;
    try {
      const { data } = await axios.post(`${API_BASE}/api/predict-priority`, { description }, { headers });
      setNewTask((p) => ({ ...p, priority: data.priority }));
    } catch (_) {}
  };

  const createTask = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/api/tasks`, { ...newTask, project_id: selectedProject }, { headers });
    await loadTasks(selectedProject);
    setShowModal(false);
    setNewTask({ title: "", description: "", status: "Todo", priority: "Medium" });
  };

  const moveTask = async (task, status) => {
    await axios.put(`${API_BASE}/api/tasks/${task.id}`, { status }, { headers });
    await loadTasks(selectedProject);
  };

  return (
    <div className="flex min-h-screen p-4 gap-4">
      <aside className="glass w-72 rounded-2xl p-4">
        <h2 className="font-bold text-xl">Projects</h2>
        <p className="text-sm text-slate-300 mt-1">{user?.name} ({user?.role})</p>
        <div className="mt-4 space-y-2">
          {projects.map((p) => (
            <button key={p.id} onClick={() => setSelectedProject(p.id)} className={`w-full text-left px-3 py-2 rounded-lg ${selectedProject === p.id ? "bg-brand-600" : "bg-slate-800/70"}`}>
              {p.name}
            </button>
          ))}
        </div>
        <button onClick={logout} className="mt-6 flex items-center gap-2 text-red-400"><LogOut size={16} /> Logout</button>
      </aside>

      <main className="flex-1 glass rounded-2xl p-4">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Kanban Board</h1>
          <button onClick={() => setShowModal(true)} className="bg-brand-600 px-4 py-2 rounded-lg flex items-center gap-2"><Plus size={16} />Create Task</button>
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          {statuses.map((status) => (
            <div key={status} className="bg-slate-900/50 rounded-xl p-3">
              <h3 className="font-semibold mb-3">{status === "InProgress" ? "In Progress" : status}</h3>
              <div className="space-y-2">
                {tasks.filter((t) => t.status === status).map((task) => (
                  <motion.div layout key={task.id} className="glass p-3 rounded-lg">
                    <h4 className="font-medium">{task.title}</h4>
                    <p className="text-sm text-slate-300">{task.description}</p>
                    <p className="text-xs mt-2">Priority: {task.priority}</p>
                    <select className="mt-2 bg-slate-800 rounded p-1 text-xs" value={task.status} onChange={(e) => moveTask(task, e.target.value)}>
                      <option value="Todo">Todo</option>
                      <option value="InProgress">In Progress</option>
                      <option value="Done">Done</option>
                    </select>
                  </motion.div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>

      <AnimatePresence>
        {showModal && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
            <motion.form onSubmit={createTask} initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 30, opacity: 0 }} className="glass rounded-2xl p-6 w-full max-w-lg space-y-3">
              <h2 className="text-xl font-bold">Create Task</h2>
              <input className="w-full p-3 rounded-lg bg-slate-900/60" placeholder="Title" value={newTask.title} onChange={(e) => setNewTask({ ...newTask, title: e.target.value })} required />
              <textarea className="w-full p-3 rounded-lg bg-slate-900/60 h-28" placeholder="Description" value={newTask.description} onChange={(e) => onDescriptionChange(e.target.value)} required />
              <div className="flex gap-3">
                <select className="flex-1 p-3 rounded-lg bg-slate-900/60" value={newTask.status} onChange={(e) => setNewTask({ ...newTask, status: e.target.value })}>
                  <option value="Todo">Todo</option>
                  <option value="InProgress">In Progress</option>
                  <option value="Done">Done</option>
                </select>
                <div className="flex-1">
                  <label className="text-xs text-slate-300 flex items-center gap-1 mb-1"><Brain size={12} /> ML Priority</label>
                  <select className="w-full p-3 rounded-lg bg-slate-900/60" value={newTask.priority} onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}>
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-lg bg-slate-700">Cancel</button>
                <button className="px-4 py-2 rounded-lg bg-brand-600">Create</button>
              </div>
            </motion.form>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
