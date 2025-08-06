# Google Search Console & Analytics Setup Guide

## Overview
This guide provides step-by-step instructions for setting up Google Analytics v4 and Google Search Console for the SWGDB website.

## Prerequisites
- Google account
- Access to SWGDB website files
- Domain ownership verification

## Step 1: Google Analytics Setup

### 1.1 Create Google Analytics Property
1. Go to [Google Analytics](https://analytics.google.com/)
2. Click "Start measuring"
3. Create a new property for SWGDB
4. Choose "Web" as the platform
5. Enter property details:
   - Property name: `SWGDB`
   - Reporting time zone: `UTC`
   - Currency: `USD`

### 1.2 Get Measurement ID
1. After creating the property, you'll receive a Measurement ID
2. Format: `G-XXXXXXXXX`
3. Copy this ID for use in the analytics code

### 1.3 Update Analytics Code
1. Open `swgdb_site/_includes/analytics.html`
2. Replace `G-XXXXXXX` with your actual Measurement ID
3. Save the file

## Step 2: Google Search Console Setup

### 2.1 Add Property
1. Go to [Google Search Console](https://search.google.com/search-console)
2. Click "Add property"
3. Enter your domain: `swgdb.com`
4. Choose "Domain" property type

### 2.2 Verify Ownership
1. Choose "HTML tag" verification method
2. Copy the verification code provided
3. Open `swgdb_site/_includes/analytics.html`
4. Replace `your-verification-code-here` with the actual verification code
5. Save the file

### 2.3 Submit Sitemap
1. In Google Search Console, go to "Sitemaps"
2. Click "Add a new sitemap"
3. Enter: `https://swgdb.com/sitemap.xml`
4. Click "Submit"

## Step 3: Enhanced Analytics Configuration

### 3.1 Custom Dimensions Setup
In Google Analytics, set up these custom dimensions:
1. Go to Admin > Custom Definitions > Custom Dimensions
2. Create the following dimensions:
   - `user_type` (User scope)
   - `page_category` (Hit scope)
   - `content_type` (Hit scope)

### 3.2 Custom Events Setup
The analytics code includes these custom events:
- `filter_used` - Tracks filter button usage
- `search_performed` - Tracks search functionality
- `navigation_click` - Tracks link clicks
- `form_submitted` - Tracks form submissions
- `page_load_time` - Tracks performance
- `user_engagement` - Tracks time on page
- `page_exit` - Tracks exit behavior

## Step 4: SEO Optimization

### 4.1 Meta Tags
The analytics include file adds these SEO elements:
- Meta description
- Open Graph tags
- Twitter Card tags
- Structured data (JSON-LD)

### 4.2 Robots.txt
The robots.txt file is configured to:
- Allow crawling of all public pages
- Disallow admin and private areas
- Reference the sitemap

### 4.3 Sitemap
The sitemap.xml includes:
- All public pages with proper priorities
- Last modification dates
- Change frequency indicators

## Step 5: Testing & Validation

### 5.1 Analytics Testing
1. Deploy the updated files
2. Visit the website
3. Check Google Analytics Real-Time reports
4. Verify events are being tracked

### 5.2 Search Console Testing
1. Use Google Search Console's URL Inspection tool
2. Test a few key pages
3. Verify indexing status
4. Check for any crawl errors

### 5.3 SEO Testing
1. Use Google's Rich Results Test
2. Validate structured data
3. Check mobile-friendliness
4. Test page speed

## Step 6: Monitoring & Maintenance

### 6.1 Regular Monitoring
- Check Google Analytics weekly for traffic patterns
- Monitor Search Console for crawl errors
- Review search performance monthly
- Track user engagement metrics

### 6.2 Maintenance Tasks
- Update sitemap.xml when new pages are added
- Refresh meta descriptions periodically
- Monitor for broken links
- Update analytics code as needed

## Troubleshooting

### Common Issues
1. **Analytics not tracking**: Check Measurement ID is correct
2. **Search Console not verifying**: Ensure verification code is in head section
3. **Sitemap errors**: Validate XML format
4. **Crawl errors**: Check robots.txt configuration

### Debug Tools
- Google Analytics Debugger (Chrome extension)
- Google Search Console URL Inspection
- Google PageSpeed Insights
- Google Mobile-Friendly Test

## Performance Optimization

### 6.1 Analytics Performance
- Analytics code loads asynchronously
- Minimal impact on page load times
- Efficient event tracking

### 6.2 SEO Performance
- Optimized meta tags
- Proper heading structure
- Fast loading times
- Mobile-responsive design

## Security Considerations

### 6.1 Data Privacy
- Analytics respects user privacy
- No personally identifiable information collected
- Compliant with GDPR requirements

### 6.2 Access Control
- Limit Google Analytics access to necessary users
- Use Google Search Console's access management
- Regular security reviews

## Future Enhancements

### 6.1 Advanced Analytics
- Enhanced ecommerce tracking
- User journey analysis
- A/B testing integration
- Custom dashboards

### 6.2 SEO Improvements
- Advanced structured data
- AMP page support
- Core Web Vitals optimization
- International SEO

## Support Resources

### 6.1 Documentation
- [Google Analytics Help](https://support.google.com/analytics/)
- [Google Search Console Help](https://support.google.com/webmasters/)
- [Google SEO Guide](https://developers.google.com/search/docs)

### 6.2 Tools
- Google Analytics
- Google Search Console
- Google PageSpeed Insights
- Google Mobile-Friendly Test
- Google Rich Results Test

## Contact Information
For technical support or questions about this setup:
- Email: support@swgdb.com
- Documentation: https://docs.swgdb.com
- GitHub: https://github.com/swgdb/swgdb-site 