module.exports = class {
  data() {
    return {
      title: "Skill Calculator - SWGDB Tools",
      description: "Interactive skill calculator for Star Wars Galaxies Restoration - plan your profession builds with automatic dependency tracking",
      layout: "base.njk",
      permalink: "/tools/skill-calculator/"
    };
  }

  render(data) {
    return `
    <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --dark-color: #1a1a1a;
            --light-color: #f8f9fa;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
        }

        .calculator-hero {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
        }

        .calculator-hero h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .calculator-hero p {
            font-size: 1.1rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }

        .calculator-section {
            padding: 40px 0;
        }

        .points-display {
            background: var(--dark-color);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }

        .points-used {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
        }

        .points-remaining {
            font-size: 1.2rem;
            margin-top: 10px;
        }

        .profession-tree {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }

        .profession-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .profession-header h3 {
            margin: 0;
            font-size: 1.4rem;
            font-weight: 600;
        }

        .branch-section {
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }

        .branch-section:last-child {
            border-bottom: none;
        }

        .branch-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--dark-color);
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .skill-button {
            display: block;
            width: 100%;
            text-align: left;
            padding: 12px 16px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            color: var(--dark-color);
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
        }

        .skill-button:hover {
            background: #e9ecef;
            border-color: var(--primary-color);
            color: var(--dark-color);
            transform: translateY(-1px);
        }

        .skill-button.selected {
            background: var(--primary-color);
            border-color: var(--primary-color);
            color: white;
        }

        .skill-button.prerequisite-missing {
            background: #f8f9fa;
            border-color: #dee2e6;
            color: #6c757d;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .skill-cost {
            float: right;
            background: rgba(0, 0, 0, 0.1);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .skill-button.selected .skill-cost {
            background: rgba(255, 255, 255, 0.2);
        }

        .controls-section {
            background: var(--light-color);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }

        .reset-btn {
            background: var(--danger-color);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .reset-btn:hover {
            background: #c82333;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
        }

        .export-btn {
            background: var(--success-color);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-left: 10px;
        }

        .export-btn:hover {
            background: #218838;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
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
            .calculator-hero h1 {
                font-size: 2rem;
            }
            
            .controls-section {
                text-align: center;
            }
            
            .reset-btn, .export-btn {
                display: block;
                width: 100%;
                margin: 10px 0;
            }
        }
    </style>
    <div class="calculator-hero">
        <div class="container">
            <h1><i class="fas fa-calculator"></i> Skill Calculator</h1>
            <p>Plan your profession build using our interactive skill calculator. Skill dependencies, points, and unlocks are handled automatically.</p>
        </div>
    </div>

    <div class="calculator-section">
        <div class="container">
            <div class="points-display">
                <div class="points-used" id="points-used">0</div>
                <div class="points-remaining">Points Used / 250 Total</div>
                <div style="margin-top: 10px;">
                    <span id="points-remaining" style="color: var(--warning-color);">250 Points Remaining</span>
                </div>
            </div>

            <div class="controls-section">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h4 style="margin: 0; color: var(--dark-color);">
                            <i class="fas fa-cogs"></i> Build Controls
                        </h4>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9rem;">
                            Reset your build or export your skill selection
                        </p>
                    </div>
                    <div class="col-md-6" style="text-align: right;">
                        <button id="reset-btn" class="reset-btn">
                            <i class="fas fa-trash"></i> Reset Build
                        </button>
                        <button id="export-btn" class="export-btn">
                            <i class="fas fa-download"></i> Export Build
                        </button>
                    </div>
                </div>
            </div>

            <div id="skill-calculator" class="row">
                <div class="loading-spinner">
                    <i class="fas fa-spinner"></i>
                    <p style="margin-top: 20px;">Loading skill trees...</p>
                </div>
            </div>
        </div>
    </div>

    <script type="module">
        let skillData = [];
        let pointsUsed = 0;
        let selectedSkills = new Set();

        async function loadSkills() {
            try {
                const response = await fetch('/data/skills.json');
                skillData = await response.json();
                return skillData;
            } catch (error) {
                console.error('Error loading skills:', error);
                // Fallback to sample data
                return getSampleData();
            }
        }

        function getSampleData() {
            return [
                {
                    "profession": "Rifleman",
                    "branches": [
                        {
                            "name": "Accuracy",
                            "icon": "fas fa-crosshairs",
                            "skills": [
                                { "id": "rifle_acc_1", "name": "Rifle Accuracy I", "cost": 1, "prerequisites": [] },
                                { "id": "rifle_acc_2", "name": "Rifle Accuracy II", "cost": 2, "prerequisites": ["rifle_acc_1"] },
                                { "id": "rifle_acc_3", "name": "Rifle Accuracy III", "cost": 3, "prerequisites": ["rifle_acc_2"] },
                                { "id": "rifle_acc_4", "name": "Master Rifleman", "cost": 4, "prerequisites": ["rifle_acc_3"] }
                            ]
                        },
                        {
                            "name": "Speed",
                            "icon": "fas fa-tachometer-alt",
                            "skills": [
                                { "id": "rifle_speed_1", "name": "Rifle Speed I", "cost": 1, "prerequisites": [] },
                                { "id": "rifle_speed_2", "name": "Rifle Speed II", "cost": 2, "prerequisites": ["rifle_speed_1"] },
                                { "id": "rifle_speed_3", "name": "Rifle Speed III", "cost": 3, "prerequisites": ["rifle_speed_2"] },
                                { "id": "rifle_speed_4", "name": "Rifle Speed IV", "cost": 4, "prerequisites": ["rifle_speed_3"] }
                            ]
                        }
                    ]
                },
                {
                    "profession": "Pistoleer",
                    "branches": [
                        {
                            "name": "Accuracy",
                            "icon": "fas fa-bullseye",
                            "skills": [
                                { "id": "pistol_acc_1", "name": "Pistol Accuracy I", "cost": 1, "prerequisites": [] },
                                { "id": "pistol_acc_2", "name": "Pistol Accuracy II", "cost": 2, "prerequisites": ["pistol_acc_1"] },
                                { "id": "pistol_acc_3", "name": "Pistol Accuracy III", "cost": 3, "prerequisites": ["pistol_acc_2"] },
                                { "id": "pistol_acc_4", "name": "Master Pistoleer", "cost": 4, "prerequisites": ["pistol_acc_3"] }
                            ]
                        },
                        {
                            "name": "Speed",
                            "icon": "fas fa-bolt",
                            "skills": [
                                { "id": "pistol_speed_1", "name": "Pistol Speed I", "cost": 1, "prerequisites": [] },
                                { "id": "pistol_speed_2", "name": "Pistol Speed II", "cost": 2, "prerequisites": ["pistol_speed_1"] },
                                { "id": "pistol_speed_3", "name": "Pistol Speed III", "cost": 3, "prerequisites": ["pistol_speed_2"] },
                                { "id": "pistol_speed_4", "name": "Pistol Speed IV", "cost": 4, "prerequisites": ["pistol_speed_3"] }
                            ]
                        }
                    ]
                },
                {
                    "profession": "Combat Medic",
                    "branches": [
                        {
                            "name": "Healing",
                            "icon": "fas fa-heart",
                            "skills": [
                                { "id": "medic_heal_1", "name": "Basic Healing I", "cost": 1, "prerequisites": [] },
                                { "id": "medic_heal_2", "name": "Basic Healing II", "cost": 2, "prerequisites": ["medic_heal_1"] },
                                { "id": "medic_heal_3", "name": "Advanced Healing", "cost": 3, "prerequisites": ["medic_heal_2"] },
                                { "id": "medic_heal_4", "name": "Master Combat Medic", "cost": 4, "prerequisites": ["medic_heal_3"] }
                            ]
                        },
                        {
                            "name": "Support",
                            "icon": "fas fa-plus-square",
                            "skills": [
                                { "id": "medic_support_1", "name": "Medical Support I", "cost": 1, "prerequisites": [] },
                                { "id": "medic_support_2", "name": "Medical Support II", "cost": 2, "prerequisites": ["medic_support_1"] },
                                { "id": "medic_support_3", "name": "Medical Support III", "cost": 3, "prerequisites": ["medic_support_2"] },
                                { "id": "medic_support_4", "name": "Medical Support IV", "cost": 4, "prerequisites": ["medic_support_3"] }
                            ]
                        }
                    ]
                }
            ];
        }

        function renderSkillTrees(data) {
            const container = document.getElementById('skill-calculator');
            container.innerHTML = '';

            data.forEach(tree => {
                const col = document.createElement('div');
                col.className = 'col-lg-4 col-md-6 mb-4';
                
                const treeDiv = document.createElement('div');
                treeDiv.className = 'profession-tree';
                
                const header = document.createElement('div');
                header.className = 'profession-header';
                header.innerHTML = \`<h3><i class="fas fa-user-tie"></i> \${tree.profession}</h3>\`;
                treeDiv.appendChild(header);

                tree.branches.forEach(branch => {
                    const branchDiv = document.createElement('div');
                    branchDiv.className = 'branch-section';
                    
                    const branchTitle = document.createElement('div');
                    branchTitle.className = 'branch-title';
                    branchTitle.innerHTML = \`<i class="\${branch.icon || 'fas fa-cog'}"></i> \${branch.name}\`;
                    branchDiv.appendChild(branchTitle);

                    branch.skills.forEach(skill => {
                        const btn = document.createElement('button');
                        btn.innerHTML = \`
                            \${skill.name}
                            <span class="skill-cost">\${skill.cost} pts</span>
                        \`;
                        btn.className = 'skill-button';
                        btn.dataset.skillId = skill.id;
                        btn.dataset.skillCost = skill.cost;
                        btn.dataset.prerequisites = JSON.stringify(skill.prerequisites);
                        
                        btn.addEventListener('click', () => toggleSkill(skill));
                        branchDiv.appendChild(btn);
                    });

                    treeDiv.appendChild(branchDiv);
                });

                col.appendChild(treeDiv);
                container.appendChild(col);
            });

            updateSkillStates();
        }

        function toggleSkill(skill) {
            if (selectedSkills.has(skill.id)) {
                // Deselect skill and its dependents
                deselectSkill(skill.id);
            } else {
                // Check prerequisites and points
                if (canSelectSkill(skill)) {
                    selectSkill(skill.id);
                }
            }
            updateSkillStates();
            updatePointsDisplay();
        }

        function canSelectSkill(skill) {
            // Check if enough points
            if (pointsUsed + skill.cost > 250) {
                alert('Not enough skill points remaining!');
                return false;
            }
            
            // Check prerequisites
            for (const prereq of skill.prerequisites) {
                if (!selectedSkills.has(prereq)) {
                    alert('Prerequisites not met for this skill.');
                    return false;
                }
            }
            
            return true;
        }

        function selectSkill(skillId) {
            selectedSkills.add(skillId);
            const skill = findSkillById(skillId);
            if (skill) {
                pointsUsed += skill.cost;
            }
        }

        function deselectSkill(skillId) {
            // First deselect all skills that depend on this one
            getAllSkills().forEach(skill => {
                if (skill.prerequisites.includes(skillId) && selectedSkills.has(skill.id)) {
                    deselectSkill(skill.id);
                }
            });
            
            // Then deselect this skill
            selectedSkills.delete(skillId);
            const skill = findSkillById(skillId);
            if (skill) {
                pointsUsed -= skill.cost;
            }
        }

        function findSkillById(skillId) {
            for (const tree of skillData) {
                for (const branch of tree.branches) {
                    for (const skill of branch.skills) {
                        if (skill.id === skillId) {
                            return skill;
                        }
                    }
                }
            }
            return null;
        }

        function getAllSkills() {
            const skills = [];
            for (const tree of skillData) {
                for (const branch of tree.branches) {
                    skills.push(...branch.skills);
                }
            }
            return skills;
        }

        function updateSkillStates() {
            document.querySelectorAll('.skill-button').forEach(btn => {
                const skillId = btn.dataset.skillId;
                const prerequisites = JSON.parse(btn.dataset.prerequisites);
                
                btn.classList.remove('selected', 'prerequisite-missing');
                
                if (selectedSkills.has(skillId)) {
                    btn.classList.add('selected');
                } else {
                    // Check if prerequisites are met
                    const prereqsMet = prerequisites.every(prereq => selectedSkills.has(prereq));
                    if (!prereqsMet && prerequisites.length > 0) {
                        btn.classList.add('prerequisite-missing');
                    }
                }
            });
        }

        function updatePointsDisplay() {
            document.getElementById('points-used').textContent = pointsUsed;
            const remaining = 250 - pointsUsed;
            document.getElementById('points-remaining').textContent = \`\${remaining} Points Remaining\`;
            
            // Change color based on remaining points
            const remainingEl = document.getElementById('points-remaining');
            if (remaining < 50) {
                remainingEl.style.color = 'var(--danger-color)';
            } else if (remaining < 100) {
                remainingEl.style.color = 'var(--warning-color)';
            } else {
                remainingEl.style.color = 'var(--success-color)';
            }
        }

        function resetBuild() {
            if (confirm('Are you sure you want to reset your build? This will clear all selected skills.')) {
                selectedSkills.clear();
                pointsUsed = 0;
                updateSkillStates();
                updatePointsDisplay();
            }
        }

        function exportBuild() {
            const build = {
                skills: Array.from(selectedSkills),
                totalPoints: pointsUsed,
                timestamp: new Date().toISOString()
            };
            
            const dataStr = JSON.stringify(build, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = \`swg-build-\${Date.now()}.json\`;
            link.click();
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', async function() {
            const data = await loadSkills();
            renderSkillTrees(data);
            updatePointsDisplay();
            
            document.getElementById('reset-btn').addEventListener('click', resetBuild);
            document.getElementById('export-btn').addEventListener('click', exportBuild);
        });
    </script>
    `;
  }
};