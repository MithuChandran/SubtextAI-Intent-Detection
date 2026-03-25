import React, { useEffect, useRef } from 'react';
import { AlertTriangle, MessageSquare } from 'lucide-react';

export function ResultsSection({ results, scrollToIndex, onScrollComplete }) {
    const itemRefs = useRef([]);

    useEffect(() => {
        if (scrollToIndex !== null && itemRefs.current[scrollToIndex]) {
            itemRefs.current[scrollToIndex].scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
            
            // Add a temporary pulse effect
            const el = itemRefs.current[scrollToIndex];
            el.style.backgroundColor = 'rgba(59, 130, 246, 0.2)';
            el.style.transition = 'background-color 0.5s ease';
            
            setTimeout(() => {
                el.style.backgroundColor = 'transparent';
                onScrollComplete();
            }, 2000);
        }
    }, [scrollToIndex, results, onScrollComplete]);

    if (!results) return null;

    return (
        <div className="animate-in" style={{ marginTop: '2rem', maxWidth: '1200px' }}>

            <div className="card" style={{ overflow: 'hidden' }}>
                {results.length === 0 ? (
                    <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                        No messages match your current filters.
                    </div>
                ) : (
                    results.map((row, idx) => (
                        <div
                            key={idx}
                            ref={el => itemRefs.current[idx] = el}
                            className="responsive-grid-results"
                            style={{
                                borderBottom: idx < results.length - 1 ? '1px solid var(--color-border)' : 'none',
                                backgroundColor: 'transparent'
                            }}
                        >
                            {/* Meta Column */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                                    {row.sender}
                                </span>
                                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
                                    {row.timestamp.split(',')[1] || row.timestamp}
                                </span>

                                {row.dialogue_act && (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                                        <span style={{ fontSize: '0.6rem', color: 'var(--color-text-muted)', fontWeight: 700 }}>PREDICTED INTENT</span>
                                        <div style={{ 
                                            padding: '4px 8px', 
                                            background: 'var(--color-accent-subtle)', 
                                            border: '1px solid var(--color-accent-primary)',
                                            borderRadius: 'var(--radius-sm)',
                                            width: 'fit-content',
                                            color: 'var(--color-accent-primary)',
                                            fontWeight: 600,
                                            fontSize: '0.7rem',
                                            textTransform: 'uppercase',
                                            letterSpacing: '0.02em'
                                        }}>
                                            {row.dialogue_act}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Content Column */}
                            <div style={{ position: 'relative' }}>
                                <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.925rem', lineHeight: '1.5' }}>
                                    {row.message}
                                </p>
                            </div>
                        </div>

                    ))
                )}
            </div>
        </div>
    );
}

