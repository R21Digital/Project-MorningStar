# SEO Implementation Guide - SWGDB

This document provides a comprehensive guide for implementing and maintaining SEO for the Star Wars Galaxies Database (SWGDB) website.

## Table of Contents
- [Google Analytics Setup](#google-analytics-setup)
- [Google Search Console Setup](#google-search-console-setup)
- [SEO Configuration](#seo-configuration)
- [Verification Checklist](#verification-checklist)
- [Indexing Strategy](#indexing-strategy)
- [Performance Optimization](#performance-optimization)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Google Analytics Setup

### 1. Google Analytics 4 Configuration

The website uses Google Analytics 4 (GA4) with enhanced tracking capabilities:

**Analytics ID**: `G-Q4ZZ5SFJC0`

#### Key Features Implemented:
- ✅ Enhanced ecommerce tracking
- ✅ Custom dimensions for SWGDB-specific data
- ✅ User engagement tracking
- ✅ Core Web Vitals monitoring
- ✅ Error tracking and reporting
- ✅ Custom event tracking for:
  - Filter usage
  - Search queries
  - Navigation clicks
  - Form submissions
  - Tab interactions
  - Loot table interactions
  - Performance metrics

### 2. Custom Dimensions

| Dimension | Purpose |
|-----------|---------|
| `custom_dimension1` | User type (visitor, registered, admin) |
| `custom_dimension2` | Page category (Heroics, Loot, Builds, etc.) |
| `custom_dimension3` | Content type (HTML, API, Loot Data, etc.) |
| `custom_dimension4` | Heroic type (Axkva Min, IG-88, etc.) |
| `custom_dimension5` | Loot rarity (Common, Rare, Epic, Legendary) |

### 3. Event Tracking Implementation

```javascript
// Custom event tracking function
function trackSWGDBEvent(eventName, parameters = {}) {
    gtag('event', eventName, {
        event_category: 'SWGDB',
        event_label: window.location.pathname,
        page_category: getPageCategory(),
        content_type: getContentType(),
        ...parameters
    });
}
```

#### Tracked Events:
- `filter_used` - When users interact with filters
- `search_performed` - Search queries with debouncing
- `navigation_click` - Internal and external link clicks
- `form_submitted` - Form interactions
- `tab_clicked` - Tab navigation
- `loot_interaction` - Loot table interactions
- `page_performance` - Load time and Core Web Vitals
- `user_engagement` - Time on page and scroll depth
- `resource_error` - Failed resource loads
- `javascript_error` - JS errors for debugging

## Google Search Console Setup

### 1. Site Verification

Add the verification meta tag to the base layout:

```html
<meta name="google-site-verification" content="your-verification-code-here" />
```

### 2. Property Setup Steps

1. **Add Property**: Go to [Google Search Console](https://search.google.com/search-console)
2. **Choose URL Prefix**: Use `https://swgdb.com`
3. **Verify Ownership**: Use HTML meta tag method
4. **Submit Sitemap**: Submit `https://swgdb.com/sitemap.xml`
5. **Configure Settings**: Set preferred domain and crawl rate

### 3. Search Console Features to Configure

- ✅ Sitemap submission
- ✅ URL inspection tool
- ✅ Coverage reports
- ✅ Mobile usability
- ✅ Core Web Vitals
- ✅ Manual actions monitoring
- ✅ Security issues alerts

## SEO Configuration

### 1. Meta Tags Implementation

The base layout includes comprehensive meta tags:

```html
<!-- Basic SEO -->
<title>{{ title or "SWGDB - Star Wars Galaxies Database" }}</title>
<meta name="description" content="{{ description }}">
<meta name="keywords" content="{{ keywords }}">
<meta name="author" content="SWGDB Team">
<meta name="robots" content="index, follow">

<!-- Open Graph -->
<meta property="og:title" content="{{ title }}">
<meta property="og:description" content="{{ description }}">
<meta property="og:type" content="{{ ogType or 'website' }}">
<meta property="og:url" content="{{ canonicalUrl }}{{ page.url }}">
<meta property="og:image" content="{{ ogImage }}">

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ title }}">
<meta name="twitter:description" content="{{ description }}">
<meta name="twitter:image" content="{{ twitterImage }}">
```

### 2. Structured Data

JSON-LD structured data is implemented for:
- Website schema
- Organization schema
- Breadcrumb navigation
- Search functionality
- Article markup (for guides)

### 3. Canonical URLs

All pages include canonical URLs to prevent duplicate content:

```html
<link rel="canonical" href="{{ canonicalUrl }}{{ page.url }}">
```

## Verification Checklist

### Pre-Launch Checklist

#### Technical SEO
- [ ] Google Analytics 4 installed and configured
- [ ] Google Search Console property created
- [ ] HTML meta tag verification added
- [ ] Sitemap generated and accessible
- [ ] Robots.txt configured
- [ ] Canonical URLs implemented
- [ ] HTTPS enforced
- [ ] Mobile-responsive design
- [ ] Page speed optimized (< 3s load time)
- [ ] Core Web Vitals passing
- [ ] 404 error pages configured
- [ ] URL structure SEO-friendly

#### Content SEO
- [ ] Title tags optimized (50-60 characters)
- [ ] Meta descriptions compelling (150-160 characters)
- [ ] Header structure (H1, H2, H3) logical
- [ ] Image alt tags descriptive
- [ ] Internal linking strategy implemented
- [ ] Content quality and uniqueness verified

#### Social Media & Rich Snippets
- [ ] Open Graph tags implemented
- [ ] Twitter Cards configured
- [ ] Structured data markup added
- [ ] Social media profiles linked
- [ ] Rich snippets testing passed

### Post-Launch Verification

#### Google Search Console
- [ ] Property verified successfully
- [ ] Sitemap submitted and indexed
- [ ] No crawl errors reported
- [ ] Mobile usability issues resolved
- [ ] Core Web Vitals in "Good" status
- [ ] Manual actions clear

#### Analytics Verification
- [ ] Real-time data showing in GA4
- [ ] Custom events firing correctly
- [ ] Custom dimensions populated
- [ ] Conversion goals configured
- [ ] Audience segments defined

## Indexing Strategy

### 1. Priority Pages for Indexing

**High Priority (Index immediately)**:
- Homepage (`/`)
- Main category pages (`/heroics/`, `/loot/`, `/builds/`)
- Popular heroic guides (Axkva Min, IG-88)
- Getting started guides

**Medium Priority (Index within 1 week)**:
- Individual heroic pages
- Tool pages
- Build showcase pages
- Loot tracking pages

**Low Priority (Natural indexing)**:
- API documentation
- Admin pages (excluded from indexing)
- Temporary or test pages

### 2. Sitemap Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://swgdb.com/</loc>
    <lastmod>2025-01-16</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://swgdb.com/heroics/</loc>
    <lastmod>2025-01-16</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <!-- Additional pages... -->
</urlset>
```

### 3. Robots.txt Configuration

```
User-agent: *
Disallow: /admin/
Disallow: /api/private/
Disallow: /temp/
Disallow: /test/
Disallow: /_includes/
Disallow: /config/

Allow: /api/public/
Allow: /assets/
Allow: /css/
Allow: /js/

Sitemap: https://swgdb.com/sitemap.xml
```

## Performance Optimization

### 1. Core Web Vitals Targets

| Metric | Target | Current |
|--------|---------|---------|
| **Largest Contentful Paint (LCP)** | < 2.5s | Monitor |
| **First Input Delay (FID)** | < 100ms | Monitor |
| **Cumulative Layout Shift (CLS)** | < 0.1 | Monitor |

### 2. Optimization Techniques

#### Images
- Use WebP format with fallbacks
- Implement lazy loading
- Optimize image sizes and compression
- Use responsive images with srcset

#### CSS/JS
- Minify and compress assets
- Use critical CSS inlining
- Defer non-critical JavaScript
- Implement resource hints (preload, prefetch)

#### Caching
- Set appropriate cache headers
- Use CDN for static assets
- Implement service workers for offline functionality

### 3. Monitoring Tools

- **Google PageSpeed Insights**: Core Web Vitals monitoring
- **Google Analytics**: Real user metrics (RUM)
- **GTmetrix**: Performance analysis
- **Lighthouse**: Automated auditing

## Monitoring and Maintenance

### 1. Regular Monitoring Tasks

#### Weekly Tasks
- [ ] Check Google Search Console for new issues
- [ ] Review Core Web Vitals reports
- [ ] Monitor organic traffic trends
- [ ] Check for crawl errors

#### Monthly Tasks
- [ ] Analyze top-performing content
- [ ] Review and update meta descriptions
- [ ] Check for broken internal/external links
- [ ] Update sitemap if needed
- [ ] Review keyword rankings

#### Quarterly Tasks
- [ ] Comprehensive SEO audit
- [ ] Competitor analysis
- [ ] Content gap analysis
- [ ] Technical SEO review
- [ ] Update structured data markup

### 2. Key Performance Indicators (KPIs)

#### Traffic Metrics
- Organic search traffic growth
- Click-through rate (CTR) from search results
- Average session duration
- Pages per session
- Bounce rate improvement

#### Ranking Metrics
- Keyword ranking positions
- Featured snippet appearances
- Local search visibility
- Voice search optimization

#### Technical Metrics
- Core Web Vitals scores
- Mobile usability issues
- Page load speed improvements
- Crawl budget efficiency

### 3. Alert Configuration

Set up alerts for:
- Significant traffic drops (> 20%)
- Core Web Vitals issues
- Crawl errors increase
- Manual actions in Search Console
- Page speed regressions

## Troubleshooting Common Issues

### 1. Pages Not Indexing

**Possible Causes**:
- Robots.txt blocking
- No internal links pointing to page
- Duplicate content issues
- Low-quality content

**Solutions**:
- Submit URL for indexing in Search Console
- Add internal links from high-authority pages
- Improve content quality and uniqueness
- Check and fix canonical tags

### 2. Core Web Vitals Issues

**Common Problems**:
- Large images causing LCP issues
- Third-party scripts causing FID problems
- Layout shifts from ads or dynamic content

**Solutions**:
- Optimize and compress images
- Defer non-critical JavaScript
- Reserve space for dynamic content
- Use font-display: swap for web fonts

### 3. Analytics Not Tracking

**Checklist**:
- Verify GA4 tracking ID is correct
- Check if ad blockers are interfering
- Ensure gtag is loaded before custom events
- Test in browser developer tools

## Additional Resources

### Documentation Links
- [Google Analytics 4 Documentation](https://developers.google.com/analytics/devguides/collection/ga4)
- [Google Search Console Help](https://support.google.com/webmasters/)
- [Schema.org Documentation](https://schema.org/)
- [Core Web Vitals Guide](https://web.dev/vitals/)

### Tools and Testing
- [Google Search Console](https://search.google.com/search-console)
- [Google Analytics](https://analytics.google.com/)
- [PageSpeed Insights](https://pagespeed.web.dev/)
- [Rich Results Test](https://search.google.com/test/rich-results)
- [Mobile-Friendly Test](https://search.google.com/test/mobile-friendly)

### Contact Information

For SEO-related questions or issues:
- **Technical Lead**: SWGDB Team
- **Documentation**: This file (docs/SEO.md)
- **Issue Tracking**: Use the bug tracker at `/admin/bugs`

---

**Last Updated**: January 16, 2025  
**Version**: 1.0  
**Next Review**: April 16, 2025