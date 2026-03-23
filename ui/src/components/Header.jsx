import React from 'react';
import { MessageSquareText } from 'lucide-react';

export function Header() {
    return (
        <header style={{
            padding: '1.5rem 0',
            borderBottom: '1px solid var(--color-border)',
            marginBottom: '2rem',
            backgroundColor: 'var(--color-bg-primary)'
        }}>
            <div className="container flex-between">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div
                        className="flex-center"
                        style={{
                            background: 'var(--color-accent-primary)',
                            width: '32px',
                            height: '32px',
                            borderRadius: 'var(--radius-md)',
                            color: 'white'
                        }}
                    >
                        <MessageSquareText size={20} />
                    </div>
                    <div>
                        <h1
                            style={{
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                margin: 0,
                                color: 'var(--color-text-primary)'
                            }}
                        >
                            Subtext AI
                        </h1>
                        <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                            Emoji-Aware Intent Detection
                        </p>
                    </div>
                </div>

                <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                    Advanced Dialogue Act Analysis
                </p>
            </div>
        </header>
    );
}
