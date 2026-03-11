"use client";

import { useEffect, useState } from "react";
import { auditAPI } from "@/lib/api";
import { ClipboardList, ChevronDown, ChevronUp, Filter, Bot, FileText, Users, Briefcase } from "lucide-react";

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [filter, setFilter] = useState("");

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await auditAPI.list({
        limit: 100,
        action: filter || undefined,
      });
      setLogs(res.data.logs);
      setTotal(res.data.total);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchLogs(); }, [filter]);

  const actionColors: Record<string, string> = {
    resume_uploaded: "bg-blue-100 text-blue-700",
    jd_generated: "bg-purple-100 text-purple-700",
    job_created: "bg-emerald-100 text-emerald-700",
    job_updated: "bg-teal-100 text-teal-700",
    job_deleted: "bg-red-100 text-red-600",
    match_computed: "bg-amber-100 text-amber-700",
    chatbot_message: "bg-cyan-100 text-cyan-700",
    status_updated: "bg-orange-100 text-orange-700",
  };

  const actionIcons: Record<string, any> = {
    resume_uploaded: FileText,
    jd_generated: Bot,
    job_created: Briefcase,
    match_computed: Users,
    chatbot_message: Bot,
  };

  const actions = ["resume_uploaded", "jd_generated", "job_created", "job_updated", "job_deleted", "match_computed", "chatbot_message", "status_updated"];

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Audit Logs</h1>
          <p className="text-gray-500 text-sm mt-1">ประวัติการทำงานของระบบ Prompt/Response Tracing ({total} รายการ)</p>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <button
          onClick={() => setFilter("")}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            !filter ? "bg-teal-500 text-white" : "bg-white text-gray-600 border border-gray-200 hover:border-teal-300"
          }`}
        >
          ทั้งหมด
        </button>
        {actions.map((action) => (
          <button
            key={action}
            onClick={() => setFilter(action)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === action ? "bg-teal-500 text-white" : "bg-white text-gray-600 border border-gray-200 hover:border-teal-300"
            }`}
          >
            {action.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {/* Log List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-16 bg-white rounded-xl animate-pulse border border-gray-100" />
          ))}
        </div>
      ) : logs.length > 0 ? (
        <div className="space-y-2">
          {logs.map((log) => {
            const IconComp = actionIcons[log.action] || ClipboardList;
            return (
              <div key={log.id} className="bg-white rounded-xl border border-gray-100 overflow-hidden">
                <button
                  onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="flex items-center gap-3">
                    <IconComp className="w-4 h-4 text-gray-400" />
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${actionColors[log.action] || "bg-gray-100 text-gray-600"}`}>
                      {log.action}
                    </span>
                    <span className="text-sm text-gray-700">{log.details || "—"}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400">
                      {new Date(log.created_at).toLocaleString("th-TH")}
                    </span>
                    {expandedId === log.id ? (
                      <ChevronUp className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                </button>
                {expandedId === log.id && (
                  <div className="px-4 pb-4 pt-0 border-t border-gray-50">
                    <div className="grid grid-cols-2 gap-4 mt-3">
                      {log.prompt_text && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 mb-1">📤 Prompt / Input</p>
                          <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                            {log.prompt_text}
                          </div>
                        </div>
                      )}
                      {log.response_text && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 mb-1">📥 Response / Output</p>
                          <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                            {log.response_text}
                          </div>
                        </div>
                      )}
                    </div>
                    {log.metadata_json && (
                      <div className="mt-3">
                        <p className="text-xs font-medium text-gray-500 mb-1">📋 Metadata</p>
                        <pre className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600 overflow-x-auto">
                          {JSON.stringify(log.metadata_json, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16 text-gray-400">
          <ClipboardList className="w-10 h-10 mx-auto mb-2 text-gray-300" />
          <p>ยังไม่มี Audit Log</p>
        </div>
      )}
    </div>
  );
}
