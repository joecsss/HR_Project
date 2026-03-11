"use client";

import { useEffect, useState } from "react";
import { jobsAPI } from "@/lib/api";
import { Plus, Sparkles, Pencil, Trash2, Search, Loader2, X } from "lucide-react";
import toast from "react-hot-toast";

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showGenerate, setShowGenerate] = useState(false);
  const [search, setSearch] = useState("");
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    title: "", department: "", location: "", employment_type: "full-time",
    seniority_level: "mid", description: "", requirements: "", benefits: "", salary_range: "",
  });

  const [genForm, setGenForm] = useState({
    title: "", department: "", seniority_level: "", key_skills: "", additional_notes: "",
  });

  const fetchJobs = async () => {
    try {
      const res = await jobsAPI.list({ limit: 100 });
      setJobs(res.data.jobs);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchJobs(); }, []);

  const handleCreate = async () => {
    if (!form.title || !form.description) {
      toast.error("กรุณากรอกชื่อตำแหน่งและรายละเอียดงาน");
      return;
    }
    setSaving(true);
    try {
      await jobsAPI.create(form);
      toast.success("สร้างตำแหน่งงานสำเร็จ!");
      setShowCreate(false);
      setForm({ title: "", department: "", location: "", employment_type: "full-time", seniority_level: "mid", description: "", requirements: "", benefits: "", salary_range: "" });
      fetchJobs();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "เกิดข้อผิดพลาด");
    } finally { setSaving(false); }
  };

  const handleGenerate = async () => {
    if (!genForm.title) { toast.error("กรุณากรอกชื่อตำแหน่ง"); return; }
    setGenerating(true);
    try {
      const res = await jobsAPI.generateJD(genForm);
      setForm((prev) => ({
        ...prev,
        title: genForm.title,
        department: genForm.department || prev.department,
        seniority_level: genForm.seniority_level || prev.seniority_level,
        description: res.data.description,
        requirements: res.data.requirements,
        benefits: res.data.benefits,
      }));
      toast.success("สร้าง JD ด้วย AI สำเร็จ!");
      setShowGenerate(false);
      setShowCreate(true);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "AI ไม่สามารถสร้าง JD ได้");
    } finally { setGenerating(false); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("คุณแน่ใจหรือไม่ที่จะลบตำแหน่งงานนี้?")) return;
    try {
      await jobsAPI.delete(id);
      toast.success("ลบตำแหน่งงานแล้ว");
      fetchJobs();
    } catch { toast.error("เกิดข้อผิดพลาด"); }
  };

  const handleStatusChange = async (id: number, newStatus: string) => {
    try {
      await jobsAPI.update(id, { status: newStatus });
      toast.success("อัปเดตสถานะแล้ว");
      fetchJobs();
    } catch { toast.error("เกิดข้อผิดพลาด"); }
  };

  const filteredJobs = jobs.filter((j) =>
    j.title.toLowerCase().includes(search.toLowerCase()) ||
    (j.department || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Job Management</h1>
          <p className="text-gray-500 text-sm mt-1">จัดการตำแหน่งงานและสร้าง JD ด้วย AI</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowGenerate(true)}
            className="px-4 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-medium hover:shadow-lg transition-all flex items-center gap-2 text-sm"
          >
            <Sparkles className="w-4 h-4" /> AI สร้าง JD
          </button>
          <button
            onClick={() => setShowCreate(true)}
            className="px-4 py-2.5 bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded-xl font-medium hover:shadow-lg transition-all flex items-center gap-2 text-sm"
          >
            <Plus className="w-4 h-4" /> สร้างตำแหน่งงาน
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="ค้นหาตำแหน่งงาน..."
          className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-teal-400 focus:border-transparent outline-none text-sm text-gray-700"
        />
      </div>

      {/* Job List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-white rounded-2xl animate-pulse border border-gray-100" />
          ))}
        </div>
      ) : filteredJobs.length > 0 ? (
        <div className="space-y-4">
          {filteredJobs.map((job) => (
            <div key={job.id} className="bg-white rounded-2xl p-5 border border-gray-100 card-hover">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-bold text-gray-800">{job.title}</h3>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      job.status === "active" ? "bg-emerald-100 text-emerald-700" :
                      job.status === "closed" ? "bg-red-100 text-red-600" :
                      "bg-gray-100 text-gray-600"
                    }`}>{job.status}</span>
                  </div>
                  <p className="text-sm text-gray-500 mb-2">
                    {job.department || "—"} • {job.location || "Remote"} • {job.employment_type || "full-time"} • {job.seniority_level || "—"}
                  </p>
                  <p className="text-sm text-gray-400 line-clamp-2">{job.description?.substring(0, 200)}...</p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <select
                    value={job.status}
                    onChange={(e) => handleStatusChange(job.id, e.target.value)}
                    className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 text-gray-600 focus:outline-none"
                  >
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="closed">Closed</option>
                  </select>
                  <button onClick={() => handleDelete(job.id)} className="p-2 text-gray-400 hover:text-red-500 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 text-gray-400">
          <p className="text-lg">ยังไม่มีตำแหน่งงาน</p>
          <p className="text-sm mt-1">กดปุ่ม &quot;สร้างตำแหน่งงาน&quot; หรือ &quot;AI สร้าง JD&quot; เพื่อเริ่มต้น</p>
        </div>
      )}

      {/* Create Job Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-800">สร้างตำแหน่งงานใหม่</h2>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ชื่อตำแหน่ง *</label>
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-400 outline-none text-gray-700" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">แผนก</label>
                <input value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-400 outline-none text-gray-700" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">สถานที่</label>
                <input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-400 outline-none text-gray-700" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">เงินเดือน</label>
                <input value={form.salary_range} onChange={(e) => setForm({ ...form, salary_range: e.target.value })} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-400 outline-none text-gray-700" placeholder="e.g., 30,000 - 50,000" />
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">รายละเอียดงาน *</label>
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={5} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-400 outline-none text-gray-700" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">คุณสมบัติที่ต้องการ</label>
              <textarea value={form.requirements} onChange={(e) => setForm({ ...form, requirements: e.target.value })} rows={4} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-400 outline-none text-gray-700" />
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">สวัสดิการ</label>
              <textarea value={form.benefits} onChange={(e) => setForm({ ...form, benefits: e.target.value })} rows={3} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-400 outline-none text-gray-700" />
            </div>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowCreate(false)} className="px-5 py-2.5 bg-gray-100 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">ยกเลิก</button>
              <button onClick={handleCreate} disabled={saving} className="px-5 py-2.5 bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded-xl text-sm font-medium hover:shadow-lg transition-all disabled:opacity-60 flex items-center gap-2">
                {saving && <Loader2 className="w-4 h-4 animate-spin" />} สร้างตำแหน่งงาน
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Generate JD Modal */}
      {showGenerate && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-800">AI สร้าง Job Description</h2>
                  <p className="text-xs text-gray-500">ระบุข้อมูลเบื้องต้น แล้ว AI จะสร้าง JD ให้</p>
                </div>
              </div>
              <button onClick={() => setShowGenerate(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ชื่อตำแหน่ง *</label>
                <input value={genForm.title} onChange={(e) => setGenForm({ ...genForm, title: e.target.value })} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-400 outline-none text-gray-700" placeholder="e.g., Frontend Developer" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">แผนก</label>
                  <input value={genForm.department} onChange={(e) => setGenForm({ ...genForm, department: e.target.value })} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-400 outline-none text-gray-700" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ระดับ</label>
                  <select value={genForm.seniority_level} onChange={(e) => setGenForm({ ...genForm, seniority_level: e.target.value })} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-400 outline-none text-gray-700">
                    <option value="">ไม่ระบุ</option>
                    <option value="junior">Junior</option>
                    <option value="mid">Mid-level</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Lead</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ทักษะหลัก</label>
                <input value={genForm.key_skills} onChange={(e) => setGenForm({ ...genForm, key_skills: e.target.value })} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-400 outline-none text-gray-700" placeholder="e.g., React, TypeScript, Node.js" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">หมายเหตุเพิ่มเติม</label>
                <textarea value={genForm.additional_notes} onChange={(e) => setGenForm({ ...genForm, additional_notes: e.target.value })} rows={2} className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-400 outline-none text-gray-700" />
              </div>
            </div>
            <div className="flex gap-3 justify-end mt-6">
              <button onClick={() => setShowGenerate(false)} className="px-5 py-2.5 bg-gray-100 text-gray-600 rounded-xl text-sm font-medium">ยกเลิก</button>
              <button onClick={handleGenerate} disabled={generating} className="px-5 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl text-sm font-medium hover:shadow-lg transition-all disabled:opacity-60 flex items-center gap-2">
                {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                {generating ? "กำลังสร้าง..." : "สร้างด้วย AI"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
