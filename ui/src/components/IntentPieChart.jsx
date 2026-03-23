import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = ['#3b82f6', '#0ea5e9', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b', '#10b981'];

export function IntentPieChart({ results }) {
  if (!results || results.length === 0) return null;

  // Aggregate intent counts
  const intentCounts = {};
  results.forEach(r => {
    if (r.dialogue_act) {
      intentCounts[r.dialogue_act] = (intentCounts[r.dialogue_act] || 0) + 1;
    }
  });

  const sortedIntents = Object.entries(intentCounts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const top4 = sortedIntents.slice(0, 4);
  const others = sortedIntents.slice(4);
  
  const data = [...top4];
  if (others.length > 0) {
    const othersCount = others.reduce((acc, curr) => acc + curr.value, 0);
    data.push({ name: 'Other', value: othersCount });
  }


  return (
    <div className="card animate-in delay-200" style={{ padding: '1.5rem', height: '400px', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.125rem' }}>Intent Distribution</h3>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}

              paddingAngle={5}
              dataKey="value"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              labelLine={true}
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', backdropFilter: 'blur(10px)' }}
              itemStyle={{ color: 'var(--color-text-primary)' }}
            />
            <Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ paddingTop: '20px' }} />
          </PieChart>
        </ResponsiveContainer>

      </div>
    </div>
  );
}
