import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { supabase } from '../supabase';
import { Mail, Lock, AlertCircle, CheckCircle } from 'lucide-react';

const LoginPage = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [isSignUp, setIsSignUp] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (session) {
                navigate('/');
            }
        });
    }, [navigate]);

    const handleAuth = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });

        try {
            if (isSignUp) {
                const { data, error } = await supabase.auth.signUp({
                    email,
                    password,
                });
                if (error) throw error;

                // Create profile in profiles table
                if (data.user) {
                    await supabase.table('profiles').upsert({
                        id: data.user.id,
                        email: data.user.email,
                        updated_at: new Date().toISOString()
                    });
                }

                if (data.session) {
                    navigate('/');
                } else {
                    // If session is null, it usually means email confirmation is ON.
                    // But since the user wants to avoid it, we just give a generic success or try to login.
                    setMessage({ type: 'success', text: "Account created! Logging you in..." });

                    // Attempt auto-login just in case (race condition or setting lag)
                    setTimeout(async () => {
                        const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
                            email,
                            password,
                        });
                        if (signInData.session) navigate('/');
                        else setMessage({ type: 'success', text: "Account created! Please check your email (or disable confirmation in Supabase)." });
                    }, 1000);
                }
            } else {
                const { error } = await supabase.auth.signInWithPassword({
                    email,
                    password,
                });
                if (error) throw error;
                navigate('/');
            }
        } catch (err) {
            setMessage({ type: 'error', text: err.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900 p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass p-8 rounded-2xl w-full max-w-md backdrop-blur-xl border border-white/10 shadow-2xl"
            >
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-400 mb-2">
                        {isSignUp ? "Create Account" : "Welcome Back"}
                    </h1>
                    <p className="text-slate-400 text-sm">
                        {isSignUp ? "Join the vibe community" : "Sign in to find your movie"}
                    </p>
                </div>

                {message.text && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className={`mb-6 p-3 rounded-lg flex items-center gap-2 text-sm ${message.type === 'error' ? 'bg-red-500/20 text-red-200 border border-red-500/30' : 'bg-emerald-500/20 text-emerald-200 border border-emerald-500/30'}`}
                    >
                        {message.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle size={16} />}
                        {message.text}
                    </motion.div>
                )}

                <form onSubmit={handleAuth} className="space-y-6">
                    <div className="relative">
                        <Mail className="absolute left-3 top-3.5 text-slate-500" size={18} />
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="Email address"
                            className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all placeholder-slate-500"
                        />
                    </div>
                    <div className="relative">
                        <Lock className="absolute left-3 top-3.5 text-slate-500" size={18} />
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength={6}
                            placeholder="Password (min 6 chars)"
                            className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all placeholder-slate-500"
                        />
                    </div>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg font-semibold shadow-lg hover:shadow-purple-500/30 transition-all disabled:opacity-50 flex items-center justify-center"
                    >
                        {loading ? (
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (isSignUp ? "Sign Up" : "Sign In")}
                    </motion.button>
                </form>

                <p className="mt-6 text-center text-sm text-slate-400">
                    {isSignUp ? "Already have an account?" : "Don't have an account?"}
                    <span
                        onClick={() => {
                            setIsSignUp(!isSignUp);
                            setMessage({ type: '', text: '' });
                        }}
                        className="text-purple-400 cursor-pointer hover:underline ml-1 font-semibold"
                    >
                        {isSignUp ? "Sign In" : "Sign Up"}
                    </span>
                </p>
            </motion.div>
        </div>
    );
};

export default LoginPage;
