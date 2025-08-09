/**
 * Session Card JavaScript
 * Enhanced functionality for individual session cards
 */

class SessionCard {
    constructor(session) {
        this.session = session;
        this.element = null;
        this.init();
    }
    
    init() {
        this.createElement();
        this.bindEvents();
    }
    
    createElement() {
        const template = `
            <div class="session-card ${this.getCardClasses()}">
                ${this.renderHeader()}
                ${this.renderMetrics()}
                ${this.renderDetails()}
                ${this.renderAlerts()}
                ${this.renderQuests()}
                ${this.renderLocations()}
                ${this.renderPerformance()}
                ${this.renderActions()}
                ${this.renderTags()}
            </div>
        `;
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = template;
        this.element = tempDiv.firstElementChild;
    }
    
    getCardClasses() {
        const classes = [];
        if (this.hasStuckEvents()) classes.push('has-stuck');
        if (this.hasAlerts()) classes.push('has-alerts');
        return classes.join(' ');
    }
    
    renderHeader() {
        return `
            <div class="session-header">
                <div class="session-id">
                    <h3>${this.session.session_id}</h3>
                    <span class="character-name">${this.session.character_name}</span>
                </div>
                <div class="session-status">
                    <span class="status-indicator ${this.getStatusClass()}"></span>
                    <span class="status-text">${this.getStatusText()}</span>
                </div>
            </div>
        `;
    }
    
