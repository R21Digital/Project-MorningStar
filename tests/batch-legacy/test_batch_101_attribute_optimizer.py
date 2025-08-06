"""Test suite for Batch 101 - Attribute Optimizer Engine.

This test suite covers:
- Unit tests for the AttributeOptimizer class
- Integration tests for build optimization
- API endpoint tests
- Error handling and edge cases
- Data validation and serialization
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.attribute_optimizer import (
    AttributeOptimizer,
    WeaponType,
    CombatRole,
    ResistanceType,
    AttributeEffect,
    ArmorRecommendation,
    BuffRecommendation,
    BuildOptimization,
    attribute_optimizer,
    optimize_character_build
)


class TestAttributeOptimizer:
    """Test the AttributeOptimizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.optimizer = AttributeOptimizer(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test optimizer initialization."""
        assert self.optimizer.cache_dir.exists()
        assert isinstance(self.optimizer.attribute_effects, dict)
        assert isinstance(self.optimizer.weapon_attributes, dict)
        assert isinstance(self.optimizer.role_priorities, dict)
    
    def test_parse_wiki_attributes(self):
        """Test parsing attribute effects from wiki."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html>Sample wiki content</html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = self.optimizer.parse_wiki_attributes()
            assert result is True
            assert len(self.optimizer.attribute_effects) > 0
    
    def test_parse_wiki_attributes_error(self):
        """Test error handling in wiki parsing."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = self.optimizer.parse_wiki_attributes()
            assert result is False
    
    def test_cache_validation(self):
        """Test cache validation logic."""
        # Test with no cache
        assert not self.optimizer._is_cache_valid()
        
        # Test with valid cache
        cache_file = self.optimizer.cache_dir / "attribute_effects.json"
        cache_data = {
            'attribute_effects': [],
            'weapon_attributes': {},
            'role_priorities': {},
            'last_updated': datetime.now().isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        assert self.optimizer._is_cache_valid()
        
        # Test with expired cache
        expired_data = cache_data.copy()
        expired_data['last_updated'] = (datetime.now() - timedelta(hours=25)).isoformat()
        
        with open(cache_file, 'w') as f:
            json.dump(expired_data, f)
        
        assert not self.optimizer._is_cache_valid()
    
    def test_weapon_attributes_mapping(self):
        """Test weapon attributes mapping."""
        self.optimizer._build_weapon_attributes_mapping()
        
        assert WeaponType.MELEE in self.optimizer.weapon_attributes
        assert WeaponType.RANGED in self.optimizer.weapon_attributes
        assert 'strength' in self.optimizer.weapon_attributes[WeaponType.MELEE]
        assert 'precision' in self.optimizer.weapon_attributes[WeaponType.RANGED]
    
    def test_role_priorities(self):
        """Test role priorities mapping."""
        self.optimizer._build_role_priorities()
        
        assert CombatRole.TANK in self.optimizer.role_priorities
        assert CombatRole.DPS in self.optimizer.role_priorities
        assert 'constitution' in self.optimizer.role_priorities[CombatRole.TANK]
        assert 'precision' in self.optimizer.role_priorities[CombatRole.DPS]
    
    def test_get_armor_recommendation(self):
        """Test armor recommendation generation."""
        self.optimizer._build_weapon_attributes_mapping()
        self.optimizer._build_role_priorities()
        
        recommendation = self.optimizer.get_armor_recommendation(
            build_name="Test Build",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS
        )
        
        assert isinstance(recommendation, ArmorRecommendation)
        assert recommendation.build_name == "Test Build"
        assert recommendation.weapon_type == WeaponType.RANGED
        assert recommendation.combat_role == CombatRole.DPS
        assert len(recommendation.primary_stats) > 0
        assert len(recommendation.resistance_priorities) > 0
        assert 0 <= recommendation.effectiveness_score <= 1
    
    def test_get_armor_recommendation_with_resistance_focus(self):
        """Test armor recommendation with custom resistance focus."""
        self.optimizer._build_weapon_attributes_mapping()
        self.optimizer._build_role_priorities()
        
        resistance_focus = [ResistanceType.KINETIC, ResistanceType.ENERGY]
        
        recommendation = self.optimizer.get_armor_recommendation(
            build_name="Test Build",
            weapon_type=WeaponType.MELEE,
            combat_role=CombatRole.TANK,
            resistance_focus=resistance_focus
        )
        
        assert recommendation.resistance_priorities == resistance_focus
    
    def test_get_buff_recommendations(self):
        """Test buff recommendation generation."""
        self.optimizer._build_weapon_attributes_mapping()
        self.optimizer._build_role_priorities()
        
        recommendations = self.optimizer.get_buff_recommendations(
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS,
            primary_stats=['precision', 'agility', 'focus']
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert isinstance(rec, BuffRecommendation)
            assert rec.buff_name
            assert rec.buff_type in ['food', 'stim']
            assert rec.duration > 0
            assert rec.cost_estimate > 0
    
    def test_optimize_build(self):
        """Test complete build optimization."""
        self.optimizer._build_weapon_attributes_mapping()
        self.optimizer._build_role_priorities()
        
        optimization = self.optimizer.optimize_build(
            build_name="Test Build",
            weapon_type=WeaponType.RIFLE,
            combat_role=CombatRole.HEALER
        )
        
        assert isinstance(optimization, BuildOptimization)
        assert optimization.build_name == "Test Build"
        assert optimization.weapon_type == WeaponType.RIFLE
        assert optimization.combat_role == CombatRole.HEALER
        assert isinstance(optimization.armor_recommendation, ArmorRecommendation)
        assert isinstance(optimization.buff_recommendations, list)
        assert isinstance(optimization.food_recommendations, list)
        assert 0 <= optimization.overall_score <= 1
    
    def test_get_available_weapon_types(self):
        """Test getting available weapon types."""
        weapon_types = self.optimizer.get_available_weapon_types()
        
        assert isinstance(weapon_types, list)
        assert len(weapon_types) > 0
        assert all(isinstance(wt, WeaponType) for wt in weapon_types)
    
    def test_get_available_combat_roles(self):
        """Test getting available combat roles."""
        combat_roles = self.optimizer.get_available_combat_roles()
        
        assert isinstance(combat_roles, list)
        assert len(combat_roles) > 0
        assert all(isinstance(cr, CombatRole) for cr in combat_roles)
    
    def test_get_available_resistance_types(self):
        """Test getting available resistance types."""
        resistance_types = self.optimizer.get_available_resistance_types()
        
        assert isinstance(resistance_types, list)
        assert len(resistance_types) > 0
        assert all(isinstance(rt, ResistanceType) for rt in resistance_types)
    
    def test_get_attribute_effects(self):
        """Test getting attribute effects."""
        self.optimizer._parse_attribute_effects("")
        
        effects = self.optimizer.get_attribute_effects()
        
        assert isinstance(effects, dict)
        assert len(effects) > 0
        
        for attr, effect in effects.items():
            assert isinstance(effect, AttributeEffect)
            assert effect.attribute == attr
    
    def test_get_weapon_attributes(self):
        """Test getting attributes for a weapon type."""
        self.optimizer._build_weapon_attributes_mapping()
        
        attributes = self.optimizer.get_weapon_attributes(WeaponType.MELEE)
        
        assert isinstance(attributes, list)
        assert len(attributes) > 0
        assert all(isinstance(attr, str) for attr in attributes)
    
    def test_get_role_priorities(self):
        """Test getting priorities for a combat role."""
        self.optimizer._build_role_priorities()
        
        priorities = self.optimizer.get_role_priorities(CombatRole.TANK)
        
        assert isinstance(priorities, dict)
        assert len(priorities) > 0
        assert all(isinstance(priority, float) for priority in priorities.values())


class TestAttributeOptimizerDataClasses:
    """Test the data classes used in the attribute optimizer."""
    
    def test_attribute_effect(self):
        """Test AttributeEffect dataclass."""
        effect = AttributeEffect(
            attribute="strength",
            weapon_type=WeaponType.MELEE,
            effect_type="damage",
            effect_value=0.5,
            description="Increases melee weapon damage",
            source_url="https://example.com",
            last_updated="2024-01-01T00:00:00"
        )
        
        assert effect.attribute == "strength"
        assert effect.weapon_type == WeaponType.MELEE
        assert effect.effect_type == "damage"
        assert effect.effect_value == 0.5
        assert effect.description == "Increases melee weapon damage"
    
    def test_armor_recommendation(self):
        """Test ArmorRecommendation dataclass."""
        recommendation = ArmorRecommendation(
            build_name="Test Build",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS,
            primary_stats=["precision", "agility"],
            secondary_stats=["focus"],
            resistance_priorities=[ResistanceType.ENERGY],
            armor_slots={},
            reasoning="Test reasoning",
            effectiveness_score=0.8
        )
        
        assert recommendation.build_name == "Test Build"
        assert recommendation.weapon_type == WeaponType.RANGED
        assert recommendation.combat_role == CombatRole.DPS
        assert recommendation.primary_stats == ["precision", "agility"]
        assert recommendation.effectiveness_score == 0.8
    
    def test_buff_recommendation(self):
        """Test BuffRecommendation dataclass."""
        buff = BuffRecommendation(
            buff_name="test_stim",
            buff_type="stim",
            primary_effect="Enhances precision",
            secondary_effects=["Temporary boost"],
            duration=30,
            cost_estimate=5000,
            availability="uncommon",
            build_compatibility=["dps"]
        )
        
        assert buff.buff_name == "test_stim"
        assert buff.buff_type == "stim"
        assert buff.primary_effect == "Enhances precision"
        assert buff.duration == 30
        assert buff.cost_estimate == 5000
    
    def test_build_optimization(self):
        """Test BuildOptimization dataclass."""
        armor_rec = ArmorRecommendation(
            build_name="Test",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS,
            primary_stats=[],
            secondary_stats=[],
            resistance_priorities=[],
            armor_slots={},
            reasoning="",
            effectiveness_score=0.8
        )
        
        optimization = BuildOptimization(
            build_name="Test Build",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS,
            primary_attributes=["precision"],
            armor_recommendation=armor_rec,
            buff_recommendations=[],
            food_recommendations=[],
            resistance_focus=[],
            overall_score=0.8,
            notes="Test notes"
        )
        
        assert optimization.build_name == "Test Build"
        assert optimization.weapon_type == WeaponType.RANGED
        assert optimization.overall_score == 0.8


class TestAttributeOptimizerIntegration:
    """Test integration between attribute optimizer components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.optimizer = AttributeOptimizer(cache_dir=self.temp_dir)
        self.optimizer._parse_attribute_effects("")
        self.optimizer._build_weapon_attributes_mapping()
        self.optimizer._build_role_priorities()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_optimization(self):
        """Test complete end-to-end optimization workflow."""
        optimization = self.optimizer.optimize_build(
            build_name="Rifleman Medic",
            weapon_type=WeaponType.RIFLE,
            combat_role=CombatRole.HEALER
        )
        
        # Verify armor recommendation
        assert optimization.armor_recommendation.build_name == "Rifleman Medic"
        assert optimization.armor_recommendation.weapon_type == WeaponType.RIFLE
        assert optimization.armor_recommendation.combat_role == CombatRole.HEALER
        assert len(optimization.armor_recommendation.primary_stats) > 0
        assert len(optimization.armor_recommendation.resistance_priorities) > 0
        
        # Verify buff recommendations
        assert len(optimization.buff_recommendations) > 0
        assert len(optimization.food_recommendations) > 0
        
        # Verify overall structure
        assert optimization.overall_score > 0
        assert optimization.notes
    
    def test_different_build_types(self):
        """Test optimization for different build types."""
        build_configs = [
            ("Melee Tank", WeaponType.MELEE, CombatRole.TANK),
            ("Ranged DPS", WeaponType.RANGED, CombatRole.DPS),
            ("Pistol Healer", WeaponType.PISTOL, CombatRole.HEALER),
            ("Heavy Support", WeaponType.HEAVY_WEAPON, CombatRole.SUPPORT),
        ]
        
        for build_name, weapon_type, combat_role in build_configs:
            optimization = self.optimizer.optimize_build(
                build_name=build_name,
                weapon_type=weapon_type,
                combat_role=combat_role
            )
            
            assert optimization.build_name == build_name
            assert optimization.weapon_type == weapon_type
            assert optimization.combat_role == combat_role
            assert optimization.overall_score > 0
    
    def test_resistance_focus_impact(self):
        """Test how resistance focus affects recommendations."""
        # Test without resistance focus
        optimization1 = self.optimizer.optimize_build(
            build_name="Test Build",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS
        )
        
        # Test with resistance focus
        optimization2 = self.optimizer.optimize_build(
            build_name="Test Build",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS,
            resistance_focus=[ResistanceType.KINETIC, ResistanceType.ENERGY]
        )
        
        # Should have different resistance priorities
        assert optimization1.resistance_focus != optimization2.resistance_focus
        assert optimization2.resistance_focus == [ResistanceType.KINETIC, ResistanceType.ENERGY]


class TestAttributeOptimizerConvenienceFunctions:
    """Test convenience functions."""
    
    def test_optimize_character_build(self):
        """Test the optimize_character_build convenience function."""
        optimization = optimize_character_build(
            build_name="Test Build",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS
        )
        
        assert isinstance(optimization, BuildOptimization)
        assert optimization.build_name == "Test Build"
        assert optimization.weapon_type == WeaponType.RANGED
        assert optimization.combat_role == CombatRole.DPS
    
    def test_global_optimizer_instance(self):
        """Test the global optimizer instance."""
        assert isinstance(attribute_optimizer, AttributeOptimizer)
        
        # Test that it can generate optimizations
        optimization = attribute_optimizer.optimize_build(
            build_name="Test",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS
        )
        
        assert isinstance(optimization, BuildOptimization)


class TestAttributeOptimizerErrorHandling:
    """Test error handling in the attribute optimizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.optimizer = AttributeOptimizer(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_weapon_type(self):
        """Test handling of invalid weapon type."""
        with pytest.raises(ValueError):
            WeaponType("invalid_weapon")
    
    def test_invalid_combat_role(self):
        """Test handling of invalid combat role."""
        with pytest.raises(ValueError):
            CombatRole("invalid_role")
    
    def test_invalid_resistance_type(self):
        """Test handling of invalid resistance type."""
        with pytest.raises(ValueError):
            ResistanceType("invalid_resistance")
    
    def test_cache_load_error(self):
        """Test handling of cache load errors."""
        # Create invalid cache file
        cache_file = self.optimizer.cache_dir / "attribute_effects.json"
        with open(cache_file, 'w') as f:
            f.write("invalid json")
        
        # Should not raise exception
        self.optimizer._load_cached_data()
    
    def test_cache_save_error(self):
        """Test handling of cache save errors."""
        # Mock file write to raise exception
        with patch('builtins.open', side_effect=Exception("Write error")):
            # Should not raise exception
            self.optimizer._save_cached_data()


class TestAttributeOptimizerPerformance:
    """Test performance aspects of the attribute optimizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.optimizer = AttributeOptimizer(cache_dir=self.temp_dir)
        self.optimizer._parse_attribute_effects("")
        self.optimizer._build_weapon_attributes_mapping()
        self.optimizer._build_role_priorities()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_multiple_optimizations(self):
        """Test performance with multiple optimizations."""
        import time
        
        start_time = time.time()
        
        for i in range(10):
            optimization = self.optimizer.optimize_build(
                build_name=f"Build {i}",
                weapon_type=WeaponType.RANGED,
                combat_role=CombatRole.DPS
            )
            assert isinstance(optimization, BuildOptimization)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (less than 1 second)
        assert duration < 1.0
    
    def test_large_attribute_effects(self):
        """Test performance with large number of attribute effects."""
        # Add many attribute effects
        for i in range(100):
            effect = AttributeEffect(
                attribute=f"attr_{i}",
                weapon_type=WeaponType.RANGED,
                effect_type="test",
                effect_value=0.1,
                description=f"Test effect {i}",
                source_url="https://example.com",
                last_updated=datetime.now().isoformat()
            )
            self.optimizer.attribute_effects[f"attr_{i}"] = effect
        
        # Should still perform optimization quickly
        optimization = self.optimizer.optimize_build(
            build_name="Test",
            weapon_type=WeaponType.RANGED,
            combat_role=CombatRole.DPS
        )
        
        assert isinstance(optimization, BuildOptimization)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 