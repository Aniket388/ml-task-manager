import { useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "Member" });
  const [error, setError] = useState("");
  const { login } = useAuth();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const url = isLogin ? `${API_BASE}/api/auth/login` : `${API_BASE}/api/auth/register`;
      const payload = isLogin ? { email: form.email, password: form.password } : form;
      const { data } = await axios.post(url, payload);
      login(data.access_token, data.user);
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <motion.form onSubmit={submit} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass rounded-2xl p-8 w-full max-w-md space-y-4">
        <h1 className="text-2xl font-bold">ML Task Manager</h1>
        <p className="text-slate-300">{isLogin ? "Welcome back" : "Create your account"}</p>

        {!isLogin && <input className="w-full p-3 rounded-lg bg-slate-900/60" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />}
        <input className="w-full p-3 rounded-lg bg-slate-900/60" placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <input className="w-full p-3 rounded-lg bg-slate-900/60" placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        {!isLogin && (
          <select className="w-full p-3 rounded-lg bg-slate-900/60" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option>Member</option>
            <option>Admin</option>
          </select>
        )}

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <motion.button whileTap={{ scale: 0.97 }} className="w-full bg-brand-600 hover:bg-brand-500 rounded-lg py-3 font-semibold">
          {isLogin ? "Login" : "Register"}
        </motion.button>

        <button type="button" className="text-sm text-slate-300" onClick={() => setIsLogin((v) => !v)}>
          {isLogin ? "Need an account? Register" : "Already have an account? Login"}
        </button>
      </motion.form>
    </div>
  );
}
