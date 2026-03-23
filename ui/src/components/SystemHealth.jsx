import React, { useState, useEffect } from 'react';
import { Activity, Server, Cpu, Database } from 'lucide-react';
import { getSystemInfo } from '../services/api';

export function SystemHealth() {
    const [info, setInfo] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getSystemInfo()
            .then(data => {
                setInfo(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Health check failed:", err);
                setLoading(false);
            });
    }, []);

    const metrics = [
        { label: "Status", value: info?.status || "Offline", icon: Server, color: info?.status === 'online' ? 'var(--color-success)' : 'var(--color-danger)' },
        { label: "Processor", value: info?.device || "CPU (Default)", icon: Cpu, color: 'var(--color-accent-primary)' },
        { label: "Model Architecture", value: info?.model_path?.split('/').pop() || "N/A", icon: Database, color: 'var(--color-accent-secondary)' },
    ];

    return (
        <div className="container animate-in" style={{ paddingTop: '2rem', maxWidth: '1200px' }}>

            <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '2rem' }}>System Health</h1>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
                {metrics.map((m, i) => (
                    <div key={i} className="card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ color: m.color }}>
                            <m.icon size={24} />
                        </div>
                        <div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{m.label}</div>
                            <div style={{ fontWeight: 600 }}>{m.value}</div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="card" style={{ padding: '2rem' }}>
                <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Activity size={18} /> Enabled Features
                </h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1rem' }}>
                    {info?.features?.map((f, i) => (
                        <span 
                            key={i} 
                            style={{ 
                                padding: '4px 12px', 
                                background: 'rgba(255,255,255,0.05)', 
                                border: '1px solid var(--color-border)',
                                borderRadius: '12px',
                                fontSize: '0.8rem',
                                color: 'var(--color-text-secondary)'
                            }}
                        >
                            {f.replace('_', ' ')}
                        </span>
                    )) || "N/A"}
                </div>
            </div>
        </div>
    );
}
