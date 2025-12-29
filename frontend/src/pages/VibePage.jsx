import React, { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Search, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import MovieCard from '../components/MovieCard';

const VibePage = () => {
    const [mood, setMood] = useState('');
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(false);
    const [matchType, setMatchType] = useState('');
    const [newlyGenerated, setNewlyGenerated] = useState(false);
    const [targetGenre, setTargetGenre] = useState('');

    const handleSearch = async () => {
        if (!mood.trim()) return;
        setLoading(true);
        setMovies([]);
        setMatchType('');
        setNewlyGenerated(false);
        try {
            const response = await axios.post('http://127.0.0.1:8000/recommend', { mood });
            if (response.data.movies) {
                setMovies(response.data.movies);
                setMatchType(response.data.match_type);
                setNewlyGenerated(response.data.generated_new);
                setTargetGenre(response.data.target_genre);
            } else {
                setMovies([])
            }
            setLoading(false);

        } catch (error) {
            console.error("Error fetching movies:", error);
            setLoading(false);
            alert("Failed to fetch recommendations. Ensure backend is running.");
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-8">
            <div className="max-w-6xl mx-auto">
                <header className="flex justify-between items-center mb-12">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-400">
                        CineVibe
                    </h1>
                    <div className="flex items-center gap-4">
                        <Link to="/" className="text-slate-400 hover:text-white transition-colors font-medium">
                            About
                        </Link>
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500" />
                    </div>
                </header>

                <section className="mb-16 text-center">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-4xl md:text-5xl font-bold mb-6 text-white"
                    >
                        What's your vibe today?
                    </motion.h2>

                    <div className="relative max-w-2xl mx-auto bg-slate-800/50 p-2 rounded-2xl glass transition-all focus-within:ring-2 focus-within:ring-purple-500/50">
                        <textarea
                            className="w-full bg-transparent text-lg text-white placeholder-slate-400 border-none focus:ring-0 resize-none h-24 p-4"
                            placeholder="I'm feeling lazy and want to watch something easy..."
                            value={mood}
                            onChange={(e) => setMood(e.target.value)}
                        />
                        <div className="flex justify-between items-center px-4 pb-2">
                            <span className="text-xs text-slate-500">AI-powered recommendations</span>
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={handleSearch}
                                disabled={loading}
                                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-xl font-semibold flex items-center gap-2 shadow-lg shadow-purple-900/20 disabled:opacity-50"
                            >
                                {loading ? <Sparkles className="animate-spin w-5 h-5" /> : <Search className="w-5 h-5" />}
                                <span>Find Movies</span>
                            </motion.button>
                        </div>
                    </div>
                </section>

                {/* Match Status Message */}
                {newlyGenerated && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="mb-8 p-6 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 rounded-xl text-center backdrop-blur-md"
                    >
                        <h3 className="text-xl font-bold text-emerald-300 mb-2">✨ New Movies Generated!</h3>
                        <p className="text-indigo-100">
                            We didn't have any <span className="font-bold text-white">{targetGenre}</span> movies in our database,
                            so we asked the AI to find some for you. They've been saved for next time!
                        </p>
                    </motion.div>
                )}

                {!newlyGenerated && matchType === 'related' && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8 p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-center backdrop-blur-md"
                    >
                        <p className="text-indigo-200">
                            We couldn't find an exact match for that, but here are some <span className="font-bold text-white">related movies</span> you might like based on the vibe.
                        </p>
                    </motion.div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {movies.map((movie, index) => (
                        <MovieCard key={index} {...movie} />
                    ))}
                </div>
                {!loading && movies.length === 0 && matchType === 'none' && (
                    <div className="text-center text-slate-400 mt-12">
                        <p className="text-xl">No specific movies found for that vibe.</p>
                        <p className="text-sm mt-2">Try adding more detail or checking the database.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default VibePage;
