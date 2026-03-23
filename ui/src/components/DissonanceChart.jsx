import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function DissonanceChart({ results }) {
    if (!results || results.length === 0) return null;

    // Prepare data
    const data = results.map((r, i) => ({
        index: i + 1,
        time: r.timestamp.split(',')[0],
        dissonance: r.dissonance_score,
        sender: r.sender,
        message: r.message.substring(0, 30) + "..."
    }));

    return (
        <div className="container animate-in delay-100" style={{ marginBottom: '2rem' }}>
            <div className="card" style={{ padding: '1.5rem', height: '400px' }}>
                <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.125rem' }}>Dissonance Timeline</h3>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'flex', gap: '1rem' }}>
                         <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#3b82f6' }} /> Low Tension
                         </span>
                         <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#f87171' }} /> Conflict
                         </span>
                    </div>
                </div>
                <ResponsiveContainer width="100%" height="85%">
                    <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorDiss" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="var(--color-accent-primary)" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="var(--color-accent-primary)" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="heatGradient" x1="0" y1="0" x2="1" y2="0">
                                {data.map((entry, index) => (
                                    <stop 
                                        key={index} 
                                        offset={`${(index / (data.length - 1)) * 100}%`} 
                                        stopColor={entry.dissonance > 0.6 ? '#f87171' : '#3b82f6'} 
                                    />
                                ))}
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" vertical={false} />
                        <XAxis dataKey="index" stroke="var(--color-text-muted)" fontSize={10} tickLine={false} axisLine={false} />
                        <YAxis stroke="var(--color-text-muted)" fontSize={10} tickLine={false} axisLine={false} domain={[0, 1]} />
                        <Tooltip
                            content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    const d = payload[0].payload;
                                    return (
                                        <div className="card" style={{ padding: '0.75rem', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-card)', maxWidth: '240px' }}>
                                            <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '4px', fontSize: '0.8rem' }}>{d.sender}</div>
                                            <div style={{ fontStyle: 'italic', fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>"{d.message}"</div>
                                            <div style={{ fontSize: '0.75rem', color: d.dissonance > 0.6 ? 'var(--color-danger)' : 'var(--color-accent-primary)', fontWeight: 600 }}>
                                                Dissonance: {Math.round(d.dissonance * 100)}%
                                            </div>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                        <Area
                            type="monotone"
                            dataKey="dissonance"
                            stroke="url(#heatGradient)"
                            strokeWidth={3}
                            fillOpacity={1}
                            fill="url(#colorDiss)"
                            animationDuration={1500}
                            activeDot={{ 
                                r: 6, 
                                stroke: 'white', 
                                strokeWidth: 2, 
                                onClick: (e, payload) => {
                                    if (onPointClick && payload) {
                                        onPointClick(payload.index - 1);
                                    }
                                }
                            }}
                            cursor="pointer"
                        />

                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
