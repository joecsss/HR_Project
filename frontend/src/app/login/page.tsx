"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { Bot, Eye, EyeOff, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("applicant");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isLogin) {
        const me = await login(email, password);
        toast.success("เข้าสู่ระบบสำเร็จ!");
        // Redirect based on actual user role
        router.push(me.role === "admin" ? "/admin/dashboard" : "/applicant/jobs");
      } else {
        await register({ email, password, full_name: fullName, role });
        toast.success("สมัครสมาชิกสำเร็จ!");
        setIsLogin(true);
        setPassword("");
        return;
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "เกิดข้อผิดพลาด กรุณาลองใหม่");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#0f3d3e] via-[#0d6e6e] to-[#0d9488] items-center justify-center p-12 relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute top-20 left-20 w-64 h-64 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-teal-300/10 rounded-full blur-3xl" />
        
        <div className="relative z-10 text-center max-w-lg">
          <div className="w-20 h-20 bg-white/10 backdrop-blur rounded-2xl flex items-center justify-center mx-auto mb-8">
            <Bot className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">HR Assistant AI</h1>
          <p className="text-teal-100 text-lg leading-relaxed">
            ระบบผู้ช่วย HR อัจฉริยะ ขับเคลื่อนด้วย Generative AI
            <br />
            ตั้งแต่การสรรหา วิเคราะห์ จับคู่ จนถึงการคัดเลือก
          </p>
          <div className="mt-12 grid grid-cols-3 gap-6">
            {[
              { label: "Resume Parser", value: "AI" },
              { label: "Smart Match", value: "95%" },
              { label: "ประหยัดเวลา", value: "80%" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className="text-teal-200 text-xs mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <Bot className="w-10 h-10 text-teal-600" />
            <span className="text-2xl font-bold gradient-text">HR Assistant AI</span>
          </div>

          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            {isLogin ? "เข้าสู่ระบบ" : "สมัครสมาชิก"}
          </h2>
          <p className="text-gray-500 mb-8">
            {isLogin
              ? "เข้าสู่ระบบเพื่อจัดการงาน HR ของคุณ"
              : "สร้างบัญชีใหม่เพื่อเริ่มใช้งาน"}
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {!isLogin && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    ชื่อ-นามสกุล
                  </label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-teal-400 focus:border-transparent outline-none text-gray-700 transition-all"
                    placeholder="กรอกชื่อ-นามสกุล"
                    required
                  />
                </div>

              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                อีเมล
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-teal-400 focus:border-transparent outline-none text-gray-700 transition-all"
                placeholder="example@company.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                รหัสผ่าน
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-teal-400 focus:border-transparent outline-none text-gray-700 pr-12 transition-all"
                  placeholder="กรอกรหัสผ่าน"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-semibold rounded-xl hover:from-teal-600 hover:to-emerald-600 transition-all shadow-lg shadow-teal-500/25 disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {loading && <Loader2 className="w-5 h-5 animate-spin" />}
              {isLogin ? "เข้าสู่ระบบ" : "สมัครสมาชิก"}
            </button>
          </form>

          <p className="text-center text-gray-500 mt-6 text-sm">
            {isLogin ? "ยังไม่มีบัญชี?" : "มีบัญชีอยู่แล้ว?"}{" "}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-teal-600 font-semibold hover:underline"
            >
              {isLogin ? "สมัครสมาชิก" : "เข้าสู่ระบบ"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
