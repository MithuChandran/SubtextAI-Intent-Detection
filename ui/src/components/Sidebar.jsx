import React from 'react';
import { LayoutDashboard, BookOpen, Activity, X } from 'lucide-react';

export function Sidebar({ activeView, onViewChange, isOpen, onClose }) {
    const menuItems = [
        { id: 'analyze', label: 'Analyze', icon: LayoutDashboard },
        { id: 'methodology', label: 'Methodology', icon: BookOpen },
        { id: 'health', label: 'System Health', icon: Activity },
    ];

    return (
        <aside 
            className={`card sidebar ${isOpen ? 'open' : ''}`} 
            style={{ 
                width: '260px', 
                height: 'calc(100vh - 2rem)', 
                margin: '1rem',
                display: 'flex', 
                flexDirection: 'column',
                position: 'fixed',
                zIndex: 1000
            }}
        >
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ padding: '6px', borderRadius: '8px', background: 'var(--color-accent-primary)' }}>
                        <Activity size={18} color="white" />
                    </div>
                    <span style={{ fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.02em' }}>Subtext AI</span>
                </div>
                
                {/* Mobile Close Button */}
                <button 
                    className="mobile-only"
                    onClick={onClose}
                    style={{ background: 'transparent', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer' }}
                >
                    <X size={20} />
                </button>
            </div>

            <nav style={{ flex: 1, padding: '1rem' }}>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = activeView === item.id;
                        return (
                            <li key={item.id}>
                                <button
                                    onClick={() => onViewChange(item.id)}
                                    style={{
                                        width: '100%',
                                        padding: '0.75rem 1rem',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.75rem',
                                        border: 'none',
                                        borderRadius: 'var(--radius-md)',
                                        background: isActive ? 'var(--color-accent-subtle)' : 'transparent',
                                        color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-secondary)',
                                        cursor: 'pointer',
                                        fontWeight: isActive ? 600 : 500,
                                        transition: 'all 0.2s ease',
                                        textAlign: 'left'
                                    }}
                                >
                                    <Icon size={18} />
                                    <span>{item.label}</span>
                                </button>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            <div style={{ padding: '1.5rem', borderTop: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                    v1.0.0-beta
                </div>
            </div>
        </aside>
    );
}
