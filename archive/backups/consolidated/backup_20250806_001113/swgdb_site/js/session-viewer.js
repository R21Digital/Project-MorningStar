/**
 * Session Viewer JavaScript
 * Enhanced functionality for the SWGDB session viewer
 */

class SessionViewer {
    constructor() {
        this.sessions = [];
        this.filteredSessions = [];
        this.currentPage = 1;
        this.itemsPerPage = 12;
        this.charts = {};
        this.loading = false;
        this.filters = {
            character: '',
            planet: '',
            profession: '',
            startDate: '',
            endDate: ''
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadSessions();
    }
    
    bindEvents() {
        // Filter events
        document.addEventListener('change', (e) => {
            if (e.target.matches('#character-filter, #planet-filter, #profession-filter, #date-filter')) {
                this.applyFilters();
            }
        });
        
        // Button events
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn')) {
                this.handleButtonClick(e);
            }
        });
    }
    
    async loadSessions() {
        this.setLoading(true);
        
        try {
            const response = await fetch('/api/get_sessions_by_user.py', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.sessions = data.sessions || [];
                this.applyFilters();
                this.updateStatistics();
                this.updateCharts();
            } else {
                this.showError('Failed to load sessions');
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
            this.showError('Error loading sessions');
        } finally {
            this.setLoading(false);
        }
    }
    
    applyFilters() {
        this.filteredSessions = this.sessions.filter(session => {
            // Character filter
            if (this.filters.character && session.character_name !== this.filters.character) {
                return false;
            }
            
            // Planet filter
            if (this.filters.planet) {
                const hasPlanet = session.location_data?.location_events?.some(
                    location => location.planet === this.filters.planet
                );
                if (!hasPlanet) return false;
            }
            
            // Profession filter
            if (this.filters.profession) {
                const hasProfession = session.xp_data?.profession_breakdown && 
                    session.xp_data.profession_breakdown[this.filters.profession];
                if (!hasProfession) return false;
            }
            
            // Date filter
            if (this.filters.startDate || this.filters.endDate) {
                const sessionDate = new Date(session.start_time);
                if (this.filters.startDate && sessionDate < new Date(this.filters.startDate)) {
                    return false;
                }
                if (this.filters.endDate && sessionDate > new Date(this.filters.endDate)) {
                    return false;
                }
            }
            
            return true;
        });
        
        this.currentPage = 1;
        this.updateStatistics();
        this.updateCharts();
        this.renderSessions();
    }
    
    clearFilters() {
        this.filters = {
            character: '',
            planet: '',
            profession: '',
            startDate: '',
            endDate: ''
        };
        
        // Reset form inputs
        document.getElementById('character-filter').value = '';
        document.getElementById('planet-filter').value = '';
        document.getElementById('profession-filter').value = '';
        document.getElementById('date-filter').value = '';
        
        this.applyFilters();
    }
    
    updateStatistics() {
        const stats = this.calculateStatistics();
        this.renderStatistics(stats);
    }
    
    calculateStatistics() {
        if (this.filteredSessions.length === 0) {
            return {
                xpGained: 0,
                creditsGained: 0,
                questsCompleted: 0,
                totalTime: 0,
                stuckEvents: 0
            };
        }
        
        return this.filteredSessions.reduce((stats, session) => {
            stats.xpGained += session.xp_data?.total_xp_gained || 0;
            stats.creditsGained += session.credit_data?.total_credits_gained || 0;
            stats.questsCompleted += session.quest_data?.total_quests_completed || 0;
            stats.totalTime += session.duration_minutes || 0;
            stats.stuckEvents += session.event_data?.stuck_events?.length || 0;
            return stats;
        }, {
            xpGained: 0,
            creditsGained: 0,
            questsCompleted: 0,
            totalTime: 0,
            stuckEvents: 0
        });
    }
    
    renderStatistics(stats) {
        const statElements = document.querySelectorAll('.stat-number');
        if (statElements.length >= 5) {
            statElements[0].textContent = this.formatNumber(stats.xpGained);
            statElements[1].textContent = this.formatNumber(stats.creditsGained);
            statElements[2].textContent = stats.questsCompleted;
            statElements[3].textContent = this.formatDuration(stats.totalTime);
            statElements[4].textContent = stats.stuckEvents;
        }
    }
    
    updateCharts() {
        this.$nextTick(() => {
            this.createXPChart();
            this.createCreditsChart();
            this.createQuestsChart();
            this.createDurationChart();
        });
    }
    
    createXPChart() {
        const ctx = document.getElementById('xpChart');
        if (!ctx) return;
        
        if (this.charts.xp) {
            this.charts.xp.destroy();
        }
        
        const professionData = {};
        this.filteredSessions.forEach(session => {
            Object.entries(session.xp_data?.profession_breakdown || {}).forEach(([prof, xp]) => {
                professionData[prof] = (professionData[prof] || 0) + xp;
            });
        });
        
        if (Object.keys(professionData).length === 0) {
            ctx.style.display = 'none';
            return;
        }
        
        ctx.style.display = 'block';
        this.charts.xp = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(professionData),
                datasets: [{
                    data: Object.values(professionData),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    createCreditsChart() {
        const ctx = document.getElementById('creditsChart');
        if (!ctx) return;
        
        if (this.charts.credits) {
            this.charts.credits.destroy();
        }
        
        const sourceData = {};
        this.filteredSessions.forEach(session => {
            Object.entries(session.credit_data?.credit_events || {}).forEach(([source, amount]) => {
                sourceData[source] = (sourceData[source] || 0) + amount;
            });
        });
        
        if (Object.keys(sourceData).length === 0) {
            ctx.style.display = 'none';
            return;
        }
        
        ctx.style.display = 'block';
        this.charts.credits = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(sourceData),
                datasets: [{
                    label: 'Credits',
                    data: Object.values(sourceData),
                    backgroundColor: '#36A2EB'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    createQuestsChart() {
        const ctx = document.getElementById('questsChart');
        if (!ctx) return;
        
        if (this.charts.quests) {
            this.charts.quests.destroy();
        }
        
        const planetData = {};
        this.filteredSessions.forEach(session => {
            session.quest_data?.quest_events?.forEach(quest => {
                const planet = quest.zone || 'Unknown';
                planetData[planet] = (planetData[planet] || 0) + 1;
            });
        });
        
        if (Object.keys(planetData).length === 0) {
            ctx.style.display = 'none';
            return;
        }
        
        ctx.style.display = 'block';
        this.charts.quests = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(planetData),
                datasets: [{
                    data: Object.values(planetData),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    createDurationChart() {
        const ctx = document.getElementById('durationChart');
        if (!ctx) return;
        
        if (this.charts.duration) {
            this.charts.duration.destroy();
        }
        
        const durations = this.filteredSessions.map(s => s.duration_minutes);
        const bins = [0, 30, 60, 90, 120, 150, 180, 210, 240];
        const histogram = new Array(bins.length - 1).fill(0);
        
        durations.forEach(duration => {
            for (let i = 0; i < bins.length - 1; i++) {
                if (duration >= bins[i] && duration < bins[i + 1]) {
                    histogram[i]++;
                    break;
                }
            }
        });
        
        const labels = bins.slice(0, -1).map((bin, i) => 
            `${bin}-${bins[i + 1]} min`
        );
        
        this.charts.duration = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sessions',
                    data: histogram,
                    backgroundColor: '#4BC0C0'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    renderSessions() {
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        const paginatedSessions = this.filteredSessions.slice(start, end);
        
        const sessionsGrid = document.querySelector('.sessions-grid');
        if (!sessionsGrid) return;
        
        if (this.filteredSessions.length === 0) {
            sessionsGrid.innerHTML = `
                <div class="no-sessions">
                    <p>No sessions found matching your filters.</p>
                    <button class="btn btn-primary" onclick="sessionViewer.clearFilters()">Clear Filters</button>
                </div>
            `;
            return;
        }
        
        sessionsGrid.innerHTML = paginatedSessions.map(session => 
            this.createSessionCard(session)
        ).join('');
        
        this.updatePagination();
    }
    
    createSessionCard(session) {
        const hasStuckEvents = session.event_data?.stuck_events?.length > 0;
        const hasAlerts = session.event_data?.communication_events?.length > 0;
        
        return `
            <div class="session-card ${hasAlerts ? 'has-alerts' : ''} ${hasStuckEvents ? 'has-stuck' : ''}">
                <div class="session-header">
                    <div class="session-id">
                        <h3>${session.session_id}</h3>
                        <span class="character-name">${session.character_name}</span>
                    </div>
                    <div class="session-status">
                        <span class="status-indicator ${this.getStatusClass(session)}"></span>
                        <span class="status-text">${this.getStatusText(session)}</span>
                    </div>
                </div>
                
                <div class="session-metrics">
                    <div class="metric-item">
                        <div class="metric-icon">⏱️</div>
                        <div class="metric-content">
                            <span class="metric-label">Duration</span>
                            <span class="metric-value">${this.formatDuration(session.duration_minutes)}</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-icon">⭐</div>
                        <div class="metric-content">
                            <span class="metric-label">XP Gained</span>
                            <span class="metric-value">${this.formatNumber(session.xp_data?.total_xp_gained || 0)}</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-icon">💰</div>
                        <div class="metric-content">
                            <span class="metric-label">Credits</span>
                            <span class="metric-value">${this.formatNumber(session.credit_data?.total_credits_gained || 0)}</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-icon">📋</div>
                        <div class="metric-content">
                            <span class="metric-label">Quests</span>
                            <span class="metric-value">${session.quest_data?.total_quests_completed || 0}</span>
                        </div>
                    </div>
                </div>
                
                <div class="session-actions">
                    <button class="btn btn-primary btn-sm" onclick="sessionViewer.viewSessionDetails('${session.session_id}')">
                        <span class="btn-icon">👁️</span>
                        View Details
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="sessionViewer.downloadSession('${session.session_id}')">
                        <span class="btn-icon">📥</span>
                        Download
                    </button>
                    <button class="btn btn-outline btn-sm" onclick="sessionViewer.exportSessionPDF('${session.session_id}')">
                        <span class="btn-icon">📄</span>
                        PDF
                    </button>
                </div>
            </div>
        `;
    }
    
    getStatusClass(session) {
        if (session.event_data?.stuck_events?.length > 0) return 'status-warning';
        if (session.event_data?.communication_events?.length > 0) return 'status-info';
        return 'status-success';
    }
    
    getStatusText(session) {
        if (session.event_data?.stuck_events?.length > 0) return 'Issues Detected';
        if (session.event_data?.communication_events?.length > 0) return 'Alerts';
        return 'Normal';
    }
    
    updatePagination() {
        const totalPages = Math.ceil(this.filteredSessions.length / this.itemsPerPage);
        const pagination = document.querySelector('.pagination');
        
        if (!pagination) return;
        
        if (totalPages <= 1) {
            pagination.style.display = 'none';
            return;
        }
        
        pagination.style.display = 'flex';
        pagination.innerHTML = `
            <button class="btn btn-secondary" ${this.currentPage === 1 ? 'disabled' : ''} onclick="sessionViewer.previousPage()">
                Previous
            </button>
            <span class="page-info">
                Page ${this.currentPage} of ${totalPages}
            </span>
            <button class="btn btn-secondary" ${this.currentPage === totalPages ? 'disabled' : ''} onclick="sessionViewer.nextPage()">
                Next
            </button>
        `;
    }
    
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.renderSessions();
        }
    }
    
    nextPage() {
        const totalPages = Math.ceil(this.filteredSessions.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.renderSessions();
        }
    }
    
    async viewSessionDetails(sessionId) {
        try {
            const response = await fetch(`/api/get_sessions_by_user.py/session/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showSessionModal(data.session);
            } else {
                this.showError('Failed to load session details');
            }
        } catch (error) {
            console.error('Error loading session details:', error);
            this.showError('Error loading session details');
        }
    }
    
    showSessionModal(session) {
        // Implementation for showing session details modal
        console.log('Showing session details:', session);
    }
    
    downloadSession(sessionId) {
        const session = this.sessions.find(s => s.session_id === sessionId);
        if (!session) return;
        
        const dataStr = JSON.stringify(session, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${sessionId}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }
    
    async exportSessionPDF(sessionId) {
        const session = this.sessions.find(s => s.session_id === sessionId);
        if (!session) return;
        
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Add title
        doc.setFontSize(20);
        doc.text('Session Report', 20, 20);
        
        // Add session details
        doc.setFontSize(12);
        doc.text(`Session ID: ${session.session_id}`, 20, 40);
        doc.text(`Character: ${session.character_name}`, 20, 50);
        doc.text(`Duration: ${this.formatDuration(session.duration_minutes)}`, 20, 60);
        doc.text(`XP Gained: ${this.formatNumber(session.xp_data?.total_xp_gained || 0)}`, 20, 70);
        doc.text(`Credits Gained: ${this.formatNumber(session.credit_data?.total_credits_gained || 0)}`, 20, 80);
        
        // Add quests table
        if (session.quest_data?.quest_events?.length > 0) {
            doc.text('Quests Completed:', 20, 100);
            const questData = session.quest_data.quest_events.map(q => [
                q.quest_name,
                this.formatDateTime(q.timestamp),
                q.zone || 'N/A'
            ]);
            doc.autoTable({
                startY: 105,
                head: [['Quest', 'Time', 'Zone']],
                body: questData
            });
        }
        
        doc.save(`${sessionId}_report.pdf`);
    }
    
    exportAllSessions() {
        const dataStr = JSON.stringify(this.filteredSessions, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `all_sessions_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }
    
    handleButtonClick(e) {
        const button = e.target.closest('.btn');
        if (!button) return;
        
        const action = button.textContent.trim();
        
        switch (action) {
            case 'Clear Filters':
                this.clearFilters();
                break;
            case 'Refresh':
                this.loadSessions();
                break;
            case 'Export All':
                this.exportAllSessions();
                break;
            case 'Generate Report':
                this.generateReport();
                break;
        }
    }
    
    async generateReport() {
        // Implementation for generating comprehensive report
        console.log('Generating report...');
    }
    
    setLoading(loading) {
        this.loading = loading;
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.style.display = loading ? 'flex' : 'none';
        }
    }
    
    showError(message) {
        // Implementation for showing error messages
        console.error(message);
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
    
    formatDuration(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);
        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins}m`;
    }
    
    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString();
    }
    
    getAuthToken() {
        return localStorage.getItem('swgdb_auth_token') || '';
    }
    
    $nextTick(callback) {
        setTimeout(callback, 0);
    }
}

// Initialize the session viewer
const sessionViewer = new SessionViewer(); 