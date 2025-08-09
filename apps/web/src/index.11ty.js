// src/index.11ty.js

module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'SWGDB - Star Wars Galaxies Database',
    };
  }

  render() {
    return `
<section class="py-12 px-6 max-w-6xl mx-auto text-white relative z-10">
  <!-- Hero Section -->
  <div class="holo-panel p-12 mb-12 text-center relative overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-br from-swg-cyan/10 to-transparent"></div>
          <div class="relative z-10">
        <div class="flex items-center justify-center mb-6">
          <img src="/public/images/swgdb-logo.png" alt="SWGDB Logo" class="h-24 md:h-32 w-auto opacity-90" />
        </div>
        <p class="text-2xl text-slate-300 mb-8 max-w-3xl mx-auto font-light">
          Your comprehensive database for Star Wars Galaxies Restoration
        </p>
      <div class="flex flex-wrap justify-center gap-6">
        <a href="/tools/skill-calculator" class="terminal-btn px-8 py-4 rounded-lg font-semibold text-lg hover:scale-105 transition-transform">
          <i class="fas fa-calculator mr-2"></i>Skill Calculator
        </a>
        <a href="/tools/gcw-calculator" class="terminal-btn px-8 py-4 rounded-lg font-semibold text-lg hover:scale-105 transition-transform">
          <i class="fas fa-globe mr-2"></i>GCW Calculator
        </a>
      </div>
    </div>
  </div>

  <!-- Core Tools Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
    <div class="holo-panel p-6 hover:scale-105 transition-all duration-300 group">
      <div class="text-4xl mb-4 text-swg-cyan group-hover:text-cyan-300 transition-colors">🧮</div>
      <h3 class="text-xl font-bold text-swg-cyan mb-3 tracking-wide">Skill Calculator</h3>
      <p class="text-slate-300 mb-4 font-light">Plan your character's skill progression with our comprehensive skill calculator. Track dependencies, optimize builds, and export your configurations.</p>
      <a href="/tools/skill-calculator" class="text-swg-cyan hover:text-cyan-300 font-semibold transition-colors group-hover:translate-x-2 inline-block">
        <i class="fas fa-arrow-right mr-2"></i>Try Calculator
      </a>
    </div>

    <div class="holo-panel p-6 hover:scale-105 transition-all duration-300 group">
      <div class="text-4xl mb-4 text-swg-cyan group-hover:text-cyan-300 transition-colors">🌟</div>
      <h3 class="text-xl font-bold text-swg-cyan mb-3 tracking-wide">GCW Calculator</h3>
      <p class="text-slate-300 mb-4 font-light">Simulate Galactic Civil War control across all planets and track faction dominance with real-time calculations.</p>
      <a href="/tools/gcw-calculator" class="text-swg-cyan hover:text-cyan-300 font-semibold transition-colors group-hover:translate-x-2 inline-block">
        <i class="fas fa-arrow-right mr-2"></i>Try Calculator
      </a>
    </div>

    <div class="holo-panel p-6 hover:scale-105 transition-all duration-300 group">
      <div class="text-4xl mb-4 text-swg-cyan group-hover:text-cyan-300 transition-colors">⚙️</div>
      <h3 class="text-xl font-bold text-swg-cyan mb-3 tracking-wide">Build Calculator</h3>
      <p class="text-slate-300 mb-4 font-light">Create and optimize character builds with our advanced build calculator. Test different configurations and share with the community.</p>
      <a href="/tools/build-calculator" class="text-swg-cyan hover:text-cyan-300 font-semibold transition-colors group-hover:translate-x-2 inline-block">
        <i class="fas fa-arrow-right mr-2"></i>Try Calculator
      </a>
    </div>

    <div class="holo-panel p-6 hover:scale-105 transition-all duration-300 group">
      <div class="text-4xl mb-4 text-swg-cyan group-hover:text-cyan-300 transition-colors">🛡️</div>
      <h3 class="text-xl font-bold text-swg-cyan mb-3 tracking-wide">Gear Optimizer</h3>
      <p class="text-slate-300 mb-4 font-light">Optimize your character's gear loadout with our intelligent gear optimizer. Find the best combinations for your playstyle.</p>
      <a href="/tools/gear-optimizer" class="text-swg-cyan hover:text-cyan-300 font-semibold transition-colors group-hover:translate-x-2 inline-block">
        <i class="fas fa-arrow-right mr-2"></i>Try Optimizer
      </a>
    </div>
  </div>

  <!-- Recent Updates -->
  <div class="holo-panel p-8">
    <h2 class="text-3xl font-bold text-white mb-8 text-center tracking-wide">
      <i class="fas fa-satellite-dish mr-3 text-swg-cyan"></i>Recent Updates
    </h2>
    <div class="space-y-6">
      <div class="border-l-4 border-swg-cyan pl-6 py-2 hover:bg-swg-cyan/10 transition-colors rounded-r-lg">
        <h3 class="font-semibold text-swg-cyan text-lg">Skill Calculator Enhanced</h3>
        <p class="text-slate-300 text-sm font-light">Added support for 5 professions with automatic dependency tracking and build export functionality.</p>
        <span class="text-xs text-slate-500 mt-2 inline-block">
          <i class="fas fa-clock mr-1"></i>1 week ago
        </span>
      </div>
      <div class="border-l-4 border-swg-orange pl-6 py-2 hover:bg-swg-orange/10 transition-colors rounded-r-lg">
        <h3 class="font-semibold text-swg-orange text-lg">GCW Calculator Released</h3>
        <p class="text-slate-300 text-sm font-light">New Galactic Civil War calculator with real-time planet control tracking and faction dominance analysis.</p>
        <span class="text-xs text-slate-500 mt-2 inline-block">
          <i class="fas fa-clock mr-1"></i>2 weeks ago
        </span>
      </div>
      <div class="border-l-4 border-swg-gold pl-6 py-2 hover:bg-swg-gold/10 transition-colors rounded-r-lg">
        <h3 class="font-semibold text-swg-gold text-lg">Site Redesign Complete</h3>
        <p class="text-slate-300 text-sm font-light">New SWG-themed design with improved navigation and authentic Star Wars Galaxies aesthetic.</p>
        <span class="text-xs text-slate-500 mt-2 inline-block">
          <i class="fas fa-clock mr-1"></i>3 weeks ago
        </span>
      </div>
    </div>
  </div>

  <!-- Quick Stats -->
  <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mt-12">
    <div class="holo-panel p-6 text-center">
      <div class="text-3xl font-bold text-swg-cyan mb-2">4</div>
      <div class="text-slate-400 text-sm font-light">Core Tools</div>
    </div>
    <div class="holo-panel p-6 text-center">
      <div class="text-3xl font-bold text-swg-orange mb-2">5+</div>
      <div class="text-slate-400 text-sm font-light">Professions Supported</div>
    </div>
    <div class="holo-panel p-6 text-center">
      <div class="text-3xl font-bold text-swg-gold mb-2">100%</div>
      <div class="text-slate-400 text-sm font-light">Free & Open Source</div>
    </div>
    <div class="holo-panel p-6 text-center">
      <div class="text-3xl font-bold text-swg-cyan mb-2">24/7</div>
      <div class="text-slate-400 text-sm font-light">Available</div>
    </div>
  </div>
</section>
`;
  }
};