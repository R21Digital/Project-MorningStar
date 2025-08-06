const fs = require('fs');
const path = require('path');
const glob = require('glob');
const matter = require('gray-matter');

/**
 * Sitemap Generator for MorningStar SEO Enhancement System
 * Automatically generates XML sitemaps with intelligent priority and changefreq detection
 */
class SitemapGenerator {
    constructor(options = {}) {
        this.siteUrl = options.siteUrl || 'https://morningstar-swg.com';
        this.outputDir = options.outputDir || './dist';
        this.sourceDir = options.sourceDir || './src';
        this.seoConfig = options.seoConfig || require('../_data/seo.json');
        this.pages = [];
        this.lastmod = new Date().toISOString().split('T')[0];
    }

    /**
     * Scan directory for pages and extract metadata
     */
    async scanPages() {
        console.log('🔍 Scanning pages for sitemap generation...');
        
        const patterns = [
            `${this.sourceDir}/**/*.md`,
            `${this.sourceDir}/**/*.njk`,
            `${this.sourceDir}/**/*.html`,
            `${this.sourceDir}/**/*.liquid`
        ];

        const files = [];
        for (const pattern of patterns) {
            const matched = glob.sync(pattern, { ignore: this.seoConfig.sitemap.exclude });
            files.push(...matched);
        }

        console.log(`📄 Found ${files.length} potential pages`);

        for (const file of files) {
            try {
                const content = fs.readFileSync(file, 'utf8');
                const parsed = matter(content);
                const page = this.processPage(file, parsed);
                
                if (page && !this.isExcluded(page.url)) {
                    this.pages.push(page);
                }
            } catch (error) {
                console.warn(`⚠️  Warning: Could not process ${file}: ${error.message}`);
            }
        }

        console.log(`✅ Processed ${this.pages.length} pages for sitemap`);
        return this.pages;
    }

    /**
     * Process individual page and extract SEO metadata
     */
    processPage(filePath, parsed) {
        const relativePath = path.relative(this.sourceDir, filePath);
        const data = parsed.data || {};
        
        // Skip if explicitly excluded
        if (data.sitemap === false || data.robots === 'noindex') {
            return null;
        }

        // Generate URL from file path
        let url = this.generateUrl(relativePath, data);
        
        // Determine priority based on URL pattern and frontmatter
        const priority = this.calculatePriority(url, data);
        
        // Determine change frequency
        const changefreq = this.determineChangeFreq(url, data);
        
        // Get last modified date
        const lastmod = this.getLastModified(filePath, data);

        return {
            url,
            priority,
            changefreq,
            lastmod,
            title: data.title || '',
            description: data.description || '',
            keywords: data.keywords || [],
            images: this.extractImages(parsed.content, data),
            alternates: data.alternates || []
        };
    }

