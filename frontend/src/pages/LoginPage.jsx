import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { supabase } from '../supabase';
import { Mail, Lock, AlertCircle, CheckCircle } from 'lucide-react';

const LoginPage = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [fullName, setFullName] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [isSignUp, setIsSignUp] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [profile, setProfile] = useState(null);

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
                const trimmedName = fullName.trim();
                console.log("Attempting Signup for:", email, "Name:", trimmedName);

                const { data, error } = await supabase.auth.signUp({
                    email,
                    password,
                    options: {
                        data: {
                            full_name: trimmedName,
                        }
                    }
                });

                console.log("Signup Response:", { data, error });
                if (error) throw error;

                // On successful sign-up, create or upsert the profile row in 'profiles' table
                const user = data?.user;
                if (user) {
                    // Safe upsert: will create or update the row with the same id
                    const { error: upsertError } = await supabase
                        .from('profiles')
                        .upsert([{
                            id: user.id,
                            email: email,
                            full_name: trimmedName,
                            created_at: new Date().toISOString()
                            // optionally add preferences: favorite_genres: [], languages: []
                        }], { onConflict: 'id' }); // 'onConflict' ensures id-based upsert

                    if (upsertError) {
                        console.error("Profile upsert failed:", upsertError);
                        // Decide whether to show an error or continue — you can still allow login
                    } else {
                        console.log("Profile created successfully for user:", user.id);
                    }
                }

                if (data.session) {
                    navigate('/');
                } else {
                    setMessage({ type: 'success', text: "Account created! Logging you in..." });

                    // Attempt auto-login
                    setTimeout(async () => {
                        const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
                            email,
                            password,
                        });
                        if (signInData.session) navigate('/');
                        else setMessage({ type: 'success', text: "Account created! Please check your email or try signing in." });
                    }, 1500);
                }
            } else {
                const { data, error } = await supabase.auth.signInWithPassword({
                    email,
                    password,
                });
                if (error) throw error;

                const user = data?.user;

                // Fetch the profile row
                if (user) {
                    const { data: profileData, error: profileError } = await supabase
                        .from('profiles')
                        .select('*')
                        .eq('id', user.id)
                        .single();

                    if (profileError) {
                        // If there's no profile (possible), create one from auth metadata
                        if (profileError.code === 'PGRST116') { // single() not found error
                            console.log("Profile not found, creating one...");
                            await supabase.from('profiles').insert({
                                id: user.id,
                                email: user.email,
                                full_name: user.user_metadata?.full_name || ''
                            });
                        } else {
                            console.error('Error fetching profile:', profileError);
                        }
                    } else {
                        // Save profile to state for personalization
                        console.log("Profile fetched successfully:", profileData);
                        setProfile(profileData);
                    }
                }

                navigate('/');
            }
        } catch (err) {
            console.error("Auth error:", err);
            setMessage({ type: 'error', text: err.message || "Authentication failed. Check your credentials." });
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

                <div className="flex p-1 bg-slate-800/50 rounded-xl mb-8 border border-slate-700">
                    <button
                        onClick={() => { setIsSignUp(false); setMessage({ type: '', text: '' }); }}
                        className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${!isSignUp ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                    >
                        Sign In
                    </button>
                    <button
                        onClick={() => { setIsSignUp(true); setMessage({ type: '', text: '' }); }}
                        className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${isSignUp ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                    >
                        Create Account
                    </button>
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

                <form onSubmit={handleAuth} className="space-y-5">
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

                    {isSignUp && (
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="relative"
                        >
                            <span className="absolute left-3 top-3.5 text-slate-500 font-bold text-xs uppercase opacity-50">Name</span>
                            <input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                required={isSignUp}
                                placeholder="Full Name (e.g. John Doe)"
                                className="w-full pl-16 pr-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all placeholder-slate-500"
                            />
                        </motion.div>
                    )}

                    <div className="relative">
                        <Lock className="absolute left-3 top-3.5 text-slate-500" size={18} />
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength={6}
                            placeholder="Password"
                            className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all placeholder-slate-500"
                        />
                    </div>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3 rounded-lg font-semibold shadow-lg transition-all disabled:opacity-50 flex items-center justify-center ${isSignUp ? 'bg-gradient-to-r from-purple-600 to-pink-600' : 'bg-indigo-600 hover:bg-indigo-500'}`}
                    >
                        {loading ? (
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (isSignUp ? "Sign Up & Join" : "Sign In to CineVibe")}
                    </motion.button>
                </form>

                <p className="mt-6 text-center text-xs text-slate-500">
                    By {isSignUp ? "signing up" : "logging in"}, you agree to find the best vibes in cinema.
                </p>
            </motion.div>
        </div>
    );
};

export default LoginPage;
