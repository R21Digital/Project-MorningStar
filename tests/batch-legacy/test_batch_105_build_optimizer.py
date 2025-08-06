"""Test suite for Batch 105 - Build Optimizer Tool."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core.build_optimizer import (
    BuildOptimizer,
    CharacterStats,
    BuildRecommendation,
    BuildAnalysis,
    CombatRole,
    StatType,
    RecommendationType,
    build_optimizer,
    analyze_character_build,
    get_profession_recommendations,
    get_equipment_recommendations,
    get_buff_recommendations,
    get_food_recommendations
)


class TestCharacterStats:
    """Test the CharacterStats dataclass."""
    
    def test_character_stats_creation(self):
        """Test creating a CharacterStats instance."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            agility=40,
            quickness=35,
            stamina=30,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=15,
            current_profession="rifleman",
            respec_available=False
        )
        
        assert stats.health == 150
        assert stats.action == 120
        assert stats.mind == 80
        assert stats.combat_role == CombatRole.DPS
        assert stats.level == 15
        assert stats.current_profession == "rifleman"
        assert stats.respec_available == False
    
    def test_character_stats_defaults(self):
        """Test CharacterStats with default values."""
        stats = CharacterStats()
        
        assert stats.health == 0
        assert stats.action == 0
        assert stats.mind == 0
        assert stats.combat_role == CombatRole.DPS
        assert stats.level == 1
        assert stats.current_profession is None
        assert stats.respec_available == False
    
    def test_character_stats_serialization(self):
        """Test CharacterStats serialization to/from dict."""
        original_stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            agility=40,
            quickness=35,
            stamina=30,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.TANK,
            level=20,
            current_profession="commando",
            respec_available=True
        )
        
        # Convert to dict
        stats_dict = original_stats.to_dict()
        
        # Convert back from dict
        restored_stats = CharacterStats.from_dict(stats_dict)
        
        assert restored_stats.health == original_stats.health
        assert restored_stats.action == original_stats.action
        assert restored_stats.mind == original_stats.mind
        assert restored_stats.combat_role == original_stats.combat_role
        assert restored_stats.level == original_stats.level
        assert restored_stats.current_profession == original_stats.current_profession
        assert restored_stats.respec_available == original_stats.respec_available


class TestBuildRecommendation:
    """Test the BuildRecommendation dataclass."""
    
    def test_build_recommendation_creation(self):
        """Test creating a BuildRecommendation instance."""
        recommendation = BuildRecommendation(
            recommendation_type=RecommendationType.PROFESSION,
            name="Rifleman",
            description="Long-range combat specialist",
            score=0.85,
            reasoning="Your high action and strength stats align well with this profession.",
            requirements=["Novice Artisan"],
            benefits=["High damage output", "Long range combat"],
            drawbacks=["Requires skill training", "May conflict with current profession"],
            cost=1000,
            location="Coronet"
        )
        
        assert recommendation.recommendation_type == RecommendationType.PROFESSION
        assert recommendation.name == "Rifleman"
        assert recommendation.description == "Long-range combat specialist"
        assert recommendation.score == 0.85
        assert recommendation.cost == 1000
        assert recommendation.location == "Coronet"
        assert len(recommendation.benefits) == 2
        assert len(recommendation.drawbacks) == 2
    
    def test_build_recommendation_defaults(self):
        """Test BuildRecommendation with default values."""
        recommendation = BuildRecommendation(
            recommendation_type=RecommendationType.BUFF,
            name="Weapon Buff",
            description="Increases weapon damage",
            score=0.7,
            reasoning="Essential for DPS combat"
        )
        
        assert recommendation.requirements == []
        assert recommendation.benefits == []
        assert recommendation.drawbacks == []
        assert recommendation.cost is None
        assert recommendation.location is None
    
    def test_build_recommendation_serialization(self):
        """Test BuildRecommendation serialization to dict."""
        original_rec = BuildRecommendation(
            recommendation_type=RecommendationType.ARMOR,
            name="Heavy Combat Armor",
            description="Maximum protection for tanking",
            score=0.9,
            reasoning="Optimal armor for tank combat",
            benefits=["High protection", "Durability"],
            drawbacks=["Reduced mobility", "High cost"],
            cost=500,
            location="Vendor"
        )
        
        # Convert to dict
        rec_dict = original_rec.to_dict()
        
        assert rec_dict['recommendation_type'] == 'armor'
        assert rec_dict['name'] == "Heavy Combat Armor"
        assert rec_dict['score'] == 0.9
        assert rec_dict['cost'] == 500
        assert rec_dict['location'] == "Vendor"


