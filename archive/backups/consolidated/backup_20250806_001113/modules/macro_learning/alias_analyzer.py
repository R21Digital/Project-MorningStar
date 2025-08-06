"""Alias Analyzer for detailed analysis of alias configurations and patterns.

This module provides advanced analysis of alias usage patterns, dependencies,
and optimization recommendations.
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class AliasPattern:
    """Data class for representing an alias usage pattern."""
    pattern: str
    frequency: int
    examples: List[str]
    category: str
    complexity_score: float
    dependencies: List[str]

@dataclass
class AliasAnalysis:
    """Data class for alias analysis results."""
    total_aliases: int
    unique_patterns: int
    most_common_patterns: List[Tuple[str, int]]
    category_distribution: Dict[str, int]
    complexity_distribution: Dict[str, int]
    dependency_chains: List[List[str]]
    optimization_suggestions: List[str]
    critical_missing: List[str]

class AliasAnalyzer:
    """Analyzer for alias configurations and usage patterns."""
    
    def __init__(self):
        """Initialize the alias analyzer."""
        self.aliases = {}
        self.patterns = {}
        self.dependency_graph = defaultdict(set)
        self.category_stats = defaultdict(int)
        self.complexity_scores = {}
        
        # Pattern recognition rules
        self.pattern_rules = {
            "combat": [
                r"/attack",
                r"/heal",
                r"/buff",
                r"/defend",
                r"/flee"
            ],
            "travel": [
                r"/travel",
                r"/goto",
                r"/follow",
                r"/waypoint"
            ],
            "crafting": [
                r"/craft",
                r"/harvest",
                r"/survey",
                r"/resource"
            ],
            "social": [
                r"/say",
                r"/tell",
                r"/group",
                r"/guild"
            ],
            "utility": [
                r"/loot",
                r"/inventory",
                r"/equipment",
                r"/status"
            ]
        }
        
        # Complexity scoring factors
        self.complexity_factors = {
            "command_length": 0.3,
            "parameter_count": 0.2,
            "nested_commands": 0.3,
            "special_chars": 0.2
        }
        
        log_event("[ALIAS_ANALYZER] Initialized alias analyzer")
    
    def load_aliases(self, aliases: Dict[str, Any]) -> None:
        """Load aliases for analysis.
        
        Parameters
        ----------
        aliases : dict
            Dictionary of alias name to alias data
        """
        self.aliases = aliases
        log_event(f"[ALIAS_ANALYZER] Loaded {len(aliases)} aliases for analysis")
    
    def analyze_patterns(self) -> Dict[str, AliasPattern]:
        """Analyze alias patterns and categorize them.
        
        Returns
        -------
        dict
            Dictionary of pattern name to AliasPattern object
        """
        pattern_counter = Counter()
        pattern_examples = defaultdict(list)
        
        for alias_name, alias_data in self.aliases.items():
            # Handle both Alias objects and dictionaries
            if hasattr(alias_data, 'command'):
                command = alias_data.command
            else:
                command = alias_data.get('command', '')
            
            # Categorize by pattern
            category = self._categorize_command(command)
            pattern = self._extract_pattern(command)
            
            pattern_counter[pattern] += 1
            pattern_examples[pattern].append(alias_name)
            
            # Update category stats
            self.category_stats[category] += 1
        
        # Create AliasPattern objects
        for pattern, frequency in pattern_counter.items():
            examples = pattern_examples[pattern][:5]  # Limit to 5 examples
            category = self._categorize_pattern(pattern)
            complexity = self._calculate_complexity(pattern)
            dependencies = self._extract_dependencies(pattern)
            
            self.patterns[pattern] = AliasPattern(
                pattern=pattern,
                frequency=frequency,
                examples=examples,
                category=category,
                complexity_score=complexity,
                dependencies=dependencies
            )
        
        log_event(f"[ALIAS_ANALYZER] Analyzed {len(self.patterns)} unique patterns")
        return self.patterns
    
    def _categorize_command(self, command: str) -> str:
        """Categorize a command based on its content.
        
        Parameters
        ----------
        command : str
            Command to categorize
            
        Returns
        -------
        str
            Category name
        """
        command_lower = command.lower()
        
        for category, patterns in self.pattern_rules.items():
            for pattern in patterns:
                if re.search(pattern, command_lower):
                    return category
        
        return "general"
    
    def _extract_pattern(self, command: str) -> str:
        """Extract a pattern from a command.
        
        Parameters
        ----------
        command : str
            Command to extract pattern from
            
        Returns
        -------
        str
            Extracted pattern
        """
        # Replace specific values with placeholders
        pattern = re.sub(r'\b\w+\b', '{param}', command)
        pattern = re.sub(r'\d+', '{number}', pattern)
        pattern = re.sub(r'"[^"]*"', '{string}', pattern)
        
        return pattern.strip()
    
    def _categorize_pattern(self, pattern: str) -> str:
        """Categorize a pattern.
        
        Parameters
        ----------
        pattern : str
            Pattern to categorize
            
        Returns
        -------
        str
            Category name
        """
        pattern_lower = pattern.lower()
        
        for category, patterns in self.pattern_rules.items():
            for rule_pattern in patterns:
                if re.search(rule_pattern, pattern_lower):
                    return category
        
        return "general"
    
    def _calculate_complexity(self, pattern: str) -> float:
        """Calculate complexity score for a pattern.
        
        Parameters
        ----------
        pattern : str
            Pattern to analyze
            
        Returns
        -------
        float
            Complexity score (0.0 to 1.0)
        """
        score = 0.0
        
        # Command length factor
        length_score = min(len(pattern) / 50.0, 1.0)
        score += length_score * self.complexity_factors["command_length"]
        
        # Parameter count factor
        param_count = len(re.findall(r'\{[^}]+\}', pattern))
        param_score = min(param_count / 5.0, 1.0)
        score += param_score * self.complexity_factors["parameter_count"]
        
        # Nested commands factor
        nested_count = pattern.count(';') + pattern.count('|')
        nested_score = min(nested_count / 3.0, 1.0)
        score += nested_score * self.complexity_factors["nested_commands"]
        
        # Special characters factor
        special_chars = len(re.findall(r'[^\w\s{}]', pattern))
        special_score = min(special_chars / 10.0, 1.0)
        score += special_score * self.complexity_factors["special_chars"]
        
        return min(score, 1.0)
    
    def _extract_dependencies(self, pattern: str) -> List[str]:
        """Extract dependencies from a pattern.
        
        Parameters
        ----------
        pattern : str
            Pattern to analyze
            
        Returns
        -------
        list
            List of dependency names
        """
        dependencies = []
        
        # Look for common dependency patterns
        dependency_patterns = [
            r'\{target\}',
            r'\{player\}',
            r'\{item\}',
            r'\{location\}',
            r'\{skill\}'
        ]
        
        for dep_pattern in dependency_patterns:
            if re.search(dep_pattern, pattern):
                dep_name = dep_pattern.strip('{}')
                dependencies.append(dep_name)
        
        return dependencies
    
    def find_dependency_chains(self) -> List[List[str]]:
        """Find chains of dependent aliases.
        
        Returns
        -------
        list
            List of dependency chains
        """
        chains = []
        visited = set()
        
        for alias_name, alias_data in self.aliases.items():
            if alias_name in visited:
                continue
            
            chain = self._build_dependency_chain(alias_name, visited)
            if len(chain) > 1:  # Only include chains with dependencies
                chains.append(chain)
        
        return chains
    
    def _build_dependency_chain(self, alias_name: str, visited: Set[str]) -> List[str]:
        """Build a dependency chain starting from an alias.
        
        Parameters
        ----------
        alias_name : str
            Starting alias name
        visited : set
            Set of visited aliases
            
        Returns
        -------
        list
            Dependency chain
        """
        if alias_name in visited:
            return []
        
        visited.add(alias_name)
        chain = [alias_name]
        
        alias_data = self.aliases.get(alias_name, {})
        # Handle both Alias objects and dictionaries
        if hasattr(alias_data, 'command'):
            command = alias_data.command
        else:
            command = alias_data.get('command', '')
        
        # Find aliases referenced in this command
        referenced_aliases = re.findall(r'/\w+', command)
        
        for ref_alias in referenced_aliases:
            ref_name = ref_alias[1:]  # Remove leading slash
            if ref_name in self.aliases and ref_name not in visited:
                sub_chain = self._build_dependency_chain(ref_name, visited)
                chain.extend(sub_chain)
        
        return chain
    
    def generate_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions based on analysis.
        
        Returns
        -------
        list
            List of optimization suggestions
        """
        suggestions = []
        
        # Analyze pattern frequency
        most_common = sorted(
            [(pattern, data.frequency) for pattern, data in self.patterns.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        if most_common:
            suggestions.append(f"Most common pattern: {most_common[0][0]} (used {most_common[0][1]} times)")
        
        # Analyze complexity
        complex_patterns = [
            (pattern, data.complexity_score) 
            for pattern, data in self.patterns.items() 
            if data.complexity_score > 0.7
        ]
        
        if complex_patterns:
            suggestions.append(f"Found {len(complex_patterns)} complex patterns that could be simplified")
        
        # Analyze dependencies
        dependency_chains = self.find_dependency_chains()
        long_chains = [chain for chain in dependency_chains if len(chain) > 3]
        
        if long_chains:
            suggestions.append(f"Found {len(long_chains)} long dependency chains that could be optimized")
        
        # Category analysis
        underused_categories = [
            category for category, count in self.category_stats.items()
            if count < 3
        ]
        
        if underused_categories:
            suggestions.append(f"Underused categories: {', '.join(underused_categories)}")
        
        return suggestions
    
    def find_missing_critical_aliases(self, critical_aliases: List[str]) -> List[str]:
        """Find missing critical aliases.
        
        Parameters
        ----------
        critical_aliases : list
            List of critical alias names
            
        Returns
        -------
        list
            List of missing critical aliases
        """
        missing = []
        
        for alias_name in critical_aliases:
            if alias_name not in self.aliases:
                missing.append(alias_name)
        
        return missing
    
    def get_comprehensive_analysis(self) -> AliasAnalysis:
        """Get comprehensive alias analysis.
        
        Returns
        -------
        AliasAnalysis
            Complete analysis results
        """
        # Analyze patterns if not already done
        if not self.patterns:
            self.analyze_patterns()
        
        # Get most common patterns
        most_common_patterns = sorted(
            [(pattern, data.frequency) for pattern, data in self.patterns.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        # Get complexity distribution
        complexity_distribution = {
            "simple": len([p for p in self.patterns.values() if p.complexity_score < 0.3]),
            "medium": len([p for p in self.patterns.values() if 0.3 <= p.complexity_score < 0.7]),
            "complex": len([p for p in self.patterns.values() if p.complexity_score >= 0.7])
        }
        
        # Find dependency chains
        dependency_chains = self.find_dependency_chains()
        
        # Generate optimization suggestions
        optimization_suggestions = self.generate_optimization_suggestions()
        
        # Find missing critical aliases
        critical_aliases = [
            "/heal", "/buff", "/travel", "/craft", "/loot",
            "/follow", "/attack", "/defend", "/flee"
        ]
        missing_critical = self.find_missing_critical_aliases(critical_aliases)
        
        return AliasAnalysis(
            total_aliases=len(self.aliases),
            unique_patterns=len(self.patterns),
            most_common_patterns=most_common_patterns,
            category_distribution=dict(self.category_stats),
            complexity_distribution=complexity_distribution,
            dependency_chains=dependency_chains,
            optimization_suggestions=optimization_suggestions,
            critical_missing=missing_critical
        )
    
    def save_analysis_report(self, analysis: AliasAnalysis, file_path: str = None) -> str:
        """Save alias analysis report to JSON file.
        
        Parameters
        ----------
        analysis : AliasAnalysis
            Analysis results to save
        file_path : str, optional
            Path to save file
            
        Returns
        -------
        str
            Path to saved file
        """
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"logs/alias_analysis_{timestamp}.json"
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis": asdict(analysis),
            "patterns": {pattern: asdict(data) for pattern, data in self.patterns.items()},
            "aliases": self.aliases
        }
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        log_event(f"[ALIAS_ANALYZER] Saved analysis report to {file_path}")
        return file_path 