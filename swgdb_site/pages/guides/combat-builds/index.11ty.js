module.exports = class {
  data() {
    return {
      title: "Combat Builds - SWGDB Guides",
      description: "PvP and PvE combat builds for Star Wars Galaxies Restoration",
      layout: "base.njk",
      permalink: "/guides/combat-builds/"
    };
  }

  render(data) {
    const combatBuilds = data.collections.combatBuilds || [];
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.title}</title>
    <meta name="description" content="${data.description}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #28a745;
            --dark-color: #333;
            --light-color: #f8f9fa;
        }

        .category-hero {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
        }

        .category-hero h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .category-hero p {
            font-size: 1.1rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }

        .breadcrumb-nav {
            background: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .breadcrumb {
            background: none;
            margin: 0;
            padding: 0;
        }

        .breadcrumb-item + .breadcrumb-item::before {
            content: ">";
            color: #666;
        }

        .guides-section {
            padding: 60px 0;
        }

        .guides-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }

        .guide-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }

        .guide-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border-color: var(--primary-color);
        }

        .guide-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 25px;
        }

        .guide-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .guide-author {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 15px;
        }

        .guide-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .guide-tag {
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .guide-content {
            padding: 25px;
        }

        .guide-summary {
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        .guide-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: #666;
        }

        .guide-date {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .guide-link {
            background: var(--primary-color);
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-block;
        }

        .guide-link:hover {
            background: var(--secondary-color);
            color: white;
            transform: scale(1.05);
        }

        .no-guides {
            text-align: center;
            padding: 60px 0;
            color: #666;
        }

        .no-guides i {
            font-size: 4rem;
            color: var(--primary-color);
            margin-bottom: 20px;
        }

        .back-link {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 20px;
        }

        .back-link:hover {
            background: rgba(255, 255, 255, 0.3);
            color: white;
        }

        @media (max-width: 768px) {
            .category-hero h1 {
                font-size: 2rem;
            }
            
            .guides-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="category-hero">
        <div class="container">
            <h1><i class="fas fa-sword"></i> Combat Builds</h1>
            <p>Optimized builds for PvP and PvE combat, including weapon specializations and tactical strategies</p>
            <a href="/guides/" class="back-link">
                <i class="fas fa-arrow-left"></i> Back to All Guides
            </a>
        </div>
    </div>

    <div class="breadcrumb-nav">
        <div class="container">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/">Home</a></li>
                    <li class="breadcrumb-item"><a href="/guides/">Guides</a></li>
                    <li class="breadcrumb-item active">Combat Builds</li>
                </ol>
            </nav>
        </div>
    </div>

    <div class="guides-section">
        <div class="container">
            ${combatBuilds.length > 0 ? `
                <div class="guides-grid">
                    ${combatBuilds.map(guide => `
                        <div class="guide-card">
                            <div class="guide-header">
                                <h3 class="guide-title">${guide.data.title}</h3>
                                ${guide.data.author ? `
                                    <div class="guide-author">
                                        <i class="fas fa-user"></i> by ${guide.data.author}
                                    </div>
                                ` : ''}
                                ${guide.data.tags && guide.data.tags.length > 0 ? `
                                    <div class="guide-tags">
                                        ${guide.data.tags.map(tag => `
                                            <span class="guide-tag">${tag}</span>
                                        `).join('')}
                                    </div>
                                ` : ''}
                            </div>
                            <div class="guide-content">
                                ${guide.data.summary ? `
                                    <p class="guide-summary">${guide.data.summary}</p>
                                ` : ''}
                                <div class="guide-meta">
                                    ${guide.data.createdAt ? `
                                        <div class="guide-date">
                                            <i class="fas fa-calendar"></i>
                                            ${new Date(guide.data.createdAt).toLocaleDateString('en-US', { 
                                                year: 'numeric', 
                                                month: 'long', 
                                                day: 'numeric' 
                                            })}
                                        </div>
                                    ` : ''}
                                </div>
                                <a href="${guide.url}" class="guide-link">
                                    Read Guide <i class="fas fa-arrow-right"></i>
                                </a>
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : `
                <div class="no-guides">
                    <i class="fas fa-sword"></i>
                    <h3>No Combat Builds Yet</h3>
                    <p>Combat builds are coming soon! Check back later for comprehensive PvP and PvE guides.</p>
                </div>
            `}
        </div>
    </div>
</body>
</html>
    `;
  }
};