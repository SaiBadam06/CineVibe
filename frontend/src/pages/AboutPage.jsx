import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Database, Sparkles, Tv, Heart, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../supabase';

const AboutPage = () => {
    const navigate = useNavigate();
    const [session, setSession] = useState(null);
    const [profile, setProfile] = useState(null);

    useEffect(() => {
        const getProfile = async (session) => {
            if (!session) return;
            const { data, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', session.user.id)
                .single();
            if (data) setProfile(data);
        };

        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session);
            getProfile(session);
        });

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session);
        });

        return () => subscription.unsubscribe();
    }, []);

    const handleLogout = async () => {
        await supabase.auth.signOut();
        navigate('/login');
    };

    const sections = [
        {
            icon: <Sparkles className="w-6 h-6 text-yellow-400" />,
            title: "AI-Powered Vibe Matching",
            description: "We don't just match keywords. Our system uses advanced AI (Groq/Llama-3) to understand the *nuance* of your request. Whether you want 'sad but hopeful' or 'mind-bending sci-fi', we get it."
        },
        {
            icon: <Database className="w-6 h-6 text-blue-400" />,
            title: "Infinite Database",
            description: "If we don't have a movie in our database, we don't give up. The system automatically 'learns' new movies for requested genres on the fly, expanding our collection every time you search."
        },
        {
            icon: <Heart className="w-6 h-6 text-red-400" />,
            title: "Curated for You",
            description: "Built for movie lovers who hate algorithms that only suggest what's popular. Vibe Coder is about finding the hidden gems that match your specific emotional state."
        }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-8 text-white font-sans flex flex-col items-center">
            <div className="max-w-5xl mx-auto w-full">
                <nav className="flex justify-between items-center mb-16">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500" />
                        <span className="font-bold text-xl tracking-tight">CineVibe</span>
                    </div>
                    {session ? (
                        <div className="flex items-center gap-4">
                            <span className="text-sm text-slate-400 hidden md:block">
                                {profile?.full_name || session.user.email}
                            </span>
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                onClick={handleLogout}
                                className="px-6 py-2 rounded-full border border-red-500/30 bg-red-500/10 hover:bg-red-500/20 text-red-300 transition-colors text-sm font-medium flex items-center gap-2"
                            >
                                <LogOut size={16} /> Sign Out
                            </motion.button>
                        </div>
                    ) : (
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            onClick={() => navigate('/login')}
                            className="px-6 py-2 rounded-full border border-white/20 hover:bg-white/10 transition-colors text-sm font-medium"
                        >
                            Login
                        </motion.button>
                    )}
                </nav>

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-20"
                >
                    <h1 className="text-6xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400 mb-8 pb-4 tracking-tight">
                        Feel the Movie.
                    </h1>
                    <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto leading-relaxed mb-10">
                        Stop searching by genre. Start searching by <span className="text-white font-semibold">vibe</span>. <br />
                        Our AI understands your mood and finds the perfect match.
                    </p>

                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => navigate('/vibe')}
                        className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-10 py-4 rounded-full font-bold text-lg shadow-xl shadow-purple-900/30 flex items-center gap-3 mx-auto"
                    >
                        <Sparkles className="w-5 h-5" />
                        Explore Recommender
                    </motion.button>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
                    {sections.map((section, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="glass p-8 rounded-2xl border border-white/5 bg-white/5 hover:bg-white/10 transition-colors"
                        >
                            <div className="mb-4 p-3 bg-white/5 rounded-xl w-fit">
                                {section.icon}
                            </div>
                            <h3 className="text-xl font-bold mb-3 text-purple-100">{section.title}</h3>
                            <p className="text-slate-400 leading-relaxed">{section.description}</p>
                        </motion.div>
                    ))}
                </div>

                <div className="text-center border-t border-white/10 pt-12">
                    <h2 className="text-2xl font-bold mb-8">Tech Stack</h2>
                    <div className="flex flex-wrap justify-center gap-4">
                        {['React', 'Tailwind', 'Framer Motion', 'FastAPI', 'Supabase'].map((tech) => (
                            <span key={tech} className="px-4 py-2 rounded-full bg-slate-800 text-slate-300 border border-slate-700 text-sm">
                                {tech}
                            </span>
                        ))}
                    </div>
                </div>

                <footer className="mt-20 text-center text-slate-600 text-sm">
                    © 2025 CineVibe Project. All rights reserved.
                </footer>
            </div>
        </div>
    );
};

export default AboutPage;