    renderMetrics() {
        return `
            <div class="session-metrics">
                <div class="metric-item">
                    <div class="metric-icon">⏱️</div>
                    <div class="metric-content">
                        <span class="metric-label">Duration</span>
                        <span class="metric-value">${this.formatDuration(this.session.duration_minutes)}</span>
                    </div>
                </div>
                
                <div class="metric-item">
                    <div class="metric-icon">⭐</div>
                    <div class="metric-content">
                        <span class="metric-label">XP Gained</span>
                        <span class="metric-value">${this.formatNumber(this.session.xp_data?.total_xp_gained || 0)}</span>
                    </div>
                </div>
                
                <div class="metric-item">
                    <div class="metric-icon">💰</div>
                    <div class="metric-content">
                        <span class="metric-label">Credits</span>
                        <span class="metric-value">${this.formatNumber(this.session.credit_data?.total_credits_gained || 0)}</span>
                    </div>
                </div>
                
                <div class="metric-item">
                    <div class="metric-icon">📋</div>
                    <div class="metric-content">
                        <span class="metric-label">Quests</span>
                        <span class="metric-value">${this.session.quest_data?.total_quests_completed || 0}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderDetails() {
        return `
            <div class="session-details">
                <div class="detail-row">
                    <span class="detail-label">Start Time:</span>
                    <span class="detail-value">${this.formatDateTime(this.session.start_time)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">End Time:</span>
                    <span class="detail-value">${this.formatDateTime(this.session.end_time)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Locations:</span>
                    <span class="detail-value">${this.session.location_data?.total_locations_visited || 0}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Events:</span>
                    <span class="detail-value">${this.session.event_data?.total_events || 0}</span>
                </div>
            </div>
        `;
    }
    
    renderAlerts() {
        if (!this.hasAlerts() && !this.hasStuckEvents()) {
            return '';
        }
        
        return `
            <div class="session-alerts">
                ${this.renderStuckEvents()}
                ${this.renderCommunicationAlerts()}
            </div>
        `;
    }
    
    renderStuckEvents() {
        const stuckEvents = this.session.event_data?.stuck_events || [];
        if (stuckEvents.length === 0) return '';
        
        return `
            <div class="alert-section">
                <div class="alert-header">
                    <span class="alert-icon">⚠️</span>
                    <span class="alert-title">Stuck Events</span>
                    <span class="alert-count">${stuckEvents.length}</span>
                </div>
                <div class="alert-items">
                    ${stuckEvents.slice(0, 2).map(event => `
                        <div class="alert-item">
                            <span class="alert-location">${event.location}</span>
                            <span class="alert-duration">${this.formatDuration(event.duration_seconds / 60)}</span>
                        </div>
                    `).join('')}
                    ${stuckEvents.length > 2 ? `
                        <div class="alert-more">
                            +${stuckEvents.length - 2} more
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderCommunicationAlerts() {
        const commEvents = this.session.event_data?.communication_events || [];
        if (commEvents.length === 0) return '';
        
        return `
            <div class="alert-section">
                <div class="alert-header">
                    <span class="alert-icon">📢</span>
                    <span class="alert-title">Communication Alerts</span>
                    <span class="alert-count">${commEvents.length}</span>
                </div>
                <div class="alert-items">
                    ${commEvents.slice(0, 2).map(event => `
                        <div class="alert-item">
                            <span class="alert-type">${event.event_type}</span>
                            <span class="alert-sender">${event.sender}</span>
                        </div>
                    `).join('')}
                    ${commEvents.length > 2 ? `
                        <div class="alert-more">
                            +${commEvents.length - 2} more
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderQuests() {
        const quests = this.session.quest_data?.quest_events || [];
        if (quests.length === 0) return '';
        
        return `
            <div class="session-quests">
                <div class="quests-header">
                    <span class="quests-icon">📋</span>
                    <span class="quests-title">Recent Quests</span>
                </div>
                <div class="quests-list">
                    ${quests.slice(0, 3).map(quest => `
                        <div class="quest-item">
                            <span class="quest-name">${quest.quest_name}</span>
                            ${quest.zone ? `<span class="quest-zone">${quest.zone}</span>` : ''}
                        </div>
                    `).join('')}
                    ${quests.length > 3 ? `
                        <div class="quests-more">
                            +${quests.length - 3} more quests
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderLocations() {
        const locations = this.session.location_data?.location_events || [];
        if (locations.length === 0) return '';
        
        return `
            <div class="session-locations">
                <div class="locations-header">
                    <span class="locations-icon">🗺️</span>
                    <span class="locations-title">Locations Visited</span>
                </div>
                <div class="locations-list">
                    ${locations.slice(0, 3).map(location => `
                        <div class="location-item">
                            <span class="location-name">${location.city}, ${location.planet}</span>
                            ${location.duration_minutes ? `
                                <span class="location-duration">${this.formatDuration(location.duration_minutes)}</span>
                            ` : ''}
                        </div>
                    `).join('')}
                    ${locations.length > 3 ? `
                        <div class="locations-more">
                            +${locations.length - 3} more locations
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderPerformance() {
        const xpPerHour = this.calculateXPPerHour();
        const creditsPerHour = this.calculateCreditsPerHour();
        const questsPerHour = this.calculateQuestsPerHour();
        
        return `
            <div class="session-performance">
                <div class="performance-indicators">
                    <div class="indicator ${xpPerHour > 1000 ? 'good' : 'warning'}">
                        <span class="indicator-label">XP/Hour</span>
                        <span class="indicator-value">${Math.round(xpPerHour)}</span>
                    </div>
                    <div class="indicator ${creditsPerHour > 5000 ? 'good' : 'warning'}">
                        <span class="indicator-label">Credits/Hour</span>
                        <span class="indicator-value">${Math.round(creditsPerHour)}</span>
                    </div>
                    <div class="indicator ${questsPerHour > 2 ? 'good' : 'warning'}">
                        <span class="indicator-label">Quests/Hour</span>
                        <span class="indicator-value">${questsPerHour.toFixed(1)}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderActions() {
        return `
            <div class="session-actions">
                <button class="btn btn-primary btn-sm" onclick="sessionCard.viewDetails('${this.session.session_id}')">
                    <span class="btn-icon">👁️</span>
                    View Details
                </button>
                <button class="btn btn-secondary btn-sm" onclick="sessionCard.download('${this.session.session_id}')">
                    <span class="btn-icon">📥</span>
                    Download
                </button>
                <button class="btn btn-outline btn-sm" onclick="sessionCard.exportPDF('${this.session.session_id}')">
                    <span class="btn-icon">📄</span>
                    PDF
                </button>
            </div>
        `;
    }
    
    renderTags() {
        const tags = [];
        tags.push(`<span class="tag tag-character">${this.session.character_name}</span>`);
        tags.push(`<span class="tag tag-duration">${this.formatDuration(this.session.duration_minutes)}</span>`);
        
        if (this.hasStuckEvents()) {
            tags.push('<span class="tag tag-warning">Stuck Events</span>');
        }
        
        if (this.hasAlerts()) {
            tags.push('<span class="tag tag-alert">Alerts</span>');
        }
        
        if (this.session.quest_data?.total_quests_completed > 5) {
            tags.push('<span class="tag tag-success">High Activity</span>');
        }
        
        return `
            <div class="session-tags">
                ${tags.join('')}
            </div>
        `;
    }
    
    bindEvents() {
        // Add event listeners for interactive elements
        const buttons = this.element.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleButtonClick(button);
            });
        });
    }
    
    handleButtonClick(button) {
        const action = button.textContent.trim();
        const sessionId = this.session.session_id;
        
        switch (action) {
            case 'View Details':
                this.viewDetails(sessionId);
                break;
            case 'Download':
                this.download(sessionId);
                break;
            case 'PDF':
                this.exportPDF(sessionId);
                break;
        }
    }
    
    viewDetails(sessionId) {
        // Emit custom event for parent component
        const event = new CustomEvent('sessionView', {
            detail: { sessionId, session: this.session }
        });
        document.dispatchEvent(event);
    }
    
    download(sessionId) {
        const dataStr = JSON.stringify(this.session, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${sessionId}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }
    
    async exportPDF(sessionId) {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Add session title
        doc.setFontSize(18);
        doc.text(`Session Report: ${sessionId}`, 20, 20);
        
        // Add basic info
        doc.setFontSize(12);
        doc.text(`Character: ${this.session.character_name}`, 20, 40);
        doc.text(`Duration: ${this.formatDuration(this.session.duration_minutes)}`, 20, 50);
        doc.text(`XP Gained: ${this.formatNumber(this.session.xp_data?.total_xp_gained || 0)}`, 20, 60);
        doc.text(`Credits Gained: ${this.formatNumber(this.session.credit_data?.total_credits_gained || 0)}`, 20, 70);
        doc.text(`Quests Completed: ${this.session.quest_data?.total_quests_completed || 0}`, 20, 80);
        
        // Add quests table
        if (this.session.quest_data?.quest_events?.length > 0) {
            doc.text('Quests Completed:', 20, 100);
            const questData = this.session.quest_data.quest_events.map(q => [
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
        
        doc.save(`${sessionId}_card.pdf`);
    }
    
    // Utility methods
    hasStuckEvents() {
        return this.session.event_data?.stuck_events?.length > 0;
    }
    
    hasAlerts() {
        return this.session.event_data?.communication_events?.length > 0;
    }
    
    getStatusClass() {
        if (this.hasStuckEvents()) return 'status-warning';
        if (this.hasAlerts()) return 'status-info';
        return 'status-success';
    }
    
    getStatusText() {
        if (this.hasStuckEvents()) return 'Issues Detected';
        if (this.hasAlerts()) return 'Alerts';
        return 'Normal';
    }
    
    calculateXPPerHour() {
        const hours = this.session.duration_minutes / 60;
        return hours > 0 ? (this.session.xp_data?.total_xp_gained || 0) / hours : 0;
    }
    
    calculateCreditsPerHour() {
        const hours = this.session.duration_minutes / 60;
        return hours > 0 ? (this.session.credit_data?.total_credits_gained || 0) / hours : 0;
    }
    
    calculateQuestsPerHour() {
        const hours = this.session.duration_minutes / 60;
        return hours > 0 ? (this.session.quest_data?.total_quests_completed || 0) / hours : 0;
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
    
    // Public methods
    getElement() {
        return this.element;
    }
    
    updateSession(newSession) {
        this.session = newSession;
        this.element.outerHTML = this.createElement().outerHTML;
        this.bindEvents();
    }
    
    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

// Global session card manager
window.sessionCard = {
    create: (session) => new SessionCard(session),
    viewDetails: (sessionId) => {
        // Implementation for viewing session details
        console.log('Viewing session details:', sessionId);
    },
    download: (sessionId) => {
        // Implementation for downloading session
        console.log('Downloading session:', sessionId);
    },
    exportPDF: (sessionId) => {
        // Implementation for exporting PDF
        console.log('Exporting PDF for session:', sessionId);
    }
}; 