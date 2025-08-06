# 🤝 Contributing to SWGDB & Project MorningStar

Thank you for your interest in contributing! This guide will help you get started with contributing to **SWGDB.com** (our public platform) and understand the project structure.

## 📋 Table of Contents

- [🌟 Quick Start for New Contributors](#-quick-start-for-new-contributors)
- [🌐 Contributing to SWGDB (Public Platform)](#-contributing-to-swgdb-public-platform)
- [🔐 MS11 Research System (Private)](#-ms11-research-system-private)
- [🛠️ Development Workflow](#️-development-workflow)
- [🧪 Testing Guidelines](#-testing-guidelines)
- [📝 Documentation Standards](#-documentation-standards)
- [🎯 Code Quality Standards](#-code-quality-standards)
- [🌐 Community Guidelines](#-community-guidelines)

---

## 🌟 Quick Start for New Contributors

**Welcome to the SWGDB community!** Here's how to make your first contribution in under 10 minutes:

### 1️⃣ Choose Your Contribution Type

| **No Coding Required** | **Basic Coding** | **Advanced Development** |
|---|---|---|
| 📊 Add game data (JSON/YAML) | 🌐 Improve website UI | 🔧 Develop new APIs |
| 📝 Write guides and tutorials | 🎨 Fix styling issues | 🗄️ Database optimizations |
| 🐛 Report bugs via feedback form | 📱 Mobile responsiveness | ⚡ Performance improvements |
| 💡 Suggest new features | 🔧 Add interactive tools | 🔒 Security enhancements |

### 2️⃣ Set Up Development Environment

```bash
# Quick setup (2 minutes)
git clone https://github.com/YOUR-USERNAME/Project-MorningStar.git
cd Project-MorningStar
pip install -r requirements.txt
python dashboard/app.py
# Visit: http://localhost:5000
```

### 3️⃣ Find Your First Issue

- **🟢 Good First Issues**: Look for [`good first issue`](https://github.com/project-morningstar/Project-MorningStar/labels/good%20first%20issue) label
- **📚 Documentation**: Improve README, guides, or code comments
- **🐛 Bug Reports**: Check [`bug`](https://github.com/project-morningstar/Project-MorningStar/labels/bug) labeled issues
- **💡 Feature Requests**: Browse [`enhancement`](https://github.com/project-morningstar/Project-MorningStar/labels/enhancement) issues

---

## 🌐 Contributing to SWGDB (Public Platform)

**SWGDB is our open-source, community-driven platform.** Everyone can contribute without special approval!

### 🎯 What We're Looking For

#### 📊 Game Data Contributions (No Coding Required!)
```bash
# Easy data contributions:
data/
├── heroics/           # Add heroic instance data
│   └── new_heroic.json
├── builds/           # Character build templates
│   └── jedi_build.json
├── quests/           # Quest walkthroughs
│   └── tatooine/
└── loot_tables/      # Item and loot information
    └── weapon_data.json
```

**Example: Adding a new heroic**
```json
{
  "name": "Axkva Min",
  "difficulty": "Hard",
  "min_level": 80,
  "location": "Dathomir",
  "loot": [
    {
      "item": "Axkva Min's Saber",
      "drop_rate": "5%",
      "stats": "Legendary Jedi Weapon"
    }
  ],
  "strategy": "Focus fire on adds first, then tank and spank the boss."
}
```

#### 🌐 Website & UI Improvements
- **Frontend**: HTML, CSS, JavaScript improvements
- **Templates**: Jinja2 templates in `dashboard/templates/`  
- **Styling**: Bootstrap customizations and responsive design
- **Interactive Tools**: Character calculators, loot filters
- **Mobile Experience**: Touch-friendly interfaces

#### 🔧 API Development
- **REST APIs**: Python Flask endpoints in `api/`
- **Data Processing**: JSON/YAML parsers and validators
- **Search Features**: Advanced filtering and sorting
- **Integration**: Discord bots, third-party tools

### 🚀 SWGDB Development Workflow

#### Standard Contribution Process
```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/Project-MorningStar.git
cd Project-MorningStar

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes to SWGDB components only:
dashboard/           # Web interface
api/                # Public APIs  
data/               # Game data
docs/               # Documentation
utils/              # Utilities

# 4. Test your changes
pytest tests/ -v
python dashboard/app.py  # Test locally

# 5. Submit pull request
git push origin feature/your-feature-name
# Create PR on GitHub
```

#### Pull Request Guidelines
- **✅ Clear title**: "Add Axkva Min heroic guide" (not "fix stuff")
- **✅ Description**: What does this change and why?
- **✅ Screenshots**: For UI changes, include before/after images  
- **✅ Tests pass**: Ensure `pytest` runs successfully
- **✅ Documentation**: Update relevant docs if needed

---

## 🔐 MS11 Research System (Private)

**Important**: MS11 is a **private research system** with restricted access.

### ⚠️ MS11 Access Requirements

**MS11 is NOT open for general contributions.** Access requires:

1. **🎓 Research Purpose**: Academic research or accessibility needs
2. **🤝 Trust Building**: History of responsible SWGDB contributions  
3. **📋 Application Process**: Formal review and approval
4. **✅ Ethics Agreement**: Signed usage and compliance agreement
5. **🧪 Supervised Trial**: Monitored access period

### 🛡️ MS11 Contribution Rules

**For approved MS11 contributors:**

- **🔒 Privacy First**: All MS11 code remains private
- **📝 Documentation Required**: Extensive docs for all functions
- **👥 Multiple Reviews**: All changes require 2+ maintainer approval
- **⚖️ Ethics Review**: New features undergo ethical assessment  
- **🎯 Limited Scope**: Only approved research functionality

```python
# Example of required MS11 documentation:
def research_data_collector(target: str, duration: int) -> dict:
    """
    Collect anonymized game data for research purposes.
    
    ETHICAL NOTICE: 
    - Only for approved academic research
    - Must have explicit server permission
    - Data anonymized before storage
    - Usage logged for audit trail
    
    Args:
        target: Approved research target (validated against whitelist)
        duration: Collection time in seconds (max 3600)
    
    Returns:
        dict: Anonymized research dataset
        
    Raises:
        PermissionError: User lacks research authorization
        ValueError: Target not approved for research
        
    Example:
        data = research_data_collector("xp_rates", 1800)
    """
    verify_research_authorization()  # Security check
    validate_ethical_compliance()    # Ethics check
    # ... implementation
```

### 📞 Applying for MS11 Access

**Only apply if you have legitimate research needs:**

1. **Build SWGDB contributions** - 10+ meaningful contributions
2. **Email maintainers** at research@project-morningstar.org:
   - Research proposal and academic affiliation
   - Ethical justification for automation needs
   - Technical background and experience
   - References from academic supervisors (if applicable)

3. **Review process** (2-4 weeks):
   - Application review by project leads
   - Technical interview and ethics discussion
   - Trial access period with supervision
   - Full access upon successful completion

---

## 🛠️ Development Workflow

### 📋 Before You Start

#### Required Setup
```bash
# Check Python version (3.8+ required)
python --version

# Install dependencies  
pip install -r requirements.txt
pip install -r requirements-test.txt

# Verify setup
python -c "from dashboard.app import app; print('✅ Setup successful!')"
```

#### Repository Structure
```bash
Project-MorningStar/
├── 🌐 SWGDB (Public) - Open Contributions Welcome
│   ├── dashboard/          # Web interface (Flask)
│   ├── api/               # Public APIs
│   ├── data/              # Game data (JSON/YAML)
│   ├── docs/              # Documentation  
│   ├── utils/             # Utility scripts
│   └── tests/             # Test suites
│   
├── 🔐 MS11 (Private) - Restricted Access Only
│   ├── core/              # Automation systems
│   ├── safety/            # Anti-detection
│   ├── auth/              # Authentication  
│   └── android_ms11/      # Mobile companion
│   
└── 📚 Shared Resources
    ├── scripts/           # Build and deployment
    ├── requirements.txt   # Python dependencies
    └── README.md          # Project documentation
```

### 🔄 Git Workflow

#### Branch Naming Conventions
```bash
feature/heroic-guides     # New features
bugfix/login-error       # Bug fixes  
docs/api-examples        # Documentation
data/new-loot-tables     # Data additions
ui/mobile-responsive     # UI improvements
```

#### Commit Message Guidelines
```bash
# Good commit messages:
✅ "Add Axkva Min heroic guide with loot table"
✅ "Fix mobile responsive layout on build pages"  
✅ "Update API documentation with authentication examples"

# Poor commit messages:
❌ "fix stuff"
❌ "update"
❌ "changes"
```

---

## 🧪 Testing Guidelines

### 🎯 Testing Strategy

**We maintain high quality through comprehensive testing:**

- **Unit Tests**: Individual function testing (`tests/unit/`)
- **Integration Tests**: Component interaction testing (`tests/integration/`)
- **End-to-End Tests**: Full user workflow testing (`tests/e2e/`)
- **Data Validation**: JSON/YAML structure verification (`tests/data/`)

### 🚀 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v              # Unit tests only
pytest tests/integration/ -v       # Integration tests
pytest tests/data/ -v              # Data validation

# Run tests for specific components
pytest -k "test_heroic" -v         # Heroic-related tests
pytest -k "test_api" -v            # API tests

# Generate coverage report
pytest tests/ --cov=dashboard --cov=api --cov-report=html
open htmlcov/index.html
```

### ✅ Test Requirements for Contributions

**All SWGDB contributions must include tests:**

#### For Data Contributions:
```python
def test_new_heroic_data():
    """Test new heroic data structure and validation"""
    with open('data/heroics/axkva_min.json') as f:
        heroic = json.load(f)
    
    # Required fields
    assert 'name' in heroic
    assert 'difficulty' in heroic
    assert 'loot' in heroic
    
    # Validate loot structure
    for item in heroic['loot']:
        assert 'item' in item
        assert 'drop_rate' in item
```

#### For API Contributions:
```python
def test_heroics_api_endpoint():
    """Test heroics API returns valid data"""
    response = client.get('/api/heroics')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'heroics' in data
    assert len(data['heroics']) > 0
```

#### For UI Contributions:
```python
def test_heroic_page_loads():
    """Test heroic page renders correctly"""
    response = client.get('/heroics/axkva-min')
    
    assert response.status_code == 200
    assert b'Axkva Min' in response.data
    assert b'Difficulty:' in response.data
```

---

## 📝 Documentation Standards

### 📚 Documentation is Critical

**Good documentation makes our project accessible to everyone.**

#### Required Documentation:

##### 🔧 Code Documentation
```python
def get_heroic_loot(heroic_id: str, difficulty: str = "normal") -> List[Dict]:
    """
    Retrieve loot table for a specific heroic instance.
    
    Args:
        heroic_id: Unique identifier for the heroic (e.g., "axkva_min")
        difficulty: Difficulty level ("normal", "hard", "nightmare")
        
    Returns:
        List of loot items with drop rates and statistics
        
    Raises:
        ValueError: If heroic_id not found
        KeyError: If difficulty level not available
        
    Example:
        >>> loot = get_heroic_loot("axkva_min", "hard")
        >>> print(loot[0]['item'])
        "Axkva Min's Saber"
    """
```

##### 📖 User Documentation
```markdown
# Heroic Instance Guides

## Axkva Min

**Difficulty**: Hard  
**Recommended Level**: 80+  
**Location**: Dathomir Cave System  

### Strategy

1. **Preparation**: Bring buff packages and medical supplies
2. **Phase 1**: Clear adds while avoiding boss AoE attacks  
3. **Phase 2**: Focus fire on boss, rotate tanks when needed

### Loot Table

| Item | Drop Rate | Notes |
|------|-----------|-------|
| Axkva Min's Saber | 5% | Legendary Jedi weapon |
| Nightsister Cloak | 15% | +25 Force Power |
```

##### 🔧 API Documentation
```yaml
/api/heroics/{heroic_id}:
  get:
    summary: Get heroic instance details
    parameters:
      - name: heroic_id
        in: path
        required: true
        schema:
          type: string
        example: "axkva_min"
    responses:
      200:
        description: Heroic instance data
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: "Axkva Min"
                difficulty:
                  type: string
                  example: "Hard"
```

---

## 🎯 Code Quality Standards

### 📏 Python Code Standards

**We follow PEP 8 with some project-specific guidelines:**

```python
# ✅ Good Python code example:
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class HeroicManager:
    """Manages heroic instance data and operations."""
    
    def __init__(self, data_path: str = "data/heroics"):
        self.data_path = Path(data_path)
        self.heroics_cache: Optional[Dict] = None
    
    def get_heroic(self, heroic_id: str) -> Optional[Dict]:
        """Retrieve heroic by ID with error handling."""
        try:
            heroic_file = self.data_path / f"{heroic_id}.json"
            if not heroic_file.exists():
                logger.warning(f"Heroic {heroic_id} not found")
                return None
                
            with open(heroic_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading heroic {heroic_id}: {e}")
            return None
```

### 🌐 Frontend Code Standards

```javascript
// ✅ Good JavaScript code example:
class HeroicDisplay {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.apiBase = '/api/heroics';
    }
    
    async loadHeroic(heroicId) {
        try {
            const response = await fetch(`${this.apiBase}/${heroicId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const heroic = await response.json();
            this.renderHeroic(heroic);
            
        } catch (error) {
            console.error('Failed to load heroic:', error);
            this.showError('Failed to load heroic data');
        }
    }
    
    renderHeroic(heroic) {
        const html = `
            <h2>${heroic.name}</h2>
            <p>Difficulty: <span class="difficulty-${heroic.difficulty.toLowerCase()}">${heroic.difficulty}</span></p>
            <div class="loot-table">
                ${heroic.loot.map(item => `
                    <div class="loot-item">
                        <strong>${item.item}</strong> - ${item.drop_rate}
                    </div>
                `).join('')}
            </div>
        `;
        
        this.container.innerHTML = html;
    }
}
```

### 🎨 CSS/HTML Standards

```css
/* ✅ Good CSS example: */
.heroic-guide {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    
    /* Use CSS custom properties for consistency */
    background-color: var(--bg-primary);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-card);
}

.difficulty-hard {
    color: var(--color-danger);
    font-weight: bold;
}

/* Mobile-first responsive design */
@media (max-width: 768px) {
    .heroic-guide {
        padding: 1rem;
        margin: 0 1rem;
    }
}
```

### 📊 Data Format Standards

```json
{
  "name": "Axkva Min",
  "id": "axkva_min",
  "difficulty": "Hard",
  "min_level": 80,
  "location": {
    "planet": "Dathomir",
    "coordinates": [1234, 5678],
    "landmark": "Cave System"
  },
  "loot": [
    {
      "item": "Axkva Min's Saber",
      "type": "weapon",
      "drop_rate": "5%",
      "stats": {
        "damage": "350-400",
        "special": "Legendary Jedi Weapon"
      }
    }
  ],
  "strategy": {
    "phases": [
      {
        "name": "Add Clear",
        "description": "Focus on clearing adds while avoiding AoE"
      }
    ]
  }
}
```

---

## 🌐 Community Guidelines

### 🤝 Our Community Values

- **🔓 Open & Welcoming**: Everyone is welcome regardless of experience level
- **🎮 SWG Passion**: United by love for Star Wars Galaxies
- **🤝 Collaboration**: We build better things together
- **📈 Quality First**: High standards benefit everyone
- **🎯 Helpful**: Support others and share knowledge
- **🔒 Respectful**: Treat everyone with dignity and respect

### 💬 Communication Channels

#### GitHub (Primary)
- **Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and reviews
- **Discussions**: General questions and community chat
- **Wiki**: Community-maintained documentation

#### Discord Community
- **#general**: Casual conversation and help
- **#swgdb-dev**: Technical development discussions  
- **#data-contributors**: Game data verification and discussion
- **#feedback**: Website feedback and suggestions

### 🎖️ Recognition System

**We celebrate all contributions:**

```
🌟 First Contribution - Your first merged PR
📊 Data Expert - Significant game data contributions  
🔧 Code Contributor - Multiple code contributions
📝 Documentation Hero - Improved project docs
🐛 Bug Hunter - Found and fixed important bugs
🎨 Design Contributor - UI/UX improvements
⭐ Core Contributor - 10+ merged contributions
👑 Community Leader - Helps other contributors regularly
```

### 📋 Code of Conduct

**We follow a simple code of conduct:**

#### ✅ Do:
- Be respectful and professional in all interactions
- Help newcomers get started with contributions
- Provide constructive feedback on pull requests
- Share knowledge and expertise with the community
- Follow project guidelines and conventions

#### ❌ Don't:
- Use discriminatory or offensive language
- Harass or bully community members  
- Share private information without permission
- Violate game server rules or terms of service
- Submit low-effort or spam contributions

### 🚨 Reporting Issues

**If you experience problems:**

1. **Technical Issues**: Create GitHub issue with details
2. **Community Issues**: Contact maintainers privately
3. **Security Vulnerabilities**: Email security@project-morningstar.org
4. **Harassment**: Report immediately via Discord or email

---

## 🎉 Ready to Contribute?

### 🚀 Your Next Steps:

1. **⭐ Star the repository** to show your support
2. **🍴 Fork the project** to your GitHub account  
3. **💬 Join our Discord** for real-time help and community
4. **🔍 Find a good first issue** to get started
5. **📖 Read the README.md** for project overview
6. **🛠️ Set up your development environment**
7. **🎯 Make your first contribution** and become part of the community!

### 💡 Contribution Ideas for Beginners:

- **Fix typos** in documentation or code comments
- **Add missing game data** for heroics, builds, or quests
- **Improve mobile responsiveness** of existing pages
- **Write user guides** for complex features  
- **Create example API usage** code snippets
- **Report bugs** through our feedback system
- **Suggest features** that would help the community

### 🌟 "The galaxy needs heroes like you!"

**Welcome to the SWGDB community!** Whether you're contributing data, code, documentation, or just helping other community members, **every contribution matters**.

Together, we're building the ultimate Star Wars Galaxies resource for players across all servers and emulators.

---

*Questions? Problems? Ideas?*  
💬 **Discord**: [Join our community](https://discord.gg/swgdb)  
🐛 **Issues**: [GitHub Issues](https://github.com/project-morningstar/Project-MorningStar/issues)  
💡 **Discussions**: [GitHub Discussions](https://github.com/project-morningstar/Project-MorningStar/discussions)  
📧 **Email**: contributors@project-morningstar.org

**May the Force be with you, and happy contributing!** ⭐✨