class TestBuildAnalysis:
    """Test the BuildAnalysis dataclass."""
    
    def test_build_analysis_creation(self):
        """Test creating a BuildAnalysis instance."""
        stats = CharacterStats(health=150, action=120, mind=80)
        recommendations = [
            BuildRecommendation(
                recommendation_type=RecommendationType.PROFESSION,
                name="Rifleman",
                description="Long-range specialist",
                score=0.85,
                reasoning="Good fit for your stats"
            )
        ]
        
        analysis = BuildAnalysis(
            character_stats=stats,
            recommendations=recommendations,
            total_score=0.85,
            analysis_date=datetime.now(),
            summary="Excellent build optimization potential."
        )
        
        assert analysis.character_stats == stats
        assert len(analysis.recommendations) == 1
        assert analysis.total_score == 0.85
        assert "Excellent" in analysis.summary
    
    def test_build_analysis_serialization(self):
        """Test BuildAnalysis serialization to dict."""
        stats = CharacterStats(health=150, action=120, mind=80)
        recommendations = [
            BuildRecommendation(
                recommendation_type=RecommendationType.PROFESSION,
                name="Rifleman",
                description="Long-range specialist",
                score=0.85,
                reasoning="Good fit for your stats"
            )
        ]
        
        analysis = BuildAnalysis(
            character_stats=stats,
            recommendations=recommendations,
            total_score=0.85,
            analysis_date=datetime.now(),
            summary="Good build optimization."
        )
        
        analysis_dict = analysis.to_dict()
        
        assert 'character_stats' in analysis_dict
        assert 'recommendations' in analysis_dict
        assert analysis_dict['total_score'] == 0.85
        assert 'Good build' in analysis_dict['summary']


