module.exports = class {
  data() {
    return {
      title: "Gear Optimizer - SWGDB Tools",
      description: "Optimize your character's gear based on scanned stats and selected builds",
      layout: "base.11ty.js",
      permalink: "/tools/gear-optimizer/"
    };
  }

  render(data) {
    return `
    <style>
        .gear-hero {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(30, 41, 59, 0.8) 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
            border-radius: 12px;
            margin-bottom: 40px;
        }

        .gear-hero h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: #06b6d4;
            text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
        }

        .gear-hero p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
            color: #e2e8f0;
        }

        .optimization-form {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
            backdrop-filter: blur(10px);
        }

        .form-section {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
        }

        .form-section h3 {
            color: #06b6d4;
            margin-bottom: 20px;
            font-weight: 600;
            font-size: 1.3rem;
        }

        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #06b6d4;
        }

        .form-control {
            width: 100%;
            padding: 12px 15px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            border-radius: 8px;
            font-size: 16px;
            color: #e2e8f0;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: #06b6d4;
            box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
        }

        .btn-optimize {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.9) 0%, rgba(8, 145, 178, 0.9) 100%);
            color: white;
            border: 1px solid rgba(6, 182, 212, 0.6);
            padding: 15px 30px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .btn-optimize::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .btn-optimize:hover::before {
            left: 100%;
        }

        .btn-optimize:hover {
            background: linear-gradient(135deg, rgba(8, 145, 178, 0.9) 0%, rgba(6, 182, 212, 0.9) 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.4);
        }

        .results-section {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            border-radius: 12px;
            padding: 30px;
            margin-top: 30px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
            backdrop-filter: blur(10px);
        }

        .gear-item {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }

        .gear-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.3);
        }

        .gear-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .gear-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #06b6d4;
        }

        .gear-slot {
            background: rgba(6, 182, 212, 0.2);
            color: #06b6d4;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }

        .gear-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }

        .gear-stat {
            text-align: center;
            padding: 8px;
            background: rgba(6, 182, 212, 0.1);
            border-radius: 6px;
            border: 1px solid rgba(6, 182, 212, 0.2);
        }

        .gear-stat-value {
            font-size: 1.1rem;
            font-weight: bold;
            color: #06b6d4;
        }

        .gear-stat-label {
            font-size: 0.8rem;
            color: #e2e8f0;
            opacity: 0.8;
        }

        .gear-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .action-btn {
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
        }

        .btn-primary {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.9) 0%, rgba(8, 145, 178, 0.9) 100%);
            color: white;
            border: 1px solid rgba(6, 182, 212, 0.6);
        }

        .btn-primary:hover {
            background: linear-gradient(135deg, rgba(8, 145, 178, 0.9) 0%, rgba(6, 182, 212, 0.9) 100%);
            transform: translateY(-1px);
            box-shadow: 0 3px 10px rgba(6, 182, 212, 0.3);
        }

        .btn-secondary {
            background: linear-gradient(135deg, rgba(51, 65, 85, 0.9) 0%, rgba(30, 41, 59, 0.9) 100%);
            color: #e2e8f0;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }

        .btn-secondary:hover {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%);
            transform: translateY(-1px);
            box-shadow: 0 3px 10px rgba(6, 182, 212, 0.2);
        }

        .optimization-summary {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }

        .summary-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #06b6d4;
            margin-bottom: 15px;
        }

        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }

        .summary-stat {
            text-align: center;
            padding: 12px;
            background: rgba(6, 182, 212, 0.1);
            border-radius: 6px;
            border: 1px solid rgba(6, 182, 212, 0.2);
        }

        .summary-stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #06b6d4;
        }

        .summary-stat-label {
            font-size: 0.9rem;
            color: #e2e8f0;
            opacity: 0.8;
        }

        .loading-spinner {
            text-align: center;
            padding: 40px;
            color: #06b6d4;
        }

        .loading-spinner i {
            font-size: 2rem;
            animation: spin 2s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>

    <section class="py-12 px-6 max-w-6xl mx-auto text-white relative z-10">
        <!-- Hero Section -->
        <div class="gear-hero">
            <h1><i class="fas fa-cogs mr-4"></i>Gear Optimizer</h1>
            <p>Optimize your character's gear based on scanned stats and selected builds</p>
        </div>

        <!-- Optimization Form -->
        <div class="optimization-form">
            <div class="form-section">
                <h3><i class="fas fa-user mr-2"></i>Character Information</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="character-name">Character Name</label>
                        <input type="text" id="character-name" class="form-control" placeholder="Enter character name">
                    </div>
                    <div class="form-group">
                        <label for="character-level">Level</label>
                        <input type="number" id="character-level" class="form-control" min="1" max="90" placeholder="90">
                    </div>
                    <div class="form-group">
                        <label for="character-profession">Primary Profession</label>
                        <select id="character-profession" class="form-control">
                            <option value="">Select profession...</option>
                            <option value="rifleman">Rifleman</option>
                            <option value="pistoleer">Pistoleer</option>
                            <option value="swordsman">Swordsman</option>
                            <option value="medic">Combat Medic</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3><i class="fas fa-target mr-2"></i>Optimization Goals</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="optimization-focus">Primary Focus</label>
                        <select id="optimization-focus" class="form-control">
                            <option value="damage">Damage Output</option>
                            <option value="defense">Defense/Survival</option>
                            <option value="accuracy">Accuracy</option>
                            <option value="utility">Utility/Support</option>
                            <option value="balanced">Balanced</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="content-type">Content Type</label>
                        <select id="content-type" class="form-control">
                            <option value="pve">PvE</option>
                            <option value="pvp">PvP</option>
                            <option value="group">Group Content</option>
                            <option value="solo">Solo Content</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="budget">Budget Range</label>
                        <select id="budget" class="form-control">
                            <option value="low">Low Budget</option>
                            <option value="medium">Medium Budget</option>
                            <option value="high">High Budget</option>
                            <option value="unlimited">Unlimited</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="text-center">
                <button class="btn-optimize" onclick="optimizeGear()">
                    <i class="fas fa-magic mr-2"></i>Optimize Gear
                </button>
            </div>
        </div>

        <!-- Results Section -->
        <div class="results-section" id="results-section" style="display: none;">
            <h3 class="text-xl font-bold text-swg-cyan mb-4">Optimization Results</h3>
            
            <div class="optimization-summary">
                <div class="summary-title">Character Summary</div>
                <div class="summary-stats">
                    <div class="summary-stat">
                        <div class="summary-stat-value" id="total-damage">0</div>
                        <div class="summary-stat-label">Total Damage</div>
                    </div>
                    <div class="summary-stat">
                        <div class="summary-stat-value" id="total-defense">0</div>
                        <div class="summary-stat-label">Total Defense</div>
                    </div>
                    <div class="summary-stat">
                        <div class="summary-stat-value" id="total-accuracy">0</div>
                        <div class="summary-stat-label">Total Accuracy</div>
                    </div>
                    <div class="summary-stat">
                        <div class="summary-stat-value" id="total-utility">0</div>
                        <div class="summary-stat-label">Total Utility</div>
                    </div>
                </div>
            </div>

            <div id="gear-results">
                <!-- Gear items will be populated here -->
            </div>
        </div>
    </section>

    <script>
        function optimizeGear() {
            const characterName = document.getElementById('character-name').value;
            const characterLevel = document.getElementById('character-level').value;
            const profession = document.getElementById('character-profession').value;
            const focus = document.getElementById('optimization-focus').value;
            const contentType = document.getElementById('content-type').value;
            const budget = document.getElementById('budget').value;

            if (!characterName || !characterLevel || !profession) {
                alert('Please fill in all required character information.');
                return;
            }

            // Show loading
            document.getElementById('results-section').style.display = 'block';
            document.getElementById('gear-results').innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner"></i><p style="margin-top: 10px;">Optimizing gear...</p></div>';

            // Simulate optimization process
            setTimeout(() => {
                generateOptimizedGear(characterName, characterLevel, profession, focus, contentType, budget);
            }, 2000);
        }

        function generateOptimizedGear(name, level, profession, focus, contentType, budget) {
            const gearItems = [
                {
                    name: "Elite Combat Rifle",
                    slot: "Weapon",
                    stats: { damage: 95, accuracy: 88, defense: 0, utility: 0 }
                },
                {
                    name: "Reinforced Combat Armor",
                    slot: "Chest",
                    stats: { damage: 0, accuracy: 0, defense: 92, utility: 15 }
                },
                {
                    name: "Tactical Helmet",
                    slot: "Head",
                    stats: { damage: 0, accuracy: 85, defense: 78, utility: 0 }
                },
                {
                    name: "Combat Boots",
                    slot: "Feet",
                    stats: { damage: 0, accuracy: 0, defense: 75, utility: 25 }
                },
                {
                    name: "Utility Belt",
                    slot: "Waist",
                    stats: { damage: 0, accuracy: 0, defense: 0, utility: 90 }
                }
            ];

            let totalDamage = 0;
            let totalDefense = 0;
            let totalAccuracy = 0;
            let totalUtility = 0;

            const gearResults = gearItems.map(item => {
                totalDamage += item.stats.damage;
                totalDefense += item.stats.defense;
                totalAccuracy += item.stats.accuracy;
                totalUtility += item.stats.utility;

                return 
                    '<div class="gear-item">' +
                        '<div class="gear-header">' +
                            '<div class="gear-name">' + item.name + '</div>' +
                            '<div class="gear-slot">' + item.slot + '</div>' +
                        '</div>' +
                        '<div class="gear-stats">' +
                            '<div class="gear-stat">' +
                                '<div class="gear-stat-value">' + item.stats.damage + '</div>' +
                                '<div class="gear-stat-label">Damage</div>' +
                            '</div>' +
                            '<div class="gear-stat">' +
                                '<div class="gear-stat-value">' + item.stats.accuracy + '</div>' +
                                '<div class="gear-stat-label">Accuracy</div>' +
                            '</div>' +
                            '<div class="gear-stat">' +
                                '<div class="gear-stat-value">' + item.stats.defense + '</div>' +
                                '<div class="gear-stat-label">Defense</div>' +
                            '</div>' +
                            '<div class="gear-stat">' +
                                '<div class="gear-stat-value">' + item.stats.utility + '</div>' +
                                '<div class="gear-stat-label">Utility</div>' +
                            '</div>' +
                        '</div>' +
                        '<div class="gear-actions">' +
                            '<button class="action-btn btn-primary" onclick="viewItem(\'' + item.name + '\')">' +
                                '<i class="fas fa-eye"></i>View Details' +
                            '</button>' +
                            '<button class="action-btn btn-secondary" onclick="exportItem(\'' + item.name + '\')">' +
                                '<i class="fas fa-download"></i>Export' +
                            '</button>' +
                        '</div>' +
                    '</div>';
            }).join('');

            document.getElementById('gear-results').innerHTML = gearResults;
            document.getElementById('total-damage').textContent = totalDamage;
            document.getElementById('total-defense').textContent = totalDefense;
            document.getElementById('total-accuracy').textContent = totalAccuracy;
            document.getElementById('total-utility').textContent = totalUtility;
        }

        function viewItem(itemName) {
            alert('Viewing details for: ' + itemName + '\n\nThis would open a detailed view of the item.');
        }

        function exportItem(itemName) {
            const itemData = {
                name: itemName,
                timestamp: new Date().toISOString(),
                character: document.getElementById('character-name').value
            };
            
            const dataStr = JSON.stringify(itemData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'swg-gear-' + itemName.toLowerCase().replace(/\s+/g, '-') + '.json';
            link.click();
        }
    </script>
    `;
  }
};