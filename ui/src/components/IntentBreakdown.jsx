import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function IntentBreakdown({ results }) {
    if (!results || results.length === 0) return null;

    const counts = {};
    results.forEach((row) => {
        if (!row.dialogue_act) return;
        counts[row.dialogue_act] = (counts[row.dialogue_act] || 0) + 1;
    });

    const data = Object.entries(counts)
        .map(([intent, count]) => ({ intent, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8);

    if (data.length === 0) return null;

    return (
        <div className="container animate-in delay-100" style={{ marginBottom: '2rem' }}>
            <div className="card" style={{ padding: '1.5rem', height: '400px' }}>
                <h3 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '1.125rem' }}>Intent Breakdown</h3>
                <p style={{ marginTop: 0, marginBottom: '1.25rem', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                    Most frequent exact intent predictions in the uploaded chat.
                </p>
                <ResponsiveContainer width="100%" height="82%">
                    <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 35 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" vertical={false} />
                        <XAxis
                            dataKey="intent"
                            stroke="var(--color-text-muted)"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            angle={-20}
                            textAnchor="end"
                            interval={0}
                            height={60}
                        />
                        <YAxis stroke="var(--color-text-muted)" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                        <Tooltip
                            contentStyle={{ backgroundColor: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px' }}
                            itemStyle={{ color: 'var(--color-text-primary)' }}
                            labelStyle={{ color: 'var(--color-text-secondary)' }}
                        />
                        <Bar dataKey="count" fill="var(--color-accent-secondary)" radius={[6, 6, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
