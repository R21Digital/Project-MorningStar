module.exports = class {
  data() {
    return {
      layout: 'base.11ty.js',
      title: 'Report an Issue',
      eleventyNavigation: {
        key: 'Report Issue',
        order: 99
      }
    };
  }

  render() {
    return `
<section class="py-12 px-6 max-w-3xl mx-auto text-white">
  <h1 class="text-4xl font-bold mb-6">Report an Issue</h1>
  <p class="text-gray-400 mb-8">Found a bug or incorrect data? Let us know so we can fix it fast.</p>

  <form class="bg-gray-800 p-6 rounded-lg shadow-md space-y-6">
    <div>
      <label class="block mb-2 text-sm font-medium text-gray-300">Your Name (optional)</label>
      <input type="text" class="w-full px-4 py-2 rounded bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Ex: Commander Zarn">
    </div>
    <div>
      <label class="block mb-2 text-sm font-medium text-gray-300">Issue Summary</label>
      <input type="text" class="w-full px-4 py-2 rounded bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Example: Loot not matching for Acklay">
    </div>
    <div>
      <label class="block mb-2 text-sm font-medium text-gray-300">Detailed Description</label>
      <textarea rows="5" maxlength="1000" class="w-full px-4 py-2 rounded bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="Describe what went wrong or what needs fixing..."></textarea>
    </div>
    <div>
      <button type="submit" class="bg-yellow-500 hover:bg-yellow-400 text-black font-semibold px-6 py-2 rounded transition">Submit Report</button>
    </div>
  </form>
</section>
`;
  }
};