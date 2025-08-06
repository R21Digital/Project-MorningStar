// Item Log JavaScript Functionality

class ItemLogManager {
    constructor() {
        this.items = [];
        this.filteredItems = [];
        this.currentPage = 1;
        this.itemsPerPage = 50;
        this.charts = {};
        
        this.initializeEventListeners();
        this.loadData();
    }
    
    initializeEventListeners() {
        // Search and filter controls
        document.getElementById('searchBtn').addEventListener('click', () => this.performSearch());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetFilters());
        
        // Sort and pagination controls
        document.getElementById('sortBy').addEventListener('change', () => this.sortItems());
        document.getElementById('itemsPerPage').addEventListener('change', () => {
            this.itemsPerPage = parseInt(document.getElementById('itemsPerPage').value);
            this.currentPage = 1;
            this.renderItems();
        });
        
        // Pagination buttons
        document.getElementById('prevPage').addEventListener('click', () => this.previousPage());
        document.getElementById('nextPage').addEventListener('click', () => this.nextPage());
        
        // Modal close buttons
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => this.closeModal(closeBtn.closest('.modal')));
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal')) {
                this.closeModal(event.target);
            }
        });
        
        // Enter key for search
        document.getElementById('itemSearch').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
    }
    
    async loadData() {
        try {
            // Simulate loading data from API
            this.items = await this.fetchItemData();
            this.filteredItems = [...this.items];
            this.updateStatistics();
            this.renderItems();
            this.initializeCharts();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showMessage('Error loading data. Please try again.', 'error');
        }
    }
    
    async fetchItemData() {
        // Simulate API call - in real implementation, this would fetch from backend
        return [
            {
                item_id: 'item_001',
                item_name: 'Enhanced Composite Chest',
                category: 'armor',
                cost: 75000,
                vendor_id: 'vendor_001',
                vendor_name: 'Corellian Armor Smith',
                vendor_type: 'armorsmith',
                planet: 'Corellia',
                location: 'Coronet City',
                coordinates: [0.0, 0.0],
                timestamp: '2024-01-15T10:30:00',
                quality: 'Exceptional',
                stats: { constitution: 25, stamina: 20 },
                resists: { energy: 30, kinetic: 25 }
            },
            {
                item_id: 'item_002',
                item_name: 'Krayt Dragon Bone Sword',
                category: 'weapons',
                cost: 150000,
                vendor_id: 'vendor_002',
                vendor_name: 'Tatooine Weaponsmith',
                vendor_type: 'weaponsmith',
                planet: 'Tatooine',
                location: 'Mos Eisley',
                coordinates: [0.0, 0.0],
                timestamp: '2024-01-15T11:45:00',
                quality: 'Mastercraft',
                stats: { damage: 150, speed: 2.5 },
                resists: {}
            },
            {
                item_id: 'item_003',
                item_name: 'Stun Resist Enhancement',
                category: 'enhancements',
                cost: 25000,
                vendor_id: 'vendor_003',
                vendor_name: 'Naboo Merchant',
                vendor_type: 'merchant',
                planet: 'Naboo',
                location: 'Theed',
                coordinates: [0.0, 0.0],
                timestamp: '2024-01-15T12:15:00',
                quality: 'Good',
                stats: {},
                resists: { stun: 50 }
            }
        ];
    }
    
    performSearch() {
        const itemName = document.getElementById('itemSearch').value.toLowerCase();
        const vendorType = document.getElementById('vendorType').value.toLowerCase();
        const planet = document.getElementById('planetFilter').value.toLowerCase();
        const category = document.getElementById('categoryFilter').value.toLowerCase();
        const minCost = parseInt(document.getElementById('minCost').value) || 0;
        const maxCost = parseInt(document.getElementById('maxCost').value) || Infinity;
        
        this.filteredItems = this.items.filter(item => {
            const matchesName = !itemName || item.item_name.toLowerCase().includes(itemName);
            const matchesVendorType = !vendorType || item.vendor_type === vendorType;
            const matchesPlanet = !planet || item.planet.toLowerCase() === planet;
            const matchesCategory = !category || item.category === category;
            const matchesMinCost = item.cost >= minCost;
            const matchesMaxCost = item.cost <= maxCost;
            
            return matchesName && matchesVendorType && matchesPlanet && 
                   matchesCategory && matchesMinCost && matchesMaxCost;
        });
        
        this.currentPage = 1;
        this.renderItems();
        this.updateStatistics();
    }
    
    resetFilters() {
        document.getElementById('itemSearch').value = '';
        document.getElementById('vendorType').value = '';
        document.getElementById('planetFilter').value = '';
        document.getElementById('categoryFilter').value = '';
        document.getElementById('minCost').value = '';
        document.getElementById('maxCost').value = '';
        
        this.filteredItems = [...this.items];
        this.currentPage = 1;
        this.renderItems();
        this.updateStatistics();
    }
    
    sortItems() {
        const sortBy = document.getElementById('sortBy').value;
        
        this.filteredItems.sort((a, b) => {
            switch (sortBy) {
                case 'timestamp':
                    return new Date(b.timestamp) - new Date(a.timestamp);
                case 'cost':
                    return b.cost - a.cost;
                case 'name':
                    return a.item_name.localeCompare(b.item_name);
                case 'vendor':
                    return a.vendor_name.localeCompare(b.vendor_name);
                case 'planet':
                    return a.planet.localeCompare(b.planet);
                default:
                    return 0;
            }
        });
        
        this.renderItems();
    }
    
    renderItems() {
        const tbody = document.getElementById('itemsTableBody');
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageItems = this.filteredItems.slice(startIndex, endIndex);
        
        tbody.innerHTML = '';
        
        if (pageItems.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="empty-state">
                        <h3>No items found</h3>
                        <p>Try adjusting your search criteria</p>
                    </td>
                </tr>
            `;
        } else {
            pageItems.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="item-name">${this.escapeHtml(item.item_name)}</td>
                    <td>${this.capitalizeFirst(item.category)}</td>
                    <td class="item-cost">${this.formatCost(item.cost)}</td>
                    <td class="vendor-name">${this.escapeHtml(item.vendor_name)}</td>
                    <td><span class="vendor-type">${item.vendor_type}</span></td>
                    <td class="planet-name">${this.escapeHtml(item.planet)}</td>
                    <td class="location-name">${this.escapeHtml(item.location)}</td>
                    <td class="discovery-date">${this.formatDate(item.timestamp)}</td>
                    <td>
                        <button class="action-btn btn-view" onclick="itemLogManager.viewItem('${item.item_id}')">View</button>
                        <button class="action-btn btn-details" onclick="itemLogManager.viewVendor('${item.vendor_id}')">Vendor</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
        
        this.updatePagination();
    }
    
    updatePagination() {
        const totalPages = Math.ceil(this.filteredItems.length / this.itemsPerPage);
        const pageInfo = document.getElementById('pageInfo');
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        
        pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === totalPages;
        
        prevBtn.style.opacity = prevBtn.disabled ? '0.5' : '1';
        nextBtn.style.opacity = nextBtn.disabled ? '0.5' : '1';
    }
    
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.renderItems();
        }
    }
    
    nextPage() {
        const totalPages = Math.ceil(this.filteredItems.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.renderItems();
        }
    }
    
    updateStatistics() {
        const totalItems = this.filteredItems.length;
        const totalValue = this.filteredItems.reduce((sum, item) => sum + item.cost, 0);
        const recentCutoff = new Date(Date.now() - 24 * 60 * 60 * 1000); // 24 hours ago
        const recentDiscoveries = this.filteredItems.filter(item => 
            new Date(item.timestamp) > recentCutoff
        ).length;
        
        // Count unique vendors
        const uniqueVendors = new Set(this.filteredItems.map(item => item.vendor_id)).size;
        
        document.getElementById('totalItems').textContent = totalItems.toLocaleString();
        document.getElementById('totalVendors').textContent = uniqueVendors.toLocaleString();
        document.getElementById('totalValue').textContent = this.formatCost(totalValue);
        document.getElementById('recentDiscoveries').textContent = recentDiscoveries.toLocaleString();
    }
    
    initializeCharts() {
        this.createCategoryChart();
        this.createVendorTypeChart();
        this.createPlanetChart();
        this.createCostChart();
    }
    
    createCategoryChart() {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const categoryData = this.getCategoryData();
        
        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: categoryData.labels,
                datasets: [{
                    data: categoryData.values,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
                        '#4BC0C0', '#FF6384', '#36A2EB'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    createVendorTypeChart() {
        const ctx = document.getElementById('vendorTypeChart').getContext('2d');
        const vendorData = this.getVendorTypeData();
        
        this.charts.vendorType = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: vendorData.labels,
                datasets: [{
                    label: 'Vendors',
                    data: vendorData.values,
                    backgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    createPlanetChart() {
        const ctx = document.getElementById('planetChart').getContext('2d');
        const planetData = this.getPlanetData();
        
        this.charts.planet = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: planetData.labels,
                datasets: [{
                    data: planetData.values,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
                        '#4BC0C0'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    createCostChart() {
        const ctx = document.getElementById('costChart').getContext('2d');
        const costData = this.getCostDistribution();
        
        this.charts.cost = new Chart(ctx, {
            type: 'line',
            data: {
                labels: costData.labels,
                datasets: [{
                    label: 'Items',
                    data: costData.values,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    getCategoryData() {
        const categories = {};
        this.filteredItems.forEach(item => {
            categories[item.category] = (categories[item.category] || 0) + 1;
        });
        
        return {
            labels: Object.keys(categories).map(cat => this.capitalizeFirst(cat)),
            values: Object.values(categories)
        };
    }
    
    getVendorTypeData() {
        const vendorTypes = {};
        this.filteredItems.forEach(item => {
            vendorTypes[item.vendor_type] = (vendorTypes[item.vendor_type] || 0) + 1;
        });
        
        return {
            labels: Object.keys(vendorTypes).map(type => this.capitalizeFirst(type)),
            values: Object.values(vendorTypes)
        };
    }
    
    getPlanetData() {
        const planets = {};
        this.filteredItems.forEach(item => {
            planets[item.planet] = (planets[item.planet] || 0) + 1;
        });
        
        return {
            labels: Object.keys(planets),
            values: Object.values(planets)
        };
    }
    
    getCostDistribution() {
        const costRanges = [
            { min: 0, max: 1000, label: '0-1k' },
            { min: 1000, max: 5000, label: '1k-5k' },
            { min: 5000, max: 10000, label: '5k-10k' },
            { min: 10000, max: 25000, label: '10k-25k' },
            { min: 25000, max: 50000, label: '25k-50k' },
            { min: 50000, max: 100000, label: '50k-100k' },
            { min: 100000, max: Infinity, label: '100k+' }
        ];
        
        const distribution = costRanges.map(range => {
            const count = this.filteredItems.filter(item => 
                item.cost >= range.min && item.cost < range.max
            ).length;
            return { label: range.label, count };
        });
        
        return {
            labels: distribution.map(d => d.label),
            values: distribution.map(d => d.count)
        };
    }
    
    viewItem(itemId) {
        const item = this.items.find(i => i.item_id === itemId);
        if (!item) return;
        
        const modal = document.getElementById('itemModal');
        const title = document.getElementById('itemModalTitle');
        const content = document.getElementById('itemModalContent');
        
        title.textContent = item.item_name;
        content.innerHTML = this.generateItemDetails(item);
        
        modal.style.display = 'block';
    }
    
    viewVendor(vendorId) {
        const vendorItems = this.items.filter(item => item.vendor_id === vendorId);
        if (vendorItems.length === 0) return;
        
        const vendor = vendorItems[0];
        const modal = document.getElementById('vendorModal');
        const title = document.getElementById('vendorModalTitle');
        const content = document.getElementById('vendorModalContent');
        
        title.textContent = vendor.vendor_name;
        content.innerHTML = this.generateVendorDetails(vendor, vendorItems);
        
        modal.style.display = 'block';
    }
    
    generateItemDetails(item) {
        const statsHtml = item.stats ? Object.entries(item.stats)
            .map(([key, value]) => `<div class="detail-row">
                <span class="detail-label">${this.capitalizeFirst(key)}:</span>
                <span class="detail-value">${value}</span>
            </div>`).join('') : '';
        
        const resistsHtml = item.resists ? Object.entries(item.resists)
            .map(([key, value]) => `<div class="detail-row">
                <span class="detail-label">${this.capitalizeFirst(key)} Resist:</span>
                <span class="detail-value">${value}</span>
            </div>`).join('') : '';
        
        return `
            <div class="modal-details">
                <div class="detail-row">
                    <span class="detail-label">Item Name:</span>
                    <span class="detail-value">${this.escapeHtml(item.item_name)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Category:</span>
                    <span class="detail-value">${this.capitalizeFirst(item.category)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Cost:</span>
                    <span class="detail-value">${this.formatCost(item.cost)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Quality:</span>
                    <span class="detail-value">${item.quality || 'Standard'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Vendor:</span>
                    <span class="detail-value">${this.escapeHtml(item.vendor_name)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Vendor Type:</span>
                    <span class="detail-value">${this.capitalizeFirst(item.vendor_type)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location:</span>
                    <span class="detail-value">${this.escapeHtml(item.location)}, ${this.escapeHtml(item.planet)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Discovered:</span>
                    <span class="detail-value">${this.formatDate(item.timestamp)}</span>
                </div>
                ${statsHtml}
                ${resistsHtml}
            </div>
        `;
    }
    
    generateVendorDetails(vendor, vendorItems) {
        const totalValue = vendorItems.reduce((sum, item) => sum + item.cost, 0);
        const avgCost = totalValue / vendorItems.length;
        const mostExpensive = vendorItems.reduce((max, item) => 
            item.cost > max.cost ? item : max
        );
        
        return `
            <div class="modal-details">
                <div class="detail-row">
                    <span class="detail-label">Vendor Name:</span>
                    <span class="detail-value">${this.escapeHtml(vendor.vendor_name)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Vendor Type:</span>
                    <span class="detail-value">${this.capitalizeFirst(vendor.vendor_type)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location:</span>
                    <span class="detail-value">${this.escapeHtml(vendor.location)}, ${this.escapeHtml(vendor.planet)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Items Available:</span>
                    <span class="detail-value">${vendorItems.length}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Total Value:</span>
                    <span class="detail-value">${this.formatCost(totalValue)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Average Cost:</span>
                    <span class="detail-value">${this.formatCost(avgCost)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Most Expensive:</span>
                    <span class="detail-value">${this.escapeHtml(mostExpensive.item_name)} (${this.formatCost(mostExpensive.cost)})</span>
                </div>
            </div>
        `;
    }
    
    closeModal(modal) {
        modal.style.display = 'none';
    }
    
    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        document.querySelector('.container').insertBefore(messageDiv, document.querySelector('.search-section'));
        
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
    
    // Utility functions
    formatCost(cost) {
        return cost.toLocaleString() + ' credits';
    }
    
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString() + ' ' + 
               new Date(dateString).toLocaleTimeString();
    }
    
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the item log manager when the page loads
let itemLogManager;
document.addEventListener('DOMContentLoaded', () => {
    itemLogManager = new ItemLogManager();
}); 