import React from 'react';
import { Search, Tags, X } from 'lucide-react';

export function FilterBar({ filters, onFilterChange, availableIntents }) {
    return (
        <div className="card animate-in" style={{ padding: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(200px, 1fr) 200px', gap: '1.5rem', alignItems: 'flex-end' }}>
                {/* Search */}
                <div style={{ position: 'relative' }}>
                    <div style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }}>
                        <Search size={18} />
                    </div>
                    <input 
                        type="text" 
                        placeholder="Search messages or senders..."
                        value={filters.search}
                        onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
                        style={{
                            width: '100%',
                            padding: '1rem 1rem 1rem 3rem',
                            background: 'var(--color-bg-mesh)',
                            border: '1px solid var(--color-border)',
                            borderRadius: 'var(--radius-md)',
                            color: 'var(--color-text-primary)',
                            fontSize: '0.9rem',
                            outline: 'none'
                        }}
                    />
                </div>

                {/* Intent Dropdown */}
                <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Tags size={14} /> Filter by Intent
                    </div>
                    <select
                        value={filters.selectedIntent}
                        onChange={(e) => onFilterChange({ ...filters, selectedIntent: e.target.value })}
                        style={{
                            width: '100%',
                            padding: '1rem',
                            background: 'var(--color-bg-mesh)',
                            border: '1px solid var(--color-border)',
                            borderRadius: 'var(--radius-md)',
                            color: 'var(--color-text-primary)',
                            fontSize: '0.9rem',
                            outline: 'none'
                        }}
                    >
                        <option value="">All Intents</option>
                        {availableIntents.map(intent => (
                            <option key={intent} value={intent}>{intent}</option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
    );
}
