module.exports = class {
  data() {
    return {
      title: "GCW Calculator - SWGDB Tools",
      description: "Galactic Civil War planet control calculator for Star Wars Galaxies Restoration - simulate faction dominance across the galaxy",
      layout: "base.11ty.js",
      permalink: "/tools/gcw-calculator/"
    };
  }

  render(data) {
    return `
    <style>
        .gcw-hero {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(30, 41, 59, 0.8) 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
            border-radius: 12px;
            margin-bottom: 40px;
        }

        .gcw-hero h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: #06b6d4;
            text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
        }

        .gcw-hero p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
            color: #e2e8f0;
        }

        .gcw-section {
            padding: 40px 0;
        }

        .faction-overview {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 40px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
            backdrop-filter: blur(10px);
        }

        .faction-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .faction-stat {
            text-align: center;
            padding: 25px;
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(6, 182, 212, 0.3);
            transition: all 0.3s ease;
        }

        .faction-stat:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.3);
        }

        .faction-stat.imperial {
            border-left: 4px solid #dc2626;
        }

        .faction-stat.rebel {
            border-left: 4px solid #16a34a;
        }

        .faction-stat.neutral {
            border-left: 4px solid #f59e0b;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
            color: #06b6d4;
        }

        .stat-label {
            font-size: 1rem;
            opacity: 0.8;
            color: #e2e8f0;
        }

        .planet-card {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
            margin-bottom: 25px;
            overflow: hidden;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .planet-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.4);
        }

        .planet-header {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(30, 41, 59, 0.9) 100%);
            color: white;
            padding: 20px;
            border-bottom: 1px solid rgba(6, 182, 212, 0.3);
        }

        .planet-header h3 {
            margin: 0;
            font-size: 1.4rem;
            font-weight: 600;
            color: #06b6d4;
        }

        .planet-content {
            padding: 25px;
        }

        .faction-control {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 15px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 8px;
            border: 1px solid rgba(6, 182, 212, 0.2);
        }

        .faction-name {
            font-weight: 600;
            color: #e2e8f0;
        }

        .faction-control.imperial .faction-name {
            color: #fca5a5;
        }

        .faction-control.rebel .faction-name {
            color: #86efac;
        }

        .faction-control.neutral .faction-name {
            color: #fde047;
        }

        .control-slider {
            width: 200px;
            height: 8px;
            border-radius: 4px;
            background: rgba(6, 182, 212, 0.2);
            outline: none;
            -webkit-appearance: none;
        }

        .control-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #06b6d4;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
        }

        .control-slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #06b6d4;
            cursor: pointer;
            border: none;
            box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
        }

        .control-value {
            font-weight: 600;
            color: #06b6d4;
            min-width: 40px;
            text-align: center;
        }

        .planet-summary {
            background: rgba(15, 23, 42, 0.6);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid rgba(6, 182, 212, 0.2);
        }

        .summary-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            color: #e2e8f0;
        }

        .summary-item:last-child {
            margin-bottom: 0;
            padding-top: 8px;
            border-top: 1px solid rgba(6, 182, 212, 0.2);
            font-weight: 600;
            color: #06b6d4;
        }

        .controls-section {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
            backdrop-filter: blur(10px);
        }

        .reset-btn {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.9) 0%, rgba(185, 28, 28, 0.9) 100%);
            color: white;
            padding: 15px 30px;
            border: 1px solid rgba(220, 38, 38, 0.6);
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .reset-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .reset-btn:hover::before {
            left: 100%;
        }

        .reset-btn:hover {
            background: linear-gradient(135deg, rgba(185, 28, 28, 0.9) 0%, rgba(153, 27, 27, 0.9) 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 38, 38, 0.4);
        }

        .export-btn {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.9) 0%, rgba(22, 163, 74, 0.9) 100%);
            color: white;
            padding: 15px 30px;
            border: 1px solid rgba(34, 197, 94, 0.6);
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-left: 15px;
            position: relative;
            overflow: hidden;
        }

        .export-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .export-btn:hover::before {
            left: 100%;
        }

        .export-btn:hover {
            background: linear-gradient(135deg, rgba(22, 163, 74, 0.9) 0%, rgba(21, 128, 61, 0.9) 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(34, 197, 94, 0.4);
        }
    </style>

    <section class="py-12 px-6 max-w-6xl mx-auto text-white relative z-10">
        <!-- Hero Section -->
        <div class="gcw-hero">
            <h1><i class="fas fa-globe mr-4"></i>GCW Calculator</h1>
            <p>Simulate Galactic Civil War control across all planets and track faction dominance</p>
        </div>

        <!-- Faction Overview -->
        <div class="faction-overview">
            <h2 class="text-2xl font-bold text-swg-cyan mb-4">Galactic Control Overview</h2>
            <div class="faction-stats">
                <div class="faction-stat imperial">
                    <div class="stat-value" id="imperial-control">0</div>
                    <div class="stat-label">Imperial Control</div>
                </div>
                <div class="faction-stat rebel">
                    <div class="stat-value" id="rebel-control">0</div>
                    <div class="stat-label">Rebel Control</div>
                </div>
                <div class="faction-stat neutral">
                    <div class="stat-value" id="neutral-control">0</div>
                    <div class="stat-label">Neutral Control</div>
                </div>
            </div>
        </div>

        <!-- Planet Controls -->
        <div class="planet-card">
            <div class="planet-header">
                <h3><i class="fas fa-planet-ringed mr-2"></i>Naboo</h3>
            </div>
            <div class="planet-content">
                <div class="faction-control imperial">
                    <span class="faction-name">Imperial Control</span>
                    <input type="range" class="control-slider" id="naboo-imperial" min="0" max="100" value="30" onchange="updatePlanetControl('naboo', 'imperial', this.value)">
                    <span class="control-value" id="naboo-imperial-value">30%</span>
                </div>
                <div class="faction-control rebel">
                    <span class="faction-name">Rebel Control</span>
                    <input type="range" class="control-slider" id="naboo-rebel" min="0" max="100" value="40" onchange="updatePlanetControl('naboo', 'rebel', this.value)">
                    <span class="control-value" id="naboo-rebel-value">40%</span>
                </div>
                <div class="faction-control neutral">
                    <span class="faction-name">Neutral Control</span>
                    <input type="range" class="control-slider" id="naboo-neutral" min="0" max="100" value="30" onchange="updatePlanetControl('naboo', 'neutral', this.value)">
                    <span class="control-value" id="naboo-neutral-value">30%</span>
                </div>
                <div class="planet-summary">
                    <div class="summary-item">
                        <span>Total Control:</span>
                        <span id="naboo-total">100%</span>
                    </div>
                    <div class="summary-item">
                        <span>Dominant Faction:</span>
                        <span id="naboo-dominant">Rebel</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="planet-card">
            <div class="planet-header">
                <h3><i class="fas fa-mountain mr-2"></i>Tatooine</h3>
            </div>
            <div class="planet-content">
                <div class="faction-control imperial">
                    <span class="faction-name">Imperial Control</span>
                    <input type="range" class="control-slider" id="tatooine-imperial" min="0" max="100" value="60" onchange="updatePlanetControl('tatooine', 'imperial', this.value)">
                    <span class="control-value" id="tatooine-imperial-value">60%</span>
                </div>
                <div class="faction-control rebel">
                    <span class="faction-name">Rebel Control</span>
                    <input type="range" class="control-slider" id="tatooine-rebel" min="0" max="100" value="25" onchange="updatePlanetControl('tatooine', 'rebel', this.value)">
                    <span class="control-value" id="tatooine-rebel-value">25%</span>
                </div>
                <div class="faction-control neutral">
                    <span class="faction-name">Neutral Control</span>
                    <input type="range" class="control-slider" id="tatooine-neutral" min="0" max="100" value="15" onchange="updatePlanetControl('tatooine', 'neutral', this.value)">
                    <span class="control-value" id="tatooine-neutral-value">15%</span>
                </div>
                <div class="planet-summary">
                    <div class="summary-item">
                        <span>Total Control:</span>
                        <span id="tatooine-total">100%</span>
                    </div>
                    <div class="summary-item">
                        <span>Dominant Faction:</span>
                        <span id="tatooine-dominant">Imperial</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Controls -->
        <div class="controls-section">
            <h3 class="text-xl font-bold text-swg-cyan mb-4">GCW Controls</h3>
            <button class="reset-btn" onclick="resetGCW()">
                <i class="fas fa-undo mr-2"></i>Reset All Planets
            </button>
            <button class="export-btn" onclick="exportGCW()">
                <i class="fas fa-download mr-2"></i>Export GCW Data
            </button>
        </div>
    </section>

    <script>
        let planetData = {
            naboo: { imperial: 30, rebel: 40, neutral: 30 },
            tatooine: { imperial: 60, rebel: 25, neutral: 15 }
        };

        function updatePlanetControl(planet, faction, value) {
            planetData[planet][faction] = parseInt(value);
            updatePlanetDisplay(planet);
            updateFactionOverview();
        }

        function updatePlanetDisplay(planet) {
            const data = planetData[planet];
            const total = data.imperial + data.rebel + data.neutral;
            
            // Update values
            document.getElementById(\`\${planet}-imperial-value\`).textContent = data.imperial + '%';
            document.getElementById(\`\${planet}-rebel-value\`).textContent = data.rebel + '%';
            document.getElementById(\`\${planet}-neutral-value\`).textContent = data.neutral + '%';
            document.getElementById(\`\${planet}-total\`).textContent = total + '%';
            
            // Determine dominant faction
            let dominant = 'Neutral';
            let maxControl = data.neutral;
            
            if (data.imperial > maxControl) {
                dominant = 'Imperial';
                maxControl = data.imperial;
            }
            if (data.rebel > maxControl) {
                dominant = 'Rebel';
                maxControl = data.rebel;
            }
            
            document.getElementById(\`\${planet}-dominant\`).textContent = dominant;
        }

        function updateFactionOverview() {
            let imperialTotal = 0;
            let rebelTotal = 0;
            let neutralTotal = 0;
            
            Object.values(planetData).forEach(planet => {
                imperialTotal += planet.imperial;
                rebelTotal += planet.rebel;
                neutralTotal += planet.neutral;
            });
            
            const planetCount = Object.keys(planetData).length;
            imperialTotal = Math.round(imperialTotal / planetCount);
            rebelTotal = Math.round(rebelTotal / planetCount);
            neutralTotal = Math.round(neutralTotal / planetCount);
            
            document.getElementById('imperial-control').textContent = imperialTotal + '%';
            document.getElementById('rebel-control').textContent = rebelTotal + '%';
            document.getElementById('neutral-control').textContent = neutralTotal + '%';
        }

        function resetGCW() {
            planetData = {
                naboo: { imperial: 30, rebel: 40, neutral: 30 },
                tatooine: { imperial: 60, rebel: 25, neutral: 15 }
            };
            
            // Reset sliders
            document.getElementById('naboo-imperial').value = 30;
            document.getElementById('naboo-rebel').value = 40;
            document.getElementById('naboo-neutral').value = 30;
            document.getElementById('tatooine-imperial').value = 60;
            document.getElementById('tatooine-rebel').value = 25;
            document.getElementById('tatooine-neutral').value = 15;
            
            updatePlanetDisplay('naboo');
            updatePlanetDisplay('tatooine');
            updateFactionOverview();
        }

        function exportGCW() {
            const gcwData = {
                timestamp: new Date().toISOString(),
                planets: planetData,
                overview: {
                    imperial: document.getElementById('imperial-control').textContent,
                    rebel: document.getElementById('rebel-control').textContent,
                    neutral: document.getElementById('neutral-control').textContent
                }
            };
            
            const dataStr = JSON.stringify(gcwData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'swg-gcw-data.json';
            link.click();
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updatePlanetDisplay('naboo');
            updatePlanetDisplay('tatooine');
            updateFactionOverview();
        });
    </script>
    `;
  }
};