    /**
     * Generate URL from file path
     */
    generateUrl(relativePath, data) {
        // Use permalink if specified
        if (data.permalink) {
            return data.permalink;
        }

        // Convert file path to URL
        let url = relativePath
            .replace(/\\/g, '/') // Windows path fix
            .replace(/\.(md|njk|html|liquid)$/, '') // Remove extensions
            .replace(/\/index$/, '/') // Handle index files
            .replace(/^\.\//, '/'); // Ensure leading slash

        // Ensure it starts with /
        if (!url.startsWith('/')) {
            url = '/' + url;
        }

        // Handle root index
        if (url === '/index') {
            url = '/';
        }

        return url;
    }

    /**
     * Calculate page priority based on URL patterns and metadata
     */
    calculatePriority(url, data) {
        // Use explicit priority if set
        if (data.priority !== undefined) {
            return parseFloat(data.priority);
        }

        // Homepage gets highest priority
        if (url === '/') {
            return 1.0;
        }

        // Check predefined patterns
        const priorities = this.seoConfig.sitemap.priority;
        
        if (url.match(/^\/(features|download|getting-started)/)) {
            return priorities.main_features || 0.9;
        }
        
        if (url.match(/^\/(guides|docs|tutorials)/)) {
            return priorities.guides || 0.8;
        }
        
        if (url.match(/^\/(blog|news|updates)/)) {
            return priorities.blog || 0.7;
        }

        return priorities.static || 0.5;
    }

    /**
     * Determine change frequency based on URL patterns and metadata
     */
    determineChangeFreq(url, data) {
        // Use explicit changefreq if set
        if (data.changefreq) {
            return data.changefreq;
        }

        const changefreqs = this.seoConfig.sitemap.changefreq;

        // Homepage
        if (url === '/') {
            return changefreqs.homepage || 'daily';
        }

        // Dynamic content areas
        if (url.match(/^\/(blog|news|updates)/)) {
            return changefreqs.blog || 'daily';
        }

        // Feature pages
        if (url.match(/^\/(features|guides)/)) {
            return changefreqs.features || 'weekly';
        }

        // Static pages
        return changefreqs.static || 'monthly';
    }

    /**
     * Get last modified date
     */
    getLastModified(filePath, data) {
        // Use explicit date if set
        if (data.lastmod || data.date) {
            const date = new Date(data.lastmod || data.date);
            return date.toISOString().split('T')[0];
        }

        // Use file modification time
        try {
            const stats = fs.statSync(filePath);
            return stats.mtime.toISOString().split('T')[0];
        } catch (error) {
            return this.lastmod;
        }
    }

    /**
     * Extract images from content and frontmatter
     */
    extractImages(content, data) {
        const images = [];

        // Add featured image
        if (data.image || data.featured_image) {
            images.push({
                url: data.image || data.featured_image,
                title: data.image_alt || data.title || '',
                caption: data.image_caption || ''
            });
        }

        // Extract images from content (basic regex)
        const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
        let match;
        while ((match = imageRegex.exec(content)) !== null) {
            images.push({
                url: match[2],
                title: match[1] || '',
                caption: ''
            });
        }

        return images;
    }

    /**
     * Check if URL should be excluded
     */
    isExcluded(url) {
        const excludePatterns = this.seoConfig.sitemap.exclude || [];
        
        return excludePatterns.some(pattern => {
            if (pattern.includes('*')) {
                const regex = new RegExp(pattern.replace(/\*/g, '.*'));
                return regex.test(url);
            }
            return url.includes(pattern);
        });
    }

    /**
     * Generate XML sitemap
     */
    generateXML() {
        console.log('🔧 Generating XML sitemap...');

        const xml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
            ''
        ];

        // Sort pages by priority (descending) then by URL
        this.pages.sort((a, b) => {
            if (b.priority !== a.priority) {
                return b.priority - a.priority;
            }
            return a.url.localeCompare(b.url);
        });

        for (const page of this.pages) {
            xml.push('  <url>');
            xml.push(`    <loc>${this.siteUrl}${page.url}</loc>`);
            xml.push(`    <lastmod>${page.lastmod}</lastmod>`);
            xml.push(`    <changefreq>${page.changefreq}</changefreq>`);
            xml.push(`    <priority>${page.priority.toFixed(1)}</priority>`);

            // Add image information
            for (const image of page.images) {
                xml.push('    <image:image>');
                xml.push(`      <image:loc>${this.getAbsoluteUrl(image.url)}</image:loc>`);
                if (image.title) {
                    xml.push(`      <image:title><![CDATA[${image.title}]]></image:title>`);
                }
                if (image.caption) {
                    xml.push(`      <image:caption><![CDATA[${image.caption}]]></image:caption>`);
                }
                xml.push('    </image:image>');
            }

            xml.push('  </url>');
            xml.push('');
        }

        xml.push('</urlset>');
        
        return xml.join('\n');
    }

    /**
     * Convert relative URL to absolute
     */
    getAbsoluteUrl(url) {
        if (url.startsWith('http')) {
            return url;
        }
        if (url.startsWith('/')) {
            return this.siteUrl + url;
        }
        return this.siteUrl + '/' + url;
    }

    /**
     * Generate robots.txt content
     */
    generateRobotsTxt() {
        console.log('🤖 Generating robots.txt...');

        const rules = this.seoConfig.robots.rules || [];
        return rules.join('\n') + '\n';
    }

    /**
     * Generate sitemap index for multiple sitemaps
     */
    generateSitemapIndex(sitemaps) {
        console.log('📋 Generating sitemap index...');

        const xml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            ''
        ];

