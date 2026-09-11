import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Icon from '../../components/ui/Icon';
import { useAuth } from '../../contexts/AuthContext';
import { authApi } from '../../api/auth';
import type { ApiError } from '../../api/types';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const response = await authApi.login(email, password);
      login(response.user);
      
      // Navigate based on actual role from Backend
      if (response.user.role === 'USER') {
        navigate('/app/user/dashboard');
      } else {
        navigate('/app');
      }
    } catch (error) {
      const apiError = error as ApiError;
      setErrorMsg(apiError.detail || 'Authentication failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-slate-50 flex flex-col justify-center items-center p-4 overflow-x-hidden">
      <div className="relative w-full min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8 overflow-hidden">
        {/* Ambient Technical / Metrology Backdrop Patterns */}
        <div className="absolute inset-0 pointer-events-none opacity-40">
          <svg className="w-full h-full text-slate-500/10" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern height="40" id="audit-grid" patternUnits="userSpaceOnUse" width="40">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.75"></path>
                <circle cx="40" cy="40" fill="currentColor" opacity="0.4" r="1.2"></circle>
              </pattern>
            </defs>
            <rect fill="url(#audit-grid)" height="100%" width="100%"></rect>
          </svg>
        </div>
        {/* Atmospheric ambient soft gradients */}
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-slate-200/40 blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-40 -right-40 w-[28rem] h-[28rem] rounded-full bg-blue-100/60 blur-3xl pointer-events-none"></div>
        
        {/* Main Container */}
        <div className="relative w-full max-w-xl z-10 flex flex-col gap-3">
          <div className="flex items-center justify-between px-4 py-1.5 bg-slate-100 rounded-lg border border-slate-200/50 text-[11px] font-semibold text-slate-600">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-slate-900 font-medium font-mono">Systems Operational</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-500">
              <Icon name="verified_user" className="text-[14px]" />
              <span className="font-mono">Legal Metrology Act 2009 Compliant</span>
            </div>
          </div>
          
          {/* Central Authentication Card */}
          <div className="w-full bg-white rounded-xl shadow-xl overflow-hidden border border-slate-200/60">
            {/* Header Banner & Organization Brand Identity */}
            <div className="bg-slate-50 px-4 sm:px-8 pt-8 pb-6 flex flex-col items-center text-center border-b border-slate-100">
              <div className="flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-white rounded-xl shadow-sm p-1.5 mb-2 border border-slate-100">
                <img alt="ComplianceSahayak Logo" className="w-full h-full object-contain rounded-lg" src="/brand/compliancesahayak-logo.png" />
              </div>

              <h1 className="text-2xl sm:text-3xl text-slate-900 tracking-tight font-bold">
                ComplianceSahayak
              </h1>
              <p className="text-xs text-slate-500 mt-0.5 max-w-md font-semibold tracking-wide">
                AI-Assisted Legal Metrology Compliance Platform
              </p>
              <div className="w-12 h-0.5 bg-slate-200 my-3"></div>
              <h2 className="text-lg text-slate-900 font-bold">
                Platform Sign In
              </h2>
              <p className="text-xs text-slate-500 max-w-sm mt-1">Sign in to your ComplianceSahayak account.</p>
            </div>
            
            {/* Form Workspace Section */}
            <div className="p-4 sm:p-8 flex flex-col gap-4 bg-white">
              {errorMsg && (
                <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm border border-red-200 font-medium">
                  {errorMsg}
                </div>
              )}
              {/* Sign-In Form */}
              <form className="flex flex-col gap-4" onSubmit={handleAuthSubmit}>
                {/* Email / Username Input */}
                <div className="flex flex-col gap-1">
                  <div className="flex justify-between items-center">
                    <label className="text-xs text-slate-900 font-bold" htmlFor="workEmail">Email / Username</label>
                  </div>
                  <div className="relative flex items-center">
                    <Icon name="alternate_email" className="absolute left-3 text-slate-400 text-[18px] pointer-events-none" />
                    <input 
                      className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm pl-10 pr-3 py-2.5 sm:py-3 rounded-lg outline-none focus:bg-white focus:ring-1 focus:ring-slate-900 transition-all placeholder:text-slate-400" 
                      id="workEmail" 
                      name="email" 
                      placeholder="name@organization.com" 
                      required 
                      type="email" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                </div>
                
                {/* Password Input with Toggle */}
                <div className="flex flex-col gap-1">
                  <div className="flex justify-between items-center">
                    <label className="text-xs text-slate-900 font-bold" htmlFor="accountPassword">Password</label>
                    <button 
                      className="text-[11px] font-semibold text-slate-500 hover:text-slate-900 transition-colors bg-transparent border-none p-0 cursor-pointer" 
                      type="button"
                      onClick={() => alert('Password reset email delivery is unavailable in the local environment.')}
                    >
                      Forgot Password?
                    </button>
                  </div>
                  <div className="relative flex items-center">
                    <Icon name="lock_open" className="absolute left-3 text-slate-400 text-[18px] pointer-events-none" />
                    <input 
                      className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm pl-10 pr-10 py-2.5 sm:py-3 rounded-lg outline-none focus:bg-white focus:ring-1 focus:ring-slate-900 transition-all placeholder:text-slate-400" 
                      id="accountPassword" 
                      name="password" 
                      placeholder="Enter your password" 
                      required 
                      type={showPassword ? "text" : "password"} 
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                    <button 
                      aria-label="Toggle Password Visibility" 
                      className="absolute right-3 text-slate-400 hover:text-slate-700 flex items-center justify-center p-1 rounded transition-colors" 
                      onClick={togglePasswordVisibility} 
                      type="button"
                    >
                      <Icon name={showPassword ? 'visibility_off' : 'visibility'} className="text-[18px]" />
                    </button>
                  </div>
                </div>
                
                {/* Options Row: Remember & Audit Log Ack */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-1">
                  <label className="flex items-center gap-1.5 cursor-pointer select-none">
                    <input defaultChecked className="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900 cursor-pointer" id="rememberSession" type="checkbox" />
                    <span className="text-xs text-slate-600">Remember me on this device</span>
                  </label>
                </div>
                
                {/* Primary Submission CTA */}
                <button 
                  className={`w-full mt-1 bg-slate-900 text-white text-sm font-semibold py-3 px-5 rounded-lg shadow-sm hover:bg-slate-800 active:scale-[0.99] transition-all flex items-center justify-center gap-1.5 group ${isSubmitting ? 'opacity-80 cursor-wait' : ''}`} 
                  disabled={isSubmitting}
                  type="submit"
                >
                  {isSubmitting ? (
                    <>
                      <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                      <span>Verifying Metrology Key...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In</span>
                      <Icon name="arrow_forward" className="text-[18px] group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </form>
            </div>
            
            {/* Security Notice Footer */}
            <div className="bg-slate-50 border-t border-slate-100 px-4 sm:px-8 py-3 text-center">
              <p className="text-[11px] font-semibold text-slate-500 leading-relaxed font-mono">Sign in to access your Legal Metrology compliance workspace.</p>
            </div>
          </div>
          
          {/* Regulatory Platform Disclaimer */}
          <footer className="text-center px-3 text-slate-500 text-xs mt-2">
            <p className="text-slate-400 font-mono">ComplianceSahayak · AI-Assisted Legal Metrology Compliance Platform</p>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
