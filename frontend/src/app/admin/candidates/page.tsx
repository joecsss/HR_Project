"use client";

import { useEffect, useState } from "react";
import { candidatesAPI, jobsAPI } from "@/lib/api";
import { Users, Search, ChevronDown, ChevronUp, Star, FileText, Award } from "lucide-react";

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<number | null>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cRes, jRes] = await Promise.all([
          candidatesAPI.list({ limit: 100 }),
          jobsAPI.list({ status_filter: "active", limit: 50 }),
        ]);
        setCandidates(cRes.data.candidates);
        setJobs(jRes.data.jobs);
      } catch {} finally { setLoading(false); }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedJob) {
      candidatesAPI.getApplicationsForJob(selectedJob, { limit: 100 })
        .then((res) => setApplications(res.data.applications))
        .catch(() => setApplications([]));
    }
  }, [selectedJob]);

  const getScoreColor = (score: number | null) => {
    if (!score) return "text-gray-400";
    if (score >= 80) return "text-emerald-600";
    if (score >= 60) return "text-teal-600";
    if (score >= 40) return "text-amber-600";
    return "text-red-500";
  };

  const getScoreBg = (score: number | null) => {
    if (!score) return "bg-gray-100";
    if (score >= 80) return "bg-emerald-50 border-emerald-200";
    if (score >= 60) return "bg-teal-50 border-teal-200";
    if (score >= 40) return "bg-amber-50 border-amber-200";
    return "bg-red-50 border-red-200";
  };

  const filteredCandidates = candidates.filter((c) =>
    (c.skills || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Candidates</h1>
          <p className="text-gray-500 text-sm mt-1">ดูรายชื่อผู้สมัครและคะแนนการจับคู่</p>
        </div>
      </div>

      {/* Job filter */}
      {jobs.length > 0 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">กรองตามตำแหน่งงาน</label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedJob(null)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                !selectedJob ? "bg-teal-500 text-white" : "bg-white text-gray-600 border border-gray-200 hover:border-teal-300"
              }`}
            >
              ทั้งหมด
            </button>
            {jobs.map((job) => (
              <button
                key={job.id}
                onClick={() => setSelectedJob(job.id)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  selectedJob === job.id ? "bg-teal-500 text-white" : "bg-white text-gray-600 border border-gray-200 hover:border-teal-300"
                }`}
              >
                {job.title}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="ค้นหาด้วยทักษะ..."
          className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-teal-400 focus:border-transparent outline-none text-sm text-gray-700"
        />
      </div>

      {/* Applications for selected job */}
      {selectedJob && applications.length > 0 && (
        <div className="mb-8">
          <h2 className="font-bold text-gray-700 mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-teal-500" /> ผู้สมัครสำหรับตำแหน่งนี้ (เรียงตามคะแนน)
          </h2>
          <div className="space-y-3">
            {applications.map((app, i) => (
              <div key={app.id} className={`bg-white rounded-2xl p-5 border ${getScoreBg(app.match_score)} card-hover`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gradient-to-br from-teal-400 to-cyan-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      #{i + 1}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{app.candidate_name || "ผู้สมัคร"}</h3>
                      <p className="text-sm text-gray-500">{app.candidate_skills?.substring(0, 80) || "—"}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getScoreColor(app.match_score)}`}>
                        {app.match_score ? `${app.match_score}%` : "N/A"}
                      </div>
                      <div className="text-xs text-gray-400">Match Score</div>
                    </div>
                    <button
                      onClick={() => setExpandedId(expandedId === app.id ? null : app.id)}
                      className="p-2 text-gray-400 hover:text-teal-500 transition-colors"
                    >
                      {expandedId === app.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
                {expandedId === app.id && app.match_reasoning && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-sm text-gray-600 leading-relaxed">{app.match_reasoning}</p>
                    <div className="mt-3 flex items-center gap-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        app.status === "pending" ? "bg-amber-100 text-amber-700" :
                        app.status === "shortlisted" ? "bg-emerald-100 text-emerald-700" :
                        app.status === "rejected" ? "bg-red-100 text-red-600" :
                        "bg-gray-100 text-gray-600"
                      }`}>
                        {app.status}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Candidates */}
      {!selectedJob && (
        loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-white rounded-2xl animate-pulse border border-gray-100" />
            ))}
          </div>
        ) : filteredCandidates.length > 0 ? (
          <div className="space-y-3">
            {filteredCandidates.map((candidate) => (
              <div key={candidate.id} className="bg-white rounded-2xl p-5 border border-gray-100 card-hover">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <FileText className="w-4 h-4 text-teal-500" />
                      <h3 className="font-medium text-gray-800">
                        {candidate.resume_original_name || `Candidate #${candidate.id}`}
                      </h3>
                    </div>
                    <p className="text-sm text-gray-500 ml-7">
                      ทักษะ: {candidate.skills?.substring(0, 100) || "ไม่ระบุ"}
                    </p>
                    <p className="text-sm text-gray-400 ml-7">
                      ประสบการณ์: {candidate.experience_years ? `${candidate.experience_years} ปี` : "ไม่ระบุ"}
                    </p>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(candidate.created_at).toLocaleDateString("th-TH")}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 text-gray-400">
            <Users className="w-10 h-10 mx-auto mb-2 text-gray-300" />
            <p>ยังไม่มีผู้สมัคร</p>
          </div>
        )
      )}
    </div>
  );
}
