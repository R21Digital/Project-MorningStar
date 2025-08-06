#!/usr/bin/env python3
"""
MS11 Batch 092 - Public Blog & SEO Guide Generator Demo

This script demonstrates the blog system functionality including:
- Data ingestion from various sources
- Automatic blog post generation
- Blog post management
- Statistics and analytics
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.blog_engine import blog_manager, BlogPost, BlogDataIngestion

def demo_data_ingestion():
    """Demonstrate data ingestion functionality."""
    print("=== Data Ingestion Demo ===")
    
    # Create data ingestion instance
    data_ingestion = BlogDataIngestion()
    
    # Ingest all data
    ingested_data = data_ingestion.ingest_all_data()
    
    print(f"Ingested {len(ingested_data)} data categories:")
    for category, data in ingested_data.items():
        if isinstance(data, dict):
            print(f"  - {category}: {len(data)} items")
        elif isinstance(data, list):
            print(f"  - {category}: {len(data)} items")
        else:
            print(f"  - {category}: {type(data).__name__}")
    
    return ingested_data

def demo_post_generation():
    """Demonstrate automatic post generation."""
    print("\n=== Post Generation Demo ===")
    
    # Generate a daily post
    post = blog_manager.generate_daily_post()
    
    if post:
        print(f"Generated post: {post.title}")
        print(f"  - ID: {post.post_id}")
        print(f"  - Category: {post.category}")
        print(f"  - Status: {post.status}")
        print(f"  - Word count: {post.word_count}")
        print(f"  - Tags: {', '.join(post.tags)}")
        print(f"  - Excerpt: {post.excerpt[:100]}...")
        
        # Save the post
        success = blog_manager.create_post(post)
        if success:
            print("  ✓ Post saved successfully")
        else:
            print("  ✗ Failed to save post")
    else:
        print("Failed to generate post")

def demo_post_management():
    """Demonstrate blog post management."""
    print("\n=== Post Management Demo ===")
    
    # List all posts
    posts = blog_manager.list_posts()
    print(f"Found {len(posts)} posts")
    
    if posts:
        # Show first post details
        post = posts[0]
        print(f"First post: {post.title}")
        print(f"  - Status: {post.status}")
        print(f"  - Views: {post.view_count}")
        print(f"  - Created: {post.created_at}")
        
        # Update the post
        success = blog_manager.update_post(
            post.post_id,
            view_count=post.view_count + 1
        )
        if success:
            print("  ✓ Post updated successfully")
        else:
            print("  ✗ Failed to update post")
        
        # Publish the post if it's a draft
        if post.status == 'draft':
            success = blog_manager.publish_post(post.post_id)
            if success:
                print("  ✓ Post published successfully")
            else:
                print("  ✗ Failed to publish post")

def demo_blog_statistics():
    """Demonstrate blog statistics."""
    print("\n=== Blog Statistics Demo ===")
    
    stats = blog_manager.get_blog_stats()
    
    print(f"Blog Statistics:")
    print(f"  - Total posts: {stats.total_posts}")
    print(f"  - Published posts: {stats.published_posts}")
    print(f"  - Draft posts: {stats.draft_posts}")
    print(f"  - Total views: {stats.total_views}")
    print(f"  - Total shares: {stats.total_shares}")
    print(f"  - Average read time: {stats.average_read_time:.1f} minutes")
    print(f"  - Most popular category: {stats.most_popular_category}")
    print(f"  - Most popular tags: {', '.join(stats.most_popular_tags[:5])}")
    print(f"  - Last post date: {stats.last_post_date}")

def demo_manual_post_creation():
    """Demonstrate manual post creation."""
    print("\n=== Manual Post Creation Demo ===")
    
    # Create a manual post
    post = BlogPost(
        post_id=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        title="Demo Blog Post - SWGDB Blog System",
        content="""
# Demo Blog Post

This is a demo blog post created to test the SWGDB blog system.

## Features Tested

- **Post Creation**: Manual post creation with metadata
- **Content Management**: Markdown content support
- **SEO Optimization**: Built-in SEO fields
- **Statistics Tracking**: View and share counting

## Community Impact

The SWGDB blog system helps the Star Wars Galaxies community by:

