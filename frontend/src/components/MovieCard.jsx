import React from 'react';
import { motion } from 'framer-motion';

const MovieCard = ({ title, description, mood_tags, tags, poster_url, imageUrl, ott }) => {
    // Handle inconsistent matching
    const displayTags = mood_tags || tags || [];

    // Use a fallback gradient if no valid image URL
    const hasValidImage = poster_url && poster_url.startsWith('http') && !poster_url.includes('via.placeholder');

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ y: -5 }}
            className="glass rounded-xl overflow-hidden group hover:shadow-2xl transition-all duration-300 flex flex-col h-full bg-slate-900/50 border border-white/5"
        >
            <div className="relative aspect-[2/3] overflow-hidden bg-slate-800">
                {hasValidImage ? (
                    <img
                        src={poster_url}
                        alt={title}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                ) : (
                    <div className="w-full h-full bg-gradient-to-br from-purple-900 to-indigo-900 flex items-center justify-center p-6 text-center">
                        <h3 className="text-xl font-bold text-white opacity-50 group-hover:opacity-100 transition-opacity">{title}</h3>
                    </div>
                )}

                {/* OTT Badge */}
                {ott && (
                    <div className="absolute top-2 right-2 bg-black/70 backdrop-blur-sm text-xs font-bold text-white px-2 py-1 rounded-md border border-white/20 shadow-lg">
                        {ott}
                    </div>
                )}

                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                    {/* Simple truncation for "one line" feel */}
                    <p className="text-sm text-gray-200 line-clamp-2">{description}</p>
                </div>
            </div>

            <div className="p-4 flex flex-col gap-2">
                <h3 className="text-lg font-bold truncate text-white" title={title}>{title}</h3>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-2">
                    {displayTags.slice(0, 3).map((tag, i) => (
                        <span key={i} className="text-[10px] uppercase tracking-wider px-2 py-1 rounded-full bg-white/5 text-purple-200 border border-white/10">
                            {tag}
                        </span>
                    ))}
                </div>

                {/* Single Line Description / Tagline (Using Description truncated) */}
                {!hasValidImage && (
                    <p className="text-xs text-slate-400 line-clamp-2">{description}</p>
                )}
            </div>
        </motion.div>
    );
};

export default MovieCard;
