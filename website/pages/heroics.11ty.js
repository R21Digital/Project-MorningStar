module.exports = {
  layout: "base",
  title: "Heroics",
  description: "SWG Heroics - Complete guide to all heroic instances with strategies, loot tables, and boss tactics",
  tags: ["heroics", "instances", "bosses", "loot"],
  eleventyComputed: {
    heroics: async function() {
      // This will be populated by 11ty data cascade
      return [];
    }
  }
}; 