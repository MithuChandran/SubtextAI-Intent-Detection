import React from 'react';
import { MessageSquare, Zap, Activity, Tags, Brain } from 'lucide-react';

export function DashboardStats({ results }) {
    if (!results || results.length === 0) return null;

    // Calculate Stats
    const totalMessages = results.length;

    const senderCounts = {};
    let totalChars = 0;
    const intentStats = {};
    let totalIntentConfidence = 0;
    let confidentIntentCount = 0;

    results.forEach(r => {
        // Senders
        if (r.sender) {
            senderCounts[r.sender] = (senderCounts[r.sender] || 0) + 1;
        }
        // Message Length
        if (r.message) {
            totalChars += r.message.length;
        }
        // Intents
        if (r.dialogue_act) {
            intentStats[r.dialogue_act] = (intentStats[r.dialogue_act] || 0) + 1;
            if (typeof r.dialogue_act_confidence === 'number') {
                totalIntentConfidence += r.dialogue_act_confidence;
                confidentIntentCount++;
            }
        }
    });

    const topSenderEntry = Object.entries(senderCounts).sort((a, b) => b[1] - a[1])[0];
    const topSender = topSenderEntry ? `${topSenderEntry[0]} (${topSenderEntry[1]})` : "N/A";
    const totalParticipants = Object.keys(senderCounts).length;
    const avgChars = (totalChars / totalMessages).toFixed(1);

    const topIntent = Object.entries(intentStats).sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A";
    const uniqueIntents = Object.keys(intentStats).length;

    const cards = [
        { label: "Total Messages", value: totalMessages, icon: MessageSquare, color: "var(--color-accent-primary)" },
        { label: "Participants", value: totalParticipants, icon: Activity, color: "var(--color-success)" },
        { label: "Top Sender", value: topSender, icon: Tags, color: "var(--color-accent-secondary)" },
        { label: "Top Intent", value: topIntent, icon: Brain, color: "var(--color-accent-primary)" },
        { label: "Intent Variety", value: uniqueIntents, icon: Tags, color: "var(--color-accent-secondary)" },
        { label: "Avg Msg Length", value: `${avgChars} ch`, icon: MessageSquare, color: "var(--color-text-muted)" },
    ];


    return (
        <div className="container animate-in">
            {/* Intent Analytics Zone */}
            <div style={{ marginBottom: '2rem' }}>
                <h4 style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1rem' }}>Chat Intelligence Breakdown</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
                    {cards.map((item, idx) => (
                        <StatCard key={idx} item={item} />
                    ))}
                </div>
            </div>

        </div>
    );
}

function StatCard({ item }) {
    return (
        <div 
            className="card" 
            style={{ 
                padding: '1.25rem', 
                display: 'flex', 
                alignItems: 'center', 
                gap: '1rem',
                transition: 'transform 0.2s ease, border-color 0.2s ease',
            }}
            onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.2)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.borderColor = 'var(--color-border)';
            }}
        >
            <div
                className="flex-center"
                style={{
                    background: `rgba(0,0,0,0.2)`,
                    width: '42px',
                    height: '42px',
                    borderRadius: 'var(--radius-md)',
                    color: item.color,
                    flexShrink: 0
                }}
            >
                <item.icon size={20} />
            </div>
            <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.label}</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>{item.value}</div>
            </div>
        </div>
    );
}