        for (const sitemap of sitemaps) {
            xml.push('  <sitemap>');
            xml.push(`    <loc>${this.siteUrl}/${sitemap.filename}</loc>`);
            xml.push(`    <lastmod>${sitemap.lastmod || this.lastmod}</lastmod>`);
            xml.push('  </sitemap>');
            xml.push('');
        }

        xml.push('</sitemapindex>');
        
        return xml.join('\n');
    }

    /**
     * Write sitemap files to output directory
     */
    async writeSitemaps() {
        // Ensure output directory exists
        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true });
        }

        const sitemapPath = path.join(this.outputDir, 'sitemap.xml');
        const robotsPath = path.join(this.outputDir, 'robots.txt');

        // Write main sitemap
        const sitemapXML = this.generateXML();
        fs.writeFileSync(sitemapPath, sitemapXML, 'utf8');
        console.log(`✅ Sitemap written to ${sitemapPath}`);

        // Write robots.txt
        const robotsTxt = this.generateRobotsTxt();
        fs.writeFileSync(robotsPath, robotsTxt, 'utf8');
        console.log(`✅ Robots.txt written to ${robotsPath}`);

        // Generate additional sitemaps if pages > 50000
        if (this.pages.length > 50000) {
            await this.generateMultipleSitemaps();
        }

        return {
            sitemap: sitemapPath,
            robots: robotsPath,
            pages: this.pages.length
        };
    }

    /**
     * Generate multiple sitemaps for large sites
     */
    async generateMultipleSitemaps() {
        const chunkSize = 50000;
        const chunks = [];
        
        for (let i = 0; i < this.pages.length; i += chunkSize) {
            chunks.push(this.pages.slice(i, i + chunkSize));
        }

        const sitemaps = [];
        
        for (let i = 0; i < chunks.length; i++) {
            const originalPages = this.pages;
            this.pages = chunks[i];
            
            const filename = `sitemap-${i + 1}.xml`;
            const filepath = path.join(this.outputDir, filename);
            const xml = this.generateXML();
            
            fs.writeFileSync(filepath, xml, 'utf8');
            console.log(`✅ Sitemap chunk ${i + 1} written to ${filepath}`);
            
            sitemaps.push({
                filename,
                lastmod: this.lastmod
            });
        }

        // Restore original pages
        this.pages = this.pages.flat();

        // Generate sitemap index
        const indexXML = this.generateSitemapIndex(sitemaps);
        const indexPath = path.join(this.outputDir, 'sitemap.xml');
        fs.writeFileSync(indexPath, indexXML, 'utf8');
        console.log(`✅ Sitemap index written to ${indexPath}`);
    }

    /**
     * Generate complete sitemap
     */
    async generate() {
        console.log('🚀 Starting sitemap generation...');
        
        try {
            await this.scanPages();
            const result = await this.writeSitemaps();
            
            console.log(`🎉 Sitemap generation completed successfully!`);
            console.log(`📊 Generated sitemap with ${result.pages} pages`);
            
            return result;
        } catch (error) {
            console.error('❌ Sitemap generation failed:', error);
            throw error;
        }
    }

    /**
     * Get sitemap statistics
     */
    getStats() {
        const stats = {
            totalPages: this.pages.length,
            priorities: {},
            changefreqs: {},
            lastGenerated: new Date().toISOString()
        };

        for (const page of this.pages) {
            // Count priorities
            const priority = page.priority.toString();
            stats.priorities[priority] = (stats.priorities[priority] || 0) + 1;

            // Count change frequencies
            stats.changefreqs[page.changefreq] = (stats.changefreqs[page.changefreq] || 0) + 1;
        }

        return stats;
    }
}

// Export for use in build scripts
module.exports = SitemapGenerator;

// CLI usage
if (require.main === module) {
    const generator = new SitemapGenerator({
        siteUrl: process.env.SITE_URL || 'https://morningstar-swg.com',
        outputDir: process.env.OUTPUT_DIR || './dist',
        sourceDir: process.env.SOURCE_DIR || './src'
    });

    generator.generate()
        .then(result => {
            console.log('📈 Sitemap Statistics:');
            console.log(JSON.stringify(generator.getStats(), null, 2));
        })
        .catch(error => {
            console.error('Failed to generate sitemap:', error);
            process.exit(1);
        });
}