module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'SWGDB Roadmap',
      eleventyNavigation: {
        key: 'Roadmap',
        order: 100
      }
    };
  }

  render() {
    return `
<section class="py-12 px-6 max-w-4xl mx-auto text-white">
  <h1 class="text-4xl font-bold mb-6">Roadmap</h1>
  <p class="text-gray-400 mb-8">Our development timeline and what's coming to SWGDB. Help shape our priorities by joining the community!</p>
  
  <div class="space-y-6">
    <div class="bg-gray-800 rounded-lg p-6 border border-green-500">
      <h2 class="text-xl font-bold text-green-400 mb-3">✅ Recently Completed</h2>
      <ul class="space-y-2 text-gray-300 list-disc pl-6">
        <li>GCW Calculator with planet control simulation</li>
        <li>Skill Calculator with dependency tracking</li>
        <li>Complete Tailwind CSS redesign</li>
        <li>Heroic encounter guides and loot tables</li>
        <li>Dropdown navigation with rich menus</li>
      </ul>
    </div>

    <div class="bg-gray-800 rounded-lg p-6 border border-yellow-500">
      <h2 class="text-xl font-bold text-yellow-400 mb-3">🔧 Currently In Progress</h2>
      <ul class="space-y-2 text-gray-300 list-disc pl-6">
        <li>Heroics loot population with community data</li>
        <li>Visual tweaks and mobile responsiveness</li>
        <li>Community feedback integration</li>
        <li>Performance optimizations</li>
      </ul>
    </div>

    <div class="bg-gray-800 rounded-lg p-6 border border-blue-500">
      <h2 class="text-xl font-bold text-blue-400 mb-3">🗃️ Coming Soon</h2>
      <ul class="space-y-2 text-gray-300 list-disc pl-6">
        <li>Player Rankings system (PVP, Master Crafter, Exploration)</li>
        <li>Interactive loot tracker with drop rate tracking</li>
        <li>Enhanced guide system with build templates</li>
        <li>Community submission system for data</li>
      </ul>
    </div>

    <div class="bg-gray-800 rounded-lg p-6 border border-purple-500">
      <h2 class="text-xl font-bold text-purple-400 mb-3">📦 Future Vision</h2>
      <ul class="space-y-2 text-gray-300 list-disc pl-6">
        <li>Live character dashboard (SWGTracker-style integration)</li>
        <li>Real-time server statistics and population data</li>
        <li>Advanced guild management tools</li>
        <li>Mobile app for iOS and Android</li>
        <li>API for third-party integrations</li>
      </ul>
    </div>

    <div class="bg-gray-800 rounded-lg p-6 border border-yellow-300">
      <h2 class="text-xl font-bold text-yellow-300 mb-3">💬 Help Shape Our Roadmap</h2>
      <p class="text-gray-300 mb-4">Your feedback drives our development priorities. Let us know what features matter most to you:</p>
      <div class="flex flex-wrap gap-4">
        <a href="/report/" class="inline-block px-6 py-3 bg-yellow-500 text-black font-bold rounded hover:bg-yellow-400 transition">
          Submit Feedback
        </a>
        <a href="https://discord.gg/swgrestoration" class="inline-block px-6 py-3 bg-blue-600 text-white font-bold rounded hover:bg-blue-500 transition">
          Join Discord
        </a>
      </div>
    </div>
  </div>
</section>
`;
  }
};