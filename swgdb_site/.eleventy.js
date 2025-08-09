module.exports = function(eleventyConfig) {
  // Ignore problematic files  
  eleventyConfig.ignores.add("pages/my-sessions.html");
  eleventyConfig.ignores.add("pages/heroics.11ty.js");
  eleventyConfig.ignores.add("pages/admin/bugs.11ty.js");
  
  // Collections for guides
  eleventyConfig.addCollection("guides", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/**/*.md")
      .sort((a, b) => {
        return new Date(b.data.createdAt) - new Date(a.data.createdAt);
      });
  });

  // Collection for each guide category
  eleventyConfig.addCollection("combatBuilds", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/combat-builds/*.md");
  });

  eleventyConfig.addCollection("crafterBuilds", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/crafter-builds/*.md");
  });

  eleventyConfig.addCollection("entertainerBuilds", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/entertainer-builds/*.md");
  });

  eleventyConfig.addCollection("forceSensitiveBuilds", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/force-sensitive-builds/*.md");
  });

  eleventyConfig.addCollection("pvpFundamentals", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/pvp-fundamentals/*.md");
  });

  eleventyConfig.addCollection("groupPvpTactics", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/group-pvp-tactics/*.md");
  });

  eleventyConfig.addCollection("baseBusting", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/base-busting/*.md");
  });

  eleventyConfig.addCollection("creditFarming", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/credit-farming/*.md");
  });

  eleventyConfig.addCollection("resourceHarvesting", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/resource-harvesting/*.md");
  });

  eleventyConfig.addCollection("rareLootFarming", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/rare-loot-farming/*.md");
  });

  eleventyConfig.addCollection("newPlayerGuides", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/new-player-guides/*.md");
  });

  eleventyConfig.addCollection("characterMaximization", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/character-maximization/*.md");
  });

  eleventyConfig.addCollection("professionOverviews", function(collectionApi) {
    return collectionApi.getFilteredByGlob("content/guides/profession-overviews/*.md");
  });

  // Copy assets and styles
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("js");
  eleventyConfig.addPassthroughCopy("assets");

  // Configure directories
  return {
    dir: {
      input: ".",
      includes: "_includes",
      data: "_data",
      output: "_site"
    },
    templateFormats: ["md", "njk", "html", "liquid", "11ty.js"]
  };
};