- Sharing weekly statistics and insights
- Providing quest and collection guides
- Highlighting popular macros and builds
- Improving search visibility for SWG content

*May the Force be with you!*
        """,
        excerpt="A demonstration of the SWGDB blog system capabilities.",
        category="general",
        tags=["demo", "blog", "swgdb", "testing"],
        status="draft",
        seo_title="Demo Blog Post - SWGDB Blog System",
        seo_description="A demonstration of the SWGDB blog system capabilities for the Star Wars Galaxies community.",
        seo_keywords=["SWG", "blog", "demo", "Star Wars Galaxies", "community"]
    )
    
    # Save the post
    success = blog_manager.create_post(post)
    if success:
        print(f"Created demo post: {post.title}")
        print(f"  - ID: {post.post_id}")
        print(f"  - Status: {post.status}")
        print(f"  - Word count: {post.word_count}")
    else:
        print("Failed to create demo post")

def demo_post_operations():
    """Demonstrate various post operations."""
    print("\n=== Post Operations Demo ===")
    
    # Get all posts
    posts = blog_manager.list_posts()
    
    if posts:
        post = posts[0]
        print(f"Working with post: {post.title}")
        
        # Test view count increment
        original_views = post.view_count
        post.view_count += 1
        success = blog_manager.create_post(post)  # Save updated post
        if success:
            print(f"  ✓ Incremented view count: {original_views} → {post.view_count}")
        else:
            print("  ✗ Failed to increment view count")
        
        # Test post retrieval
        retrieved_post = blog_manager.get_post(post.post_id)
        if retrieved_post:
            print(f"  ✓ Successfully retrieved post: {retrieved_post.title}")
        else:
            print("  ✗ Failed to retrieve post")
        
        # Test post deletion (only for demo posts)
        if post.post_id.startswith("demo_"):
            success = blog_manager.delete_post(post.post_id)
            if success:
                print(f"  ✓ Deleted demo post: {post.post_id}")
            else:
                print("  ✗ Failed to delete demo post")

def demo_data_analysis():
    """Demonstrate data analysis for blog generation."""
    print("\n=== Data Analysis Demo ===")
    
    # Create data ingestion instance
    data_ingestion = BlogDataIngestion()
    ingested_data = data_ingestion.ingest_all_data()
    
    # Analyze session statistics
    session_stats = ingested_data.get('session_stats', {})
    if session_stats:
        print("Session Statistics Analysis:")
        print(f"  - Total sessions: {session_stats.get('total_sessions', 0)}")
        print(f"  - Average duration: {session_stats.get('average_session_duration', 0):.1f} minutes")
        print(f"  - Total credits earned: {session_stats.get('total_credits_earned', 0):,}")
        print(f"  - Total XP gained: {session_stats.get('total_xp_gained', 0):,}")
        
        # Show top cities
        top_cities = session_stats.get('top_cities', [])
        if top_cities:
            print("  - Top cities:")
            for city, count in top_cities[:3]:
                print(f"    * {city}: {count} visits")
        
        # Show top planets
        top_planets = session_stats.get('top_planets', [])
        if top_planets:
            print("  - Top planets:")
            for planet, count in top_planets[:3]:
                print(f"    * {planet}: {count} visits")
    
    # Analyze other data sources
    for category, data in ingested_data.items():
        if category != 'session_stats' and isinstance(data, dict):
            print(f"  - {category}: {len(data)} items available")

def main():
    """Run the complete blog system demo."""
    print("MS11 Batch 092 - Public Blog & SEO Guide Generator Demo")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_data_ingestion()
        demo_post_generation()
        demo_post_management()
        demo_blog_statistics()
        demo_manual_post_creation()
        demo_post_operations()
        demo_data_analysis()
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("\nBlog system features demonstrated:")
        print("✓ Data ingestion from multiple sources")
        print("✓ Automatic blog post generation")
        print("✓ Manual post creation and editing")
        print("✓ Post management (CRUD operations)")
        print("✓ Blog statistics and analytics")
        print("✓ SEO optimization features")
        print("✓ View tracking and analytics")
        
        print("\nNext steps:")
        print("1. Access the blog at: http://localhost:5000/blog")
        print("2. Generate daily posts using the dashboard")
        print("3. Create manual posts for specific content")
        print("4. Monitor blog statistics and engagement")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 