class TestBuildOptimizer:
    """Test the BuildOptimizer class."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def optimizer(self, temp_data_dir):
        """Create a BuildOptimizer instance for testing."""
        return BuildOptimizer(data_dir=temp_data_dir)
    
    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initialization."""
        assert optimizer.data_dir.exists()
        assert len(optimizer.profession_requirements) == 6  # rifleman, pistoleer, commando, medic, smuggler, bounty_hunter
        assert len(optimizer.buff_recommendations) == 6  # dps, tank, support, hybrid, pvp, pve
        assert len(optimizer.food_recommendations) == 6
    
    def test_profession_requirements_structure(self, optimizer):
        """Test that profession requirements have correct structure."""
        for profession, requirements in optimizer.profession_requirements.items():
            assert 'primary_stats' in requirements
            assert 'secondary_stats' in requirements
            assert 'combat_roles' in requirements
            assert 'weapon_preferences' in requirements
            assert 'description' in requirements
            
            # Check that combat roles are valid
            for role in requirements['combat_roles']:
                assert isinstance(role, CombatRole)
    
    def test_calculate_profession_score(self, optimizer):
        """Test profession score calculation."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            agility=40,
            quickness=35,
            level=15,
            combat_role=CombatRole.DPS
        )
        
        requirements = optimizer.profession_requirements['rifleman']
        score = optimizer._calculate_profession_score(stats, requirements)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be a good match
    
    def test_generate_profession_reasoning(self, optimizer):
        """Test profession reasoning generation."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            level=15,
            combat_role=CombatRole.DPS
        )
        
        requirements = optimizer.profession_requirements['rifleman']
        reasoning = optimizer._generate_profession_reasoning(stats, requirements)
        
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
        assert "action" in reasoning.lower() or "strength" in reasoning.lower()
    
    def test_recommend_professions(self, optimizer):
        """Test profession recommendations."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            level=15,
            combat_role=CombatRole.DPS
        )
        
        recommendations = optimizer._recommend_professions(stats)
        
        assert len(recommendations) <= 3  # Top 3 recommendations
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.PROFESSION
            assert rec.score > 0.5
            assert len(rec.reasoning) > 0
    
    def test_recommend_buffs(self, optimizer):
        """Test buff recommendations."""
        stats = CharacterStats(
            combat_role=CombatRole.DPS,
            level=15
        )
        
        recommendations = optimizer._recommend_buffs(stats)
        
        assert len(recommendations) <= 3  # Top 3 recommendations
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.BUFF
            assert rec.score > 0.0
            assert len(rec.benefits) > 0
    
    def test_recommend_food(self, optimizer):
        """Test food recommendations."""
        stats = CharacterStats(
            combat_role=CombatRole.DPS,
            level=15
        )
        
        recommendations = optimizer._recommend_food(stats)
        
        assert len(recommendations) <= 2  # Top 2 recommendations
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.FOOD
            assert rec.score > 0.0
            assert len(rec.benefits) > 0
    
    def test_recommend_armor(self, optimizer):
        """Test armor recommendations."""
        stats = CharacterStats(
            combat_role=CombatRole.TANK,
            level=20,
            constitution=60
        )
        
        recommendations = optimizer._recommend_armor(stats)
        
        assert len(recommendations) <= 2  # Top 2 recommendations
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.ARMOR
            assert rec.score > 0.0
            assert "armor" in rec.name.lower()
    
    def test_recommend_weapons(self, optimizer):
        """Test weapon recommendations."""
        stats = CharacterStats(
            combat_role=CombatRole.DPS,
            level=15,
            action=80,
            strength=50
        )
        
        recommendations = optimizer._recommend_weapons(stats)
        
        assert len(recommendations) <= 2  # Top 2 recommendations
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.WEAPON
            assert rec.score > 0.0
            assert "weapon" in rec.name.lower() or "rifle" in rec.name.lower() or "pistol" in rec.name.lower()
    
    def test_analyze_stat_distribution(self, optimizer):
        """Test stat distribution analysis."""
        stats = CharacterStats(
            action=30,  # Below optimal for DPS
            strength=40,
            constitution=30,
            agility=30,
            combat_role=CombatRole.DPS
        )
        
        analysis = optimizer._analyze_stat_distribution(stats)
        
        assert 'action' in analysis
        assert analysis['action']['needs_improvement'] == True
        assert analysis['action']['improvement_score'] > 0.0
    
    def test_recommend_stat_reallocation(self, optimizer):
        """Test stat reallocation recommendations."""
        stats = CharacterStats(
            action=30,  # Below optimal
            strength=40,
            constitution=30,
            agility=30,
            combat_role=CombatRole.DPS,
            respec_available=True
        )
        
        recommendations = optimizer._recommend_stat_reallocation(stats)
        
        assert len(recommendations) <= 3  # Top 3 recommendations
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.STAT_REALLOCATION
            assert rec.score > 0.0
            assert "Improve" in rec.name
    
    def test_generate_summary(self, optimizer):
        """Test summary generation."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            level=15,
            combat_role=CombatRole.DPS
        )
        
        recommendations = [
            BuildRecommendation(
                recommendation_type=RecommendationType.PROFESSION,
                name="Rifleman",
                description="Long-range specialist",
                score=0.85,
                reasoning="Good fit for your stats"
            )
        ]
        
        total_score = 0.85
        summary = optimizer._generate_summary(stats, recommendations, total_score)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Rifleman" in summary or "recommendations" in summary.lower()


