import React, { useState, useMemo } from 'react';
import { UploadSection } from './UploadSection';
import { DashboardStats } from './DashboardStats';
import { IntentPieChart } from './IntentPieChart';
import { ResultsSection } from './ResultsSection';
import { FilterBar } from './FilterBar';

export function AnalyzeView({ file, onFileChange, onUpload, loading, error, results }) {
    const [filters, setFilters] = useState({
        search: '',
        selectedIntent: ''
    });

    const [scrollToIndex, setScrollToIndex] = useState(null);

    // Filter Logic
    const filteredResults = useMemo(() => {
        if (!results) return null;
        return results.filter(r => {
            const matchesSearch = (r.message || "").toLowerCase().includes(filters.search.toLowerCase()) || 
                                 (r.sender || "").toLowerCase().includes(filters.search.toLowerCase());
            const matchesIntent = !filters.selectedIntent || r.dialogue_act === filters.selectedIntent;
            return matchesSearch && matchesIntent;
        });
    }, [results, filters]);

    const availableIntents = useMemo(() => {
        if (!results) return [];
        return Array.from(new Set(results.map(r => r.dialogue_act).filter(Boolean))).sort();
    }, [results]);

    const handleChartClick = (index) => {
        // Clear search and intent filters to ensure the message is visible
        setFilters({ search: '', selectedIntent: '' });
        // Trigger scroll
        setScrollToIndex(index);
    };

    return (
        <>
            <div className="container" style={{ paddingTop: '2rem', maxWidth: '1200px' }}>
                <UploadSection 
                    file={file} 
                    onFileChange={onFileChange} 
                    onUpload={onUpload} 
                    loading={loading} 
                    error={error} 
                />
            </div>
            
            {results && (
                <div className="container" style={{ maxWidth: '1200px' }}>
                    <div style={{ margin: '3rem auto 1rem', padding: '0' }}>
                        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Analysis Dashboard</h2>
                    </div>
                    
                    <DashboardStats results={filteredResults || results} />
                    
                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
                        <div style={{ width: '100%', maxWidth: '600px' }}>
                            <IntentPieChart results={filteredResults || results} />
                        </div>
                    </div>


                    <div style={{ margin: '3rem auto 1rem', padding: '0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0 }}>Message Feed</h2>
                        <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                            Showing {filteredResults ? filteredResults.length : 0} / {results.length} messages
                        </span>
                    </div>

                    <FilterBar 
                        filters={filters} 
                        onFilterChange={setFilters} 
                        availableIntents={availableIntents} 
                    />

                    <ResultsSection 
                        results={filteredResults} 
                        scrollToIndex={scrollToIndex} 
                        onScrollComplete={() => setScrollToIndex(null)}
                    />
                </div>
            )}
        </>
    );
}
