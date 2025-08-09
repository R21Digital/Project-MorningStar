module.exports = class {
  data() {
    return {
      title: "GCW Calculator - SWGDB Tools",
      description: "Galactic Civil War planet control calculator for Star Wars Galaxies Restoration - simulate faction dominance across the galaxy",
      layout: "base.njk",
      permalink: "/tools/gcw-calculator/"
    };
  }

  render(data) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.title}</title>
    <meta name="description" content="${data.description}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --imperial-color: #dc3545;
            --rebel-color: #28a745;
            --neutral-color: #ffc107;
            --dark-color: #1a1a1a;
            --light-color: #f8f9fa;
        }

        .gcw-hero {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
        }

        .gcw-hero h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .gcw-hero p {
            font-size: 1.1rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }

        .gcw-section {
            padding: 40px 0;
        }

        .faction-overview {
            background: var(--dark-color);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 40px;
        }

        .faction-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .faction-stat {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
        }

        .faction-stat.imperial {
            border-left: 4px solid var(--imperial-color);
        }

        .faction-stat.rebel {
            border-left: 4px solid var(--rebel-color);
        }

        .faction-stat.neutral {
            border-left: 4px solid var(--neutral-color);
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 1rem;
            opacity: 0.8;
        }

        .planet-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
            overflow: hidden;
            transition: transform 0.3s ease;
        }

        .planet-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }

        .planet-header {
            padding: 20px;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
        }

        .planet-name {
            font-size: 1.4rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .planet-control {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 5px;
        }

        .planet-body {
            padding: 25px;
        }

        .control-section {
            margin-bottom: 25px;
        }

        .control-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .control-value {
            font-size: 1.1rem;
            font-weight: bold;
        }

        .control-slider {
            width: 100%;
            height: 8px;
            border-radius: 4px;
            outline: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .control-slider.imperial {
            background: linear-gradient(90deg, #f8f9fa 0%, var(--imperial-color) 100%);
        }

        .control-slider.rebel {
            background: linear-gradient(90deg, #f8f9fa 0%, var(--rebel-color) 100%);
        }

        .control-slider::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary-color);
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        }

        .control-slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary-color);
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        }

        .faction-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
        }

        .faction-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .faction-dot.imperial {
            background: var(--imperial-color);
        }

        .faction-dot.rebel {
            background: var(--rebel-color);
        }

        .faction-dot.neutral {
            background: var(--neutral-color);
        }

        .control-bars {
            display: flex;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
            background: #e9ecef;
        }

        .control-bar {
            height: 100%;
            transition: width 0.3s ease;
        }

        .control-bar.imperial {
            background: var(--imperial-color);
        }

        .control-bar.rebel {
            background: var(--rebel-color);
        }

        .control-bar.neutral {
            background: var(--neutral-color);
        }

        .reset-btn {
            background: var(--neutral-color);
            color: var(--dark-color);
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 30px;
        }

        .reset-btn:hover {
            background: #e0a800;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
        }

        .loading-spinner {
            text-align: center;
            padding: 60px;
            color: var(--primary-color);
        }

        .loading-spinner i {
            font-size: 3rem;
            animation: spin 2s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .gcw-hero h1 {
                font-size: 2rem;
            }
            
            .faction-stats {
                grid-template-columns: 1fr;
            }
            
            .planet-body {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="gcw-hero">
        <div class="container">
            <h1><i class="fas fa-globe"></i> GCW Planet Control Calculator</h1>
            <p>Simulate Galactic Civil War control by adjusting faction percentages on each planet. Visualize Imperial vs Rebel dominance across the galaxy.</p>
        </div>
    </div>

    <div class="gcw-section">
        <div class="container">
            <div class="faction-overview">
                <h2 style="margin: 0 0 20px 0; text-align: center;">
                    <i class="fas fa-chart-pie"></i> Galaxy-Wide Control
                </h2>
                <div class="faction-stats">
                    <div class="faction-stat imperial">
                        <div class="stat-value" id="imperial-total" style="color: var(--imperial-color);">0%</div>
                        <div class="stat-label">Imperial Control</div>
                    </div>
                    <div class="faction-stat rebel">
                        <div class="stat-value" id="rebel-total" style="color: var(--rebel-color);">0%</div>
                        <div class="stat-label">Rebel Control</div>
                    </div>
                    <div class="faction-stat neutral">
                        <div class="stat-value" id="neutral-total" style="color: var(--neutral-color);">0%</div>
                        <div class="stat-label">Neutral/Contested</div>
                    </div>
                </div>
            </div>

            <div style="text-align: center; margin-bottom: 30px;">
                <button id="reset-btn" class="reset-btn">
                    <i class="fas fa-undo"></i> Reset to Defaults
                </button>
            </div>

            <div id="gcw-calculator" class="row">
                <div class="loading-spinner">
                    <i class="fas fa-spinner"></i>
                    <p style="margin-top: 20px;">Loading planets...</p>
                </div>
            </div>
        </div>
    </div>

    <script type="module">
        let planets = [];
        let originalData = [];

        async function loadPlanets() {
            try {
                const response = await fetch('/data/gcw-planets.json');
                const data = await response.json();
                planets = [...data];
                originalData = JSON.parse(JSON.stringify(data)); // Deep copy for reset
                return planets;
            } catch (error) {
                console.error('Error loading planets:', error);
                return getSampleData();
            }
        }

        function getSampleData() {
            const data = [
                { "name": "Corellia", "imperial": 45, "rebel": 35, "description": "Core World industrial planet" },
                { "name": "Tatooine", "imperial": 25, "rebel": 55, "description": "Outer Rim desert world" },
                { "name": "Dantooine", "imperial": 40, "rebel": 50, "description": "Agricultural rebel stronghold" },
                { "name": "Naboo", "imperial": 60, "rebel": 25, "description": "Mid Rim peaceful world" },
                { "name": "Talus", "imperial": 35, "rebel": 45, "description": "Corellian system moon" },
                { "name": "Rori", "imperial": 30, "rebel": 50, "description": "Naboo system moon" },
                { "name": "Lok", "imperial": 20, "rebel": 60, "description": "Outer Rim pirate haven" },
                { "name": "Endor", "imperial": 55, "rebel": 35, "description": "Forest moon research station" },
                { "name": "Yavin 4", "imperial": 15, "rebel": 70, "description": "Ancient rebel base" }
            ];
            planets = [...data];
            originalData = JSON.parse(JSON.stringify(data));
            return data;
        }

        function renderGCW(data) {
            const container = document.getElementById('gcw-calculator');
            container.innerHTML = '';

            data.forEach((planet, idx) => {
                const col = document.createElement('div');
                col.className = 'col-lg-4 col-md-6 mb-4';
                
                const neutral = Math.max(0, 100 - planet.imperial - planet.rebel);
                const dominantFaction = planet.imperial > planet.rebel ? 'imperial' : planet.rebel > planet.imperial ? 'rebel' : 'neutral';
                
                const card = document.createElement('div');
                card.className = 'planet-card';
                
                card.innerHTML = \`
                    <div class="planet-header">
                        <h3 class="planet-name">
                            <i class="fas fa-globe-americas"></i>
                            \${planet.name}
                        </h3>
                        <div class="planet-control">
                            <div class="faction-indicator">
                                <div class="faction-dot \${dominantFaction}"></div>
                                \${dominantFaction === 'imperial' ? 'Imperial Controlled' : 
                                  dominantFaction === 'rebel' ? 'Rebel Controlled' : 
                                  'Contested Territory'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="planet-body">
                        \${planet.description ? \`<p style="color: #666; font-style: italic; margin-bottom: 20px;">\${planet.description}</p>\` : ''}
                        
                        <div class="control-section">
                            <div class="control-label">
                                <span><i class="fas fa-empire" style="color: var(--imperial-color);"></i> Imperial Control</span>
                                <span class="control-value" style="color: var(--imperial-color);">\${planet.imperial}%</span>
                            </div>
                            <input type="range" min="0" max="100" value="\${planet.imperial}" 
                                   class="control-slider imperial" data-idx="\${idx}" data-faction="imperial">
                        </div>
                        
                        <div class="control-section">
                            <div class="control-label">
                                <span><i class="fas fa-rebel" style="color: var(--rebel-color);"></i> Rebel Control</span>
                                <span class="control-value" style="color: var(--rebel-color);">\${planet.rebel}%</span>
                            </div>
                            <input type="range" min="0" max="100" value="\${planet.rebel}" 
                                   class="control-slider rebel" data-idx="\${idx}" data-faction="rebel">
                        </div>
                        
                        <div style="margin-top: 15px;">
                            <div class="control-label">
                                <span><i class="fas fa-question-circle" style="color: var(--neutral-color);"></i> Neutral/Contested</span>
                                <span class="control-value" style="color: var(--neutral-color);">\${neutral}%</span>
                            </div>
                            <div class="control-bars">
                                <div class="control-bar imperial" style="width: \${planet.imperial}%;"></div>
                                <div class="control-bar rebel" style="width: \${planet.rebel}%;"></div>
                                <div class="control-bar neutral" style="width: \${neutral}%;"></div>
                            </div>
                        </div>
                    </div>
                \`;

                col.appendChild(card);
                container.appendChild(col);
            });

            // Add event listeners
            document.querySelectorAll('.control-slider').forEach(slider => {
                slider.addEventListener('input', handleSliderChange);
            });

            updateTotals();
        }

        function handleSliderChange(event) {
            const idx = parseInt(event.target.dataset.idx);
            const faction = event.target.dataset.faction;
            const value = parseInt(event.target.value);
            
            // Update planet data
            planets[idx][faction] = value;
            
            // Ensure total doesn't exceed 100%
            const imperial = planets[idx].imperial;
            const rebel = planets[idx].rebel;
            const total = imperial + rebel;
            
            if (total > 100) {
                const otherFaction = faction === 'imperial' ? 'rebel' : 'imperial';
                planets[idx][otherFaction] = Math.max(0, 100 - value);
                
                // Update the other slider
                const otherSlider = document.querySelector(\`[data-idx="\${idx}"][data-faction="\${otherFaction}"]\`);
                if (otherSlider) {
                    otherSlider.value = planets[idx][otherFaction];
                }
            }
            
            // Update UI
            updatePlanetDisplay(idx);
            updateTotals();
        }

        function updatePlanetDisplay(idx) {
            const planet = planets[idx];
            const neutral = Math.max(0, 100 - planet.imperial - planet.rebel);
            
            // Update value displays
            const card = document.querySelector(\`[data-idx="\${idx}"]\`).closest('.planet-card');
            const imperialValue = card.querySelector('.imperial').nextElementSibling;
            const rebelValue = card.querySelector('.rebel').nextElementSibling;
            
            card.querySelectorAll('.control-value').forEach((el, i) => {
                if (i === 0) el.textContent = \`\${planet.imperial}%\`;
                if (i === 1) el.textContent = \`\${planet.rebel}%\`;
                if (i === 2) el.textContent = \`\${neutral}%\`;
            });
            
            // Update control bars
            const bars = card.querySelectorAll('.control-bar');
            bars[0].style.width = \`\${planet.imperial}%\`;
            bars[1].style.width = \`\${planet.rebel}%\`;
            bars[2].style.width = \`\${neutral}%\`;
            
            // Update faction indicator
            const dominantFaction = planet.imperial > planet.rebel ? 'imperial' : 
                                  planet.rebel > planet.imperial ? 'rebel' : 'neutral';
            const dot = card.querySelector('.faction-dot');
            const indicator = card.querySelector('.faction-indicator');
            
            dot.className = \`faction-dot \${dominantFaction}\`;
            const text = dominantFaction === 'imperial' ? 'Imperial Controlled' : 
                        dominantFaction === 'rebel' ? 'Rebel Controlled' : 
                        'Contested Territory';
            indicator.innerHTML = \`<div class="faction-dot \${dominantFaction}"></div>\${text}\`;
        }

        function updateTotals() {
            let imperialSum = 0;
            let rebelSum = 0;
            let neutralSum = 0;
            const count = planets.length;

            planets.forEach(planet => {
                imperialSum += planet.imperial;
                rebelSum += planet.rebel;
                const neutral = Math.max(0, 100 - planet.imperial - planet.rebel);
                neutralSum += neutral;
            });

            const imperialAvg = Math.round(imperialSum / count);
            const rebelAvg = Math.round(rebelSum / count);
            const neutralAvg = Math.round(neutralSum / count);

            document.getElementById('imperial-total').textContent = \`\${imperialAvg}%\`;
            document.getElementById('rebel-total').textContent = \`\${rebelAvg}%\`;
            document.getElementById('neutral-total').textContent = \`\${neutralAvg}%\`;
        }

        function resetToDefaults() {
            if (confirm('Reset all planets to their default control percentages?')) {
                planets = JSON.parse(JSON.stringify(originalData));
                renderGCW(planets);
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', async function() {
            const data = await loadPlanets();
            renderGCW(data);
            
            document.getElementById('reset-btn').addEventListener('click', resetToDefaults);
        });
    </script>
</body>
</html>
    `;
  }
};