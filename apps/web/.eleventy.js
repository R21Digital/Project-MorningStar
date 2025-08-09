const fs = require('fs');
const path = require('path');

module.exports = function(eleventyConfig) {
  // Ignore certain directories
  eleventyConfig.ignores.add("src/pages/_hidden/**/*");
  eleventyConfig.ignores.add("archive/**/*");
  eleventyConfig.ignores.add("swgdb_site/**/*");
  eleventyConfig.ignores.add("website/**/*");
  
  // Ignore content that's not part of the core tools focus
  eleventyConfig.ignores.add("src/heroics/**/*");
  eleventyConfig.ignores.add("src/guides/**/*");
  eleventyConfig.ignores.add("src/loot/**/*");
  eleventyConfig.ignores.add("src/pages/dev-tools/**/*");
  eleventyConfig.ignores.add("src/heroics.11ty.js");
  eleventyConfig.ignores.add("src/guides.11ty.js");
  
  // Add collection for loot data pagination
  eleventyConfig.addCollection('lootBosses', function(collectionApi) {
    const lootDir = './src/data/loot';
    if (!fs.existsSync(lootDir)) return [];
    
    const files = fs.readdirSync(lootDir).filter(file => file.endsWith('.json'));

    return files.map(filename => {
      const slug = filename.replace('.json', '');
      const data = require(`${lootDir}/${filename}`);
      return { ...data, slug };
    });
  });

  // Copy static assets
  eleventyConfig.addPassthroughCopy("src/assets");
  eleventyConfig.addPassthroughCopy("public");

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      layouts: "_includes/layouts",
      data: "_data"
    },
    templateFormats: ["njk", "md", "11ty.js"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};