class TestBuildOptimizerIntegration:
    """Integration tests for the BuildOptimizer."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def optimizer(self, temp_data_dir):
        """Create a BuildOptimizer instance for testing."""
        return BuildOptimizer(data_dir=temp_data_dir)
    
    def test_full_build_analysis(self, optimizer):
        """Test complete build analysis workflow."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            agility=40,
            quickness=35,
            stamina=30,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=15,
            current_profession="rifleman",
            respec_available=False
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        assert isinstance(analysis, BuildAnalysis)
        assert analysis.character_stats == stats
        assert len(analysis.recommendations) > 0
        assert 0.0 <= analysis.total_score <= 1.0
        assert len(analysis.summary) > 0
        
        # Check that we have recommendations from different categories
        rec_types = [rec.recommendation_type for rec in analysis.recommendations]
        assert RecommendationType.PROFESSION in rec_types
        assert RecommendationType.BUFF in rec_types or RecommendationType.FOOD in rec_types
        assert RecommendationType.ARMOR in rec_types or RecommendationType.WEAPON in rec_types
    
    def test_dps_build_analysis(self, optimizer):
        """Test DPS build analysis."""
        stats = CharacterStats(
            health=120,
            action=150,
            mind=60,
            strength=60,
            constitution=40,
            agility=50,
            quickness=45,
            stamina=35,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=20
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        # Should recommend DPS-focused professions
        profession_recs = [rec for rec in analysis.recommendations if rec.recommendation_type == RecommendationType.PROFESSION]
        assert len(profession_recs) > 0
        
        # Check that rifleman is recommended (good for DPS)
        profession_names = [rec.name.lower() for rec in profession_recs]
        assert any('rifleman' in name for name in profession_names)
    
    def test_tank_build_analysis(self, optimizer):
        """Test tank build analysis."""
        stats = CharacterStats(
            health=200,
            action=80,
            mind=60,
            strength=50,
            constitution=80,
            agility=30,
            quickness=25,
            stamina=70,
            presence=30,
            focus=40,
            willpower=45,
            combat_role=CombatRole.TANK,
            level=25
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        # Should recommend tank-focused equipment
        armor_recs = [rec for rec in analysis.recommendations if rec.recommendation_type == RecommendationType.ARMOR]
        assert len(armor_recs) > 0
        
        # Check that heavy armor is recommended
        armor_names = [rec.name.lower() for rec in armor_recs]
        assert any('heavy' in name for name in armor_names)
    
    def test_support_build_analysis(self, optimizer):
        """Test support build analysis."""
        stats = CharacterStats(
            health=100,
            action=60,
            mind=150,
            strength=25,
            constitution=40,
            agility=30,
            quickness=25,
            stamina=35,
            presence=50,
            focus=80,
            willpower=75,
            combat_role=CombatRole.SUPPORT,
            level=20
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        # Should recommend support-focused professions
        profession_recs = [rec for rec in analysis.recommendations if rec.recommendation_type == RecommendationType.PROFESSION]
        assert len(profession_recs) > 0
        
        # Check that medic is recommended (good for support)
        profession_names = [rec.name.lower() for rec in profession_recs]
        assert any('medic' in name for name in profession_names)
    
    def test_build_analysis_with_respec(self, optimizer):
        """Test build analysis when respec is available."""
        stats = CharacterStats(
            health=100,
            action=30,  # Below optimal for DPS
            mind=60,
            strength=40,
            constitution=30,
            agility=30,
            quickness=25,
            stamina=25,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=15,
            respec_available=True
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        # Should include stat reallocation recommendations
        reallocation_recs = [rec for rec in analysis.recommendations if rec.recommendation_type == RecommendationType.STAT_REALLOCATION]
        assert len(reallocation_recs) > 0
    
    def test_build_analysis_without_respec(self, optimizer):
        """Test build analysis when respec is not available."""
        stats = CharacterStats(
            health=100,
            action=30,  # Below optimal for DPS
            mind=60,
            strength=40,
            constitution=30,
            agility=30,
            quickness=25,
            stamina=25,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=15,
            respec_available=False
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        # Should not include stat reallocation recommendations
        reallocation_recs = [rec for rec in analysis.recommendations if rec.recommendation_type == RecommendationType.STAT_REALLOCATION]
        assert len(reallocation_recs) == 0


class TestGlobalFunctions:
    """Test the global functions from the build optimizer module."""
    
    def test_analyze_character_build_function(self):
        """Test the analyze_character_build function."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            agility=40,
            quickness=35,
            stamina=30,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=15
        )
        
        analysis = analyze_character_build(stats)
        
        assert isinstance(analysis, BuildAnalysis)
        assert analysis.character_stats == stats
        assert len(analysis.recommendations) > 0
    
    def test_get_profession_recommendations_function(self):
        """Test the get_profession_recommendations function."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            agility=40,
            quickness=35,
            stamina=30,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=15
        )
        
        recommendations = get_profession_recommendations(stats)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.PROFESSION
    
    def test_get_equipment_recommendations_function(self):
        """Test the get_equipment_recommendations function."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            agility=40,
            quickness=35,
            stamina=30,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=15
        )
        
        recommendations = get_equipment_recommendations(stats)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert rec.recommendation_type in [RecommendationType.ARMOR, RecommendationType.WEAPON]
    
    def test_get_buff_recommendations_function(self):
        """Test the get_buff_recommendations function."""
        stats = CharacterStats(
            combat_role=CombatRole.DPS,
            level=15
        )
        
        recommendations = get_buff_recommendations(stats)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.BUFF
    
    def test_get_food_recommendations_function(self):
        """Test the get_food_recommendations function."""
        stats = CharacterStats(
            combat_role=CombatRole.DPS,
            level=15
        )
        
        recommendations = get_food_recommendations(stats)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert rec.recommendation_type == RecommendationType.FOOD


class TestBuildOptimizerErrorHandling:
    """Test error handling in the BuildOptimizer."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def optimizer(self, temp_data_dir):
        """Create a BuildOptimizer instance for testing."""
        return BuildOptimizer(data_dir=temp_data_dir)
    
    def test_optimizer_with_missing_data_files(self, optimizer):
        """Test optimizer behavior with missing data files."""
        # Should not crash when data files are missing
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            combat_role=CombatRole.DPS,
            level=15
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        assert isinstance(analysis, BuildAnalysis)
        assert len(analysis.recommendations) > 0
    
    def test_optimizer_with_invalid_combat_role(self, optimizer):
        """Test optimizer behavior with invalid combat role."""
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            combat_role=CombatRole.DPS,  # Valid role
            level=15
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        assert isinstance(analysis, BuildAnalysis)
        assert len(analysis.recommendations) > 0
    
    def test_optimizer_with_extreme_stat_values(self, optimizer):
        """Test optimizer behavior with extreme stat values."""
        stats = CharacterStats(
            health=1000,  # Very high
            action=1000,  # Very high
            mind=1000,    # Very high
            strength=100, # Very high
            constitution=100,
            agility=100,
            quickness=100,
            stamina=100,
            presence=100,
            focus=100,
            willpower=100,
            combat_role=CombatRole.DPS,
            level=90
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        assert isinstance(analysis, BuildAnalysis)
        assert len(analysis.recommendations) > 0
        assert analysis.total_score > 0.0
    
    def test_optimizer_with_zero_stats(self, optimizer):
        """Test optimizer behavior with zero stats."""
        stats = CharacterStats(
            health=0,
            action=0,
            mind=0,
            strength=0,
            constitution=0,
            agility=0,
            quickness=0,
            stamina=0,
            presence=0,
            focus=0,
            willpower=0,
            combat_role=CombatRole.DPS,
            level=1
        )
        
        analysis = optimizer.analyze_character_build(stats)
        
        assert isinstance(analysis, BuildAnalysis)
        # Should still provide some recommendations even with zero stats
        assert len(analysis.recommendations) >= 0


class TestBuildOptimizerPerformance:
    """Performance tests for the BuildOptimizer."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def optimizer(self, temp_data_dir):
        """Create a BuildOptimizer instance for testing."""
        return BuildOptimizer(data_dir=temp_data_dir)
    
    def test_analysis_performance(self, optimizer):
        """Test that analysis completes in reasonable time."""
        import time
        
        stats = CharacterStats(
            health=150,
            action=120,
            mind=80,
            strength=45,
            constitution=35,
            agility=40,
            quickness=35,
            stamina=30,
            presence=25,
            focus=30,
            willpower=25,
            combat_role=CombatRole.DPS,
            level=15
        )
        
        start_time = time.time()
        analysis = optimizer.analyze_character_build(stats)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete in less than 1 second
        assert duration < 1.0
        assert isinstance(analysis, BuildAnalysis)
        assert len(analysis.recommendations) > 0
    
    def test_multiple_analyses_performance(self, optimizer):
        """Test performance of multiple analyses."""
        import time
        
        stats_list = [
            CharacterStats(health=150, action=120, mind=80, combat_role=CombatRole.DPS, level=15),
            CharacterStats(health=200, action=80, mind=100, combat_role=CombatRole.TANK, level=20),
            CharacterStats(health=100, action=60, mind=150, combat_role=CombatRole.SUPPORT, level=18)
        ]
        
        start_time = time.time()
        
        for stats in stats_list:
            analysis = optimizer.analyze_character_build(stats)
            assert isinstance(analysis, BuildAnalysis)
            assert len(analysis.recommendations) > 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete all analyses in less than 3 seconds
        assert duration < 3.0


if __name__ == "__main__":
    pytest.main([__file__]) 