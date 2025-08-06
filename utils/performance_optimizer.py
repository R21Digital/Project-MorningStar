#!/usr/bin/env python3
"""
Performance Optimization System for SWGDB
Handles caching, data loading optimization, and build performance
"""

import json
import os
import time
from functools import lru_cache, wraps
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import gzip
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheManager:
    """Manages application-level caching for improved performance"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
        self.cache_ttl = 3600  # 1 hour default TTL
        
    def get_cache_key(self, key: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        cache_data = f"{key}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def get_from_memory(self, key: str) -> Optional[Any]:
        """Get data from memory cache"""
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
            else:
                del self.memory_cache[key]
        return None
    
    def set_in_memory(self, key: str, data: Any):
        """Set data in memory cache"""
        self.memory_cache[key] = (data, time.time())
    
    def get_from_disk(self, key: str) -> Optional[Any]:
        """Get data from disk cache"""
        cache_file = self.cache_dir / f"{key}.json.gz"
        if cache_file.exists():
            try:
                with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
                    cache_entry = json.load(f)
                
                if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                    return cache_entry['data']
                else:
                    cache_file.unlink()  # Remove expired cache
            except Exception as e:
                logger.error(f"Error reading cache {key}: {e}")
        return None
    
    def set_on_disk(self, key: str, data: Any):
        """Set data in disk cache"""
        cache_file = self.cache_dir / f"{key}.json.gz"
        cache_entry = {
            'data': data,
            'timestamp': time.time(),
            'created': datetime.now().isoformat()
        }
        
        try:
            with gzip.open(cache_file, 'wt', encoding='utf-8') as f:
                json.dump(cache_entry, f, separators=(',', ':'))
        except Exception as e:
            logger.error(f"Error writing cache {key}: {e}")

# Global cache manager
cache_manager = CacheManager()

def cached(ttl: int = 3600, use_disk: bool = True):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        use_disk: Whether to use disk cache in addition to memory
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cache_manager.get_cache_key(func.__name__, *args, **kwargs)
            
            # Try memory cache first
            result = cache_manager.get_from_memory(cache_key)
            if result is not None:
                logger.debug(f"Cache hit (memory): {func.__name__}")
                return result
            
            # Try disk cache if enabled
            if use_disk:
                result = cache_manager.get_from_disk(cache_key)
                if result is not None:
                    logger.debug(f"Cache hit (disk): {func.__name__}")
                    # Also store in memory for faster access
                    cache_manager.set_in_memory(cache_key, result)
                    return result
            
            # Cache miss - execute function
            logger.debug(f"Cache miss: {func.__name__}")
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Store result in caches
            cache_manager.set_in_memory(cache_key, result)
            if use_disk:
                cache_manager.set_on_disk(cache_key, result)
            
            logger.info(f"Cached {func.__name__} (executed in {execution_time:.3f}s)")
            return result
        
        return wrapper
    return decorator

class DataLoader:
    """Optimized data loading for SWGDB content"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._file_mtimes = {}
    
    def _get_file_mtime(self, file_path: Path) -> float:
        """Get file modification time with caching"""
        try:
            return file_path.stat().st_mtime
        except OSError:
            return 0
    
    def _is_file_modified(self, file_path: Path) -> bool:
        """Check if file has been modified since last load"""
        current_mtime = self._get_file_mtime(file_path)
        cached_mtime = self._file_mtimes.get(str(file_path), 0)
        
        if current_mtime != cached_mtime:
            self._file_mtimes[str(file_path)] = current_mtime
            return True
        return False
    
    @cached(ttl=1800)  # 30 minutes cache
    def load_heroics(self) -> List[Dict[str, Any]]:
        """Load heroic instance data with caching"""
        heroics_dir = self.data_dir / "heroics"
        if not heroics_dir.exists():
            return []
        
        heroics = []
        for heroic_file in heroics_dir.glob("*.json"):
            try:
                with open(heroic_file, 'r', encoding='utf-8') as f:
                    heroic_data = json.load(f)
                    heroic_data['_file'] = heroic_file.name
                    heroic_data['_modified'] = datetime.fromtimestamp(
                        self._get_file_mtime(heroic_file)
                    ).isoformat()
                    heroics.append(heroic_data)
            except Exception as e:
                logger.error(f"Error loading heroic {heroic_file}: {e}")
        
        # Sort by name for consistent ordering
        heroics.sort(key=lambda x: x.get('name', ''))
        return heroics
    
    @cached(ttl=1800)
    def load_character_builds(self) -> List[Dict[str, Any]]:
        """Load character build data with caching"""
        builds_dir = self.data_dir / "builds"
        if not builds_dir.exists():
            return []
        
        builds = []
        for build_file in builds_dir.glob("*.json"):
            try:
                with open(build_file, 'r', encoding='utf-8') as f:
                    build_data = json.load(f)
                    build_data['_file'] = build_file.name
                    build_data['_id'] = build_file.stem
                    builds.append(build_data)
            except Exception as e:
                logger.error(f"Error loading build {build_file}: {e}")
        
        return builds
    
    @cached(ttl=3600)  # 1 hour cache for quest data
    def load_quest_data(self, planet: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Load quest data by planet with caching"""
        quests_dir = self.data_dir / "quests"
        if not quests_dir.exists():
            return {}
        
        quest_data = {}
        
        if planet:
            # Load specific planet
            planet_dir = quests_dir / planet
            if planet_dir.exists():
                quest_data[planet] = self._load_planet_quests(planet_dir)
        else:
            # Load all planets
            for planet_dir in quests_dir.iterdir():
                if planet_dir.is_dir():
                    planet_name = planet_dir.name
                    quest_data[planet_name] = self._load_planet_quests(planet_dir)
        
        return quest_data
    
    def _load_planet_quests(self, planet_dir: Path) -> List[Dict]:
        """Load quests for a specific planet"""
        quests = []
        for quest_file in planet_dir.glob("*.json"):
            try:
                with open(quest_file, 'r', encoding='utf-8') as f:
                    quest_data = json.load(f)
                    quest_data['_file'] = quest_file.name
                    quest_data['_planet'] = planet_dir.name
                    quests.append(quest_data)
            except Exception as e:
                logger.error(f"Error loading quest {quest_file}: {e}")
        
        return quests
    
    @cached(ttl=7200)  # 2 hours cache for static data
    def load_static_data(self) -> Dict[str, Any]:
        """Load static configuration and lookup data"""
        static_data = {
            'professions': [],
            'planets': [],
            'skill_trees': {},
            'item_categories': [],
            'difficulty_levels': ['Easy', 'Medium', 'Hard', 'Nightmare']
        }
        
        # Load professions data
        professions_file = self.data_dir / "professions" / "professions.json"
        if professions_file.exists():
            try:
                with open(professions_file, 'r', encoding='utf-8') as f:
                    static_data['professions'] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading professions: {e}")
        
        # Load planets data
        planets_file = self.data_dir / "planets.json"
        if planets_file.exists():
            try:
                with open(planets_file, 'r', encoding='utf-8') as f:
                    static_data['planets'] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading planets: {e}")
        
        return static_data

class AssetOptimizer:
    """Optimizes static assets for production"""
    
    def __init__(self, static_dir: str = "static"):
        self.static_dir = Path(static_dir)
    
    def optimize_images(self):
        """Optimize images for web delivery"""
        # This would use libraries like Pillow to optimize images
        # For now, just log what would be done
        logger.info("Image optimization would be performed here")
        
        image_dirs = ['images', 'icons', 'screenshots']
        for img_dir in image_dirs:
            img_path = self.static_dir / img_dir
            if img_path.exists():
                logger.info(f"Would optimize images in {img_path}")
    
    def minify_css(self):
        """Minify CSS files for production"""
        logger.info("CSS minification would be performed here")
    
    def minify_js(self):
        """Minify JavaScript files for production"""
        logger.info("JavaScript minification would be performed here")

# Global instances for easy import
data_loader = DataLoader()
asset_optimizer = AssetOptimizer()

def clear_all_caches():
    """Clear all caches - useful for development and testing"""
    cache_manager.memory_cache.clear()
    
    # Clear disk cache
    if cache_manager.cache_dir.exists():
        for cache_file in cache_manager.cache_dir.glob("*.json.gz"):
            try:
                cache_file.unlink()
                logger.info(f"Cleared cache: {cache_file.name}")
            except Exception as e:
                logger.error(f"Error clearing cache {cache_file}: {e}")

def get_cache_stats() -> Dict[str, Any]:
    """Get caching statistics for monitoring"""
    memory_count = len(cache_manager.memory_cache)
    
    disk_count = 0
    disk_size = 0
    if cache_manager.cache_dir.exists():
        cache_files = list(cache_manager.cache_dir.glob("*.json.gz"))
        disk_count = len(cache_files)
        disk_size = sum(f.stat().st_size for f in cache_files)
    
    return {
        'memory_cache_entries': memory_count,
        'disk_cache_entries': disk_count,
        'disk_cache_size_bytes': disk_size,
        'disk_cache_size_mb': round(disk_size / (1024 * 1024), 2),
        'cache_directory': str(cache_manager.cache_dir)
    }

if __name__ == '__main__':
    # Example usage and testing
    print("SWGDB Performance Optimizer")
    print("=" * 40)
    
    # Test data loading
    loader = DataLoader()
    
    print("Loading heroics data...")
    heroics = loader.load_heroics()
    print(f"Loaded {len(heroics)} heroics")
    
    print("Loading builds data...")
    builds = loader.load_character_builds()
    print(f"Loaded {len(builds)} builds")
    
    print("Cache statistics:")
    stats = get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")