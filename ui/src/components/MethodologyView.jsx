import React from 'react';
import { Shield, Target, Zap, MessageCircle } from 'lucide-react';

export function MethodologyView() {
    const concepts = [
        {
            title: "Explicit Intent Detection",
            icon: Target,
            desc: "The core engine classifies every message into one of 30+ precise dialogue acts. This intent discovery is the primary focus of the NLP model.",
            color: "var(--color-accent-primary)"
        },

        {
            title: "Emoji Context",
            icon: MessageCircle,
            desc: "Emojis are not ignored. They are isolated and passed through a dedicated sentiment channel, correcting text-only misclassifications.",
            color: "var(--color-success)"
        },
        {
            title: "Batch Optimization",
            icon: Shield,
            desc: "The system processes entire chat logs in optimized batches (GPU/CPU), ensuring real-time speed even for multi-year conversations.",
            color: "var(--color-accent-secondary)"
        }
    ];

    return (
        <div className="container animate-in" style={{ paddingTop: '2rem', maxWidth: '1200px' }}>

            <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '1rem' }}>Methodology</h1>
            <p style={{ fontSize: '1.1rem', color: 'var(--color-text-secondary)', marginBottom: '3rem' }}>
                Subtext AI combines state-of-the-art Natural Language Processing with custom intent-baseline heuristics.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {concepts.map((c, i) => (
                    <div key={i} className="card" style={{ padding: '2rem' }}>
                        <div style={{ 
                            background: 'rgba(59, 130, 246, 0.1)', 
                            width: '48px', 
                            height: '48px', 
                            borderRadius: '12px', 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center', 
                            marginBottom: '1.5rem',
                            color: c.color
                        }}>
                            <c.icon size={24} />
                        </div>
                        <h3 style={{ marginBottom: '0.75rem' }}>{c.title}</h3>
                        <p style={{ color: 'var(--color-text-secondary)', lineHeight: '1.6', margin: 0 }}>
                            {c.desc}
                        </p>
                    </div>
                ))}
            </div>

            <div className="card" style={{ marginTop: '3rem', padding: '2rem', border: '1px solid var(--color-accent-primary)' }}>
                <h3 style={{ marginTop: 0 }}>Model Pipeline</h3>
                <p style={{ color: 'var(--color-text-muted)' }}>
                    Subtext-v1 Pipeline = [(Text + Emoji Concatenation) -&gt; (RoBERTa-Base Encoder) -&gt; (30-Class Intent Classification)]
                </p>
            </div>

        </div>
    );
}
