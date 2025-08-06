#!/usr/bin/env python3
"""
Tests for Batch 123 - Build Metadata + Community Templates

This test suite validates the functionality of the new build system including:
- Build loading and parsing
- Build validation
- Search and filtering
- Export functionality
- Performance metrics
- API endpoints
"""

import sys
import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.build_loader import (
    BuildLoader, BuildMetadata, BuildCategory, BuildSpecialization, BuildDifficulty,
    get_build_loader
)


class TestBuildLoader(unittest.TestCase):
    """Test cases for the BuildLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary YAML file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_yaml_path = Path(self.temp_dir) / "test_builds.yaml"
        
        # Create test build data
        self.test_build_data = {
            'builds': {
                'test_rifleman_medic': {
                    'name': 'Test Rifleman/Medic',
                    'description': 'Test build for rifleman with medic abilities',
                    'category': 'combat',
                    'specialization': 'pve',
                    'difficulty': 'medium',
                    'professions': {
                        'primary': 'Rifleman',
                        'secondary': 'Medic'
                    },
                    'skills': {
                        'rifleman': [
                            'combat_marksman_novice',
                            'combat_rifleman_novice'
                        ],
                        'medic': [
                            'science_medic_novice',
                            'science_medic_healing'
                        ]
                    },
                    'equipment': {
                        'weapons': {
                            'primary': 'rifle',
                            'secondary': 'carbine',
                            'recommended': ['T21', 'E11']
                        },
                        'armor': {
                            'type': 'medium',
                            'recommended': ['Stormtrooper Armor']
                        },
                        'tapes': ['accuracy', 'damage'],
                        'resists': ['energy', 'kinetic']
                    },
                    'performance': {
                        'pve_rating': 8.5,
                        'pvp_rating': 6.0,
                        'solo_rating': 9.0,
                        'group_rating': 8.0,
                        'farming_rating': 7.5
                    },
                    'combat': {
                        'style': 'ranged',
                        'stance': 'kneeling',
                        'rotation': ['aim', 'headshot', 'burst_fire'],
                        'heal_threshold': 50,
                        'buff_threshold': 80,
                        'max_range': 50
                    },
                    'cooldowns': {
                        'aim': 0,
                        'headshot': 5,
                        'burst_fire': 15
                    },
                    'emergency_abilities': {
                        'critical_heal': 'heal_self',
                        'defensive': 'stim_pack'
                    },
                    'notes': [
                        'Excellent for solo PvE content',
                        'Good healing capabilities for group play'
                    ]
                },
                'test_tk_pistoleer': {
                    'name': 'Test TK/Pistoleer',
                    'description': 'Test hybrid melee and ranged build',
                    'category': 'combat',
                    'specialization': 'pvp',
                    'difficulty': 'hard',
                    'professions': {
                        'primary': 'Teras Kasi',
                        'secondary': 'Pistoleer'
                    },
                    'skills': {
                        'teras_kasi': [
                            'combat_unarmed_novice',
                            'combat_unarmed_teras_kasi'
                        ],
                        'pistoleer': [
                            'combat_marksman_novice',
                            'combat_marksman_pistol'
                        ]
                    },
                    'equipment': {
                        'weapons': {
                            'primary': 'unarmed',
                            'secondary': 'pistol',
                            'recommended': ['Power Hammer', 'DL44']
                        },
                        'armor': {
                            'type': 'light',
                            'recommended': ['Combat Armor']
                        },
                        'tapes': ['accuracy', 'damage'],
                        'resists': ['kinetic', 'energy']
                    },
                    'performance': {
                        'pve_rating': 7.0,
                        'pvp_rating': 9.0,
                        'solo_rating': 8.5,
                        'group_rating': 6.5,
                        'farming_rating': 6.0
                    },
                    'combat': {
                        'style': 'hybrid',
                        'stance': 'standing',
                        'rotation': ['pistol_shot', 'melee_strike'],
                        'heal_threshold': 40,
                        'buff_threshold': 70,
                        'max_range': 25
                    },
                    'cooldowns': {
                        'pistol_shot': 0,
                        'melee_strike': 2
                    },
                    'emergency_abilities': {
                        'critical_heal': 'heal_self',
                        'defensive': 'stim_pack'
                    },
                    'notes': [
                        'Excellent for PvP combat',
                        'High mobility and versatility'
                    ]
                }
            }
        }
        
        # Write test data to file
        import yaml
        with open(self.test_yaml_path, 'w') as f:
            yaml.dump(self.test_build_data, f)
        
        # Create build loader with test file
        self.build_loader = BuildLoader(str(self.test_yaml_path))
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if self.test_yaml_path.exists():
            self.test_yaml_path.unlink()
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_load_builds(self):
        """Test loading builds from YAML file."""
        builds = self.build_loader.get_all_builds()
        
        self.assertEqual(len(builds), 2)
        self.assertIn('test_rifleman_medic', builds)
        self.assertIn('test_tk_pistoleer', builds)
        
        # Check first build
        rifleman_build = builds['test_rifleman_medic']
        self.assertEqual(rifleman_build.name, 'Test Rifleman/Medic')
        self.assertEqual(rifleman_build.category, BuildCategory.COMBAT)
        self.assertEqual(rifleman_build.specialization, BuildSpecialization.PVE)
        self.assertEqual(rifleman_build.difficulty, BuildDifficulty.MEDIUM)
    
    def test_get_build(self):
        """Test getting a specific build."""
        build = self.build_loader.get_build('test_rifleman_medic')
        
        self.assertIsNotNone(build)
        self.assertEqual(build.name, 'Test Rifleman/Medic')
        self.assertEqual(build.description, 'Test build for rifleman with medic abilities')
        
        # Test non-existent build
        build = self.build_loader.get_build('non_existent')
        self.assertIsNone(build)
    
    def test_search_builds(self):
        """Test searching builds with filters."""
        # Search by category
        combat_builds = self.build_loader.search_builds(category=BuildCategory.COMBAT)
        self.assertEqual(len(combat_builds), 2)
        
        # Search by specialization
        pve_builds = self.build_loader.search_builds(specialization=BuildSpecialization.PVE)
        self.assertEqual(len(pve_builds), 1)
        self.assertIn('test_rifleman_medic', pve_builds)
        
        pvp_builds = self.build_loader.search_builds(specialization=BuildSpecialization.PVP)
        self.assertEqual(len(pvp_builds), 1)
        self.assertIn('test_tk_pistoleer', pvp_builds)
        
        # Search by difficulty
        medium_builds = self.build_loader.search_builds(difficulty=BuildDifficulty.MEDIUM)
        self.assertEqual(len(medium_builds), 1)
        self.assertIn('test_rifleman_medic', medium_builds)
        
        hard_builds = self.build_loader.search_builds(difficulty=BuildDifficulty.HARD)
        self.assertEqual(len(hard_builds), 1)
        self.assertIn('test_tk_pistoleer', hard_builds)
        
        # Search with minimum rating
        high_perf_builds = self.build_loader.search_builds(min_rating=8.0)
        self.assertEqual(len(high_perf_builds), 1)
        self.assertIn('test_rifleman_medic', high_perf_builds)
    
    def test_get_build_skills(self):
        """Test getting skills for a build."""
        skills = self.build_loader.get_build_skills('test_rifleman_medic')
        
        self.assertIn('rifleman', skills)
        self.assertIn('medic', skills)
        self.assertEqual(len(skills['rifleman']), 2)
        self.assertEqual(len(skills['medic']), 2)
        self.assertIn('combat_marksman_novice', skills['rifleman'])
        self.assertIn('science_medic_novice', skills['medic'])
    
    def test_get_build_equipment(self):
        """Test getting equipment for a build."""
        equipment = self.build_loader.get_build_equipment('test_rifleman_medic')
        
        self.assertIn('weapons', equipment)
        self.assertIn('armor', equipment)
        self.assertIn('tapes', equipment)
        self.assertIn('resists', equipment)
        
        self.assertEqual(equipment['weapons']['primary'], 'rifle')
        self.assertEqual(equipment['armor']['type'], 'medium')
        self.assertIn('accuracy', equipment['tapes'])
        self.assertIn('energy', equipment['resists'])
    
    def test_get_build_performance(self):
        """Test getting performance metrics for a build."""
        performance = self.build_loader.get_build_performance('test_rifleman_medic')
        
        self.assertEqual(performance['pve_rating'], 8.5)
        self.assertEqual(performance['pvp_rating'], 6.0)
        self.assertEqual(performance['solo_rating'], 9.0)
        self.assertEqual(performance['group_rating'], 8.0)
        self.assertEqual(performance['farming_rating'], 7.5)
    
    def test_get_build_combat_config(self):
        """Test getting combat configuration for a build."""
        combat = self.build_loader.get_build_combat_config('test_rifleman_medic')
        
        self.assertEqual(combat['style'], 'ranged')
        self.assertEqual(combat['stance'], 'kneeling')
        self.assertIn('aim', combat['rotation'])
        self.assertEqual(combat['heal_threshold'], 50)
        self.assertEqual(combat['max_range'], 50)
    
    def test_export_build_to_json(self):
        """Test exporting a build to JSON format."""
        output_path = Path(self.temp_dir) / "exported_build.json"
        
        success = self.build_loader.export_build_to_json('test_rifleman_medic', str(output_path))
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # Check exported content
        with open(output_path, 'r') as f:
            exported_data = json.load(f)
        
        self.assertEqual(exported_data['name'], 'Test Rifleman/Medic')
        self.assertEqual(exported_data['category'], 'combat')
        self.assertEqual(exported_data['specialization'], 'pve')
        self.assertEqual(exported_data['difficulty'], 'medium')
        self.assertIn('skills', exported_data)
        self.assertIn('equipment', exported_data)
        self.assertIn('performance', exported_data)
        
        # Clean up
        output_path.unlink()
    
    def test_validate_build(self):
        """Test build validation."""
        # Test valid build
        is_valid, errors = self.build_loader.validate_build('test_rifleman_medic')
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test non-existent build
        is_valid, errors = self.build_loader.validate_build('non_existent')
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn('not found', errors[0])
    
    def test_get_build_summary(self):
        """Test getting build summary."""
        summary = self.build_loader.get_build_summary('test_rifleman_medic')
        
        self.assertEqual(summary['id'], 'test_rifleman_medic')
        self.assertEqual(summary['name'], 'Test Rifleman/Medic')
        self.assertEqual(summary['category'], 'combat')
        self.assertEqual(summary['specialization'], 'pve')
        self.assertEqual(summary['difficulty'], 'medium')
        self.assertEqual(summary['total_skills'], 4)  # 2 rifleman + 2 medic
        self.assertEqual(summary['combat_style'], 'ranged')
        self.assertEqual(len(summary['notes']), 2)
    
    def test_get_builds_by_category(self):
        """Test getting builds by category."""
        combat_builds = self.build_loader.get_builds_by_category(BuildCategory.COMBAT)
        self.assertEqual(len(combat_builds), 2)
        
        # Test with non-existent category (should return empty)
        utility_builds = self.build_loader.get_builds_by_category(BuildCategory.UTILITY)
        self.assertEqual(len(utility_builds), 0)
    
    def test_get_builds_by_specialization(self):
        """Test getting builds by specialization."""
        pve_builds = self.build_loader.get_builds_by_specialization(BuildSpecialization.PVE)
        self.assertEqual(len(pve_builds), 1)
        self.assertIn('test_rifleman_medic', pve_builds)
        
        pvp_builds = self.build_loader.get_builds_by_specialization(BuildSpecialization.PVP)
        self.assertEqual(len(pvp_builds), 1)
        self.assertIn('test_tk_pistoleer', pvp_builds)
    
    def test_get_top_performing_builds(self):
        """Test getting top performing builds."""
        # Test PvE rankings
        top_pve = self.build_loader.get_top_performing_builds('pve_rating', 2)
        self.assertEqual(len(top_pve), 2)
        self.assertEqual(top_pve[0][0], 'test_rifleman_medic')  # 8.5 rating
        self.assertEqual(top_pve[1][0], 'test_tk_pistoleer')    # 7.0 rating
        
        # Test PvP rankings
        top_pvp = self.build_loader.get_top_performing_builds('pvp_rating', 2)
        self.assertEqual(len(top_pvp), 2)
        self.assertEqual(top_pvp[0][0], 'test_tk_pistoleer')    # 9.0 rating
        self.assertEqual(top_pvp[1][0], 'test_rifleman_medic')  # 6.0 rating


class TestBuildMetadata(unittest.TestCase):
    """Test cases for the BuildMetadata dataclass."""
    
    def test_build_metadata_creation(self):
        """Test creating BuildMetadata objects."""
        metadata = BuildMetadata(
            name="Test Build",
            description="Test description",
            category=BuildCategory.COMBAT,
            specialization=BuildSpecialization.PVE,
            difficulty=BuildDifficulty.MEDIUM,
            professions={'primary': 'Rifleman', 'secondary': 'Medic'},
            skills={'rifleman': ['skill1', 'skill2']},
            equipment={'weapons': {'primary': 'rifle'}},
            performance={'pve_rating': 8.5},
            combat={'style': 'ranged'},
            cooldowns={'skill1': 5},
            emergency_abilities={'heal': 'heal_self'},
            notes=['Note 1', 'Note 2']
        )
        
        self.assertEqual(metadata.name, "Test Build")
        self.assertEqual(metadata.category, BuildCategory.COMBAT)
        self.assertEqual(metadata.specialization, BuildSpecialization.PVE)
        self.assertEqual(metadata.difficulty, BuildDifficulty.MEDIUM)
        self.assertEqual(len(metadata.skills), 1)
        self.assertEqual(len(metadata.notes), 2)


class TestBuildEnums(unittest.TestCase):
    """Test cases for the build enums."""
    
    def test_build_category_enum(self):
        """Test BuildCategory enum."""
        self.assertEqual(BuildCategory.COMBAT.value, "combat")
        self.assertEqual(BuildCategory.UTILITY.value, "utility")
        self.assertEqual(BuildCategory.SUPPORT.value, "support")
        
        # Test creation from value
        self.assertEqual(BuildCategory("combat"), BuildCategory.COMBAT)
        self.assertEqual(BuildCategory("utility"), BuildCategory.UTILITY)
        self.assertEqual(BuildCategory("support"), BuildCategory.SUPPORT)
    
    def test_build_specialization_enum(self):
        """Test BuildSpecialization enum."""
        self.assertEqual(BuildSpecialization.PVE.value, "pve")
        self.assertEqual(BuildSpecialization.PVP.value, "pvp")
        self.assertEqual(BuildSpecialization.GROUP.value, "group")
        self.assertEqual(BuildSpecialization.SOLO.value, "solo")
        self.assertEqual(BuildSpecialization.TANK.value, "tank")
        self.assertEqual(BuildSpecialization.FARMING.value, "farming")
        
        # Test creation from value
        self.assertEqual(BuildSpecialization("pve"), BuildSpecialization.PVE)
        self.assertEqual(BuildSpecialization("pvp"), BuildSpecialization.PVP)
    
    def test_build_difficulty_enum(self):
        """Test BuildDifficulty enum."""
        self.assertEqual(BuildDifficulty.EASY.value, "easy")
        self.assertEqual(BuildDifficulty.MEDIUM.value, "medium")
        self.assertEqual(BuildDifficulty.HARD.value, "hard")
        
        # Test creation from value
        self.assertEqual(BuildDifficulty("easy"), BuildDifficulty.EASY)
        self.assertEqual(BuildDifficulty("medium"), BuildDifficulty.MEDIUM)
        self.assertEqual(BuildDifficulty("hard"), BuildDifficulty.HARD)


class TestBuildLoaderIntegration(unittest.TestCase):
    """Integration tests for the build loader."""
    
    def test_get_build_loader_singleton(self):
        """Test that get_build_loader returns a singleton."""
        loader1 = get_build_loader()
        loader2 = get_build_loader()
        
        self.assertIs(loader1, loader2)
    
    def test_build_loader_with_missing_file(self):
        """Test build loader behavior with missing file."""
        with patch('pathlib.Path.exists', return_value=False):
            loader = BuildLoader("non_existent_file.yaml")
            builds = loader.get_all_builds()
            self.assertEqual(len(builds), 0)
    
    def test_build_loader_with_invalid_yaml(self):
        """Test build loader behavior with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = f.name
        
        try:
            loader = BuildLoader(temp_file)
            builds = loader.get_all_builds()
            self.assertEqual(len(builds), 0)
        finally:
            os.unlink(temp_file)


class TestBuildValidation(unittest.TestCase):
    """Test cases for build validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.build_loader = BuildLoader()
    
    def test_validate_complete_build(self):
        """Test validation of a complete, valid build."""
        # Create a valid build
        valid_build = BuildMetadata(
            name="Valid Build",
            description="Valid description",
            category=BuildCategory.COMBAT,
            specialization=BuildSpecialization.PVE,
            difficulty=BuildDifficulty.MEDIUM,
            professions={'primary': 'Rifleman'},
            skills={'rifleman': ['skill1', 'skill2']},
            equipment={'weapons': {'primary': 'rifle'}},
            performance={'pve_rating': 8.5},
            combat={'style': 'ranged', 'stance': 'kneeling', 'rotation': ['skill1']},
            cooldowns={'skill1': 5},
            emergency_abilities={'heal': 'heal_self'},
            notes=['Note 1']
        )
        
        # Mock the get_build method to return our valid build
        with patch.object(self.build_loader, 'get_build', return_value=valid_build):
            is_valid, errors = self.build_loader.validate_build('valid_build')
            self.assertTrue(is_valid)
            self.assertEqual(len(errors), 0)
    
    def test_validate_incomplete_build(self):
        """Test validation of an incomplete build."""
        # Create an invalid build (missing required fields)
        invalid_build = BuildMetadata(
            name="",  # Missing name
            description="",  # Missing description
            category=BuildCategory.COMBAT,
            specialization=BuildSpecialization.PVE,
            difficulty=BuildDifficulty.MEDIUM,
            professions={},  # Missing professions
            skills={},  # Missing skills
            equipment={},
            performance={},
            combat={},
            cooldowns={},
            emergency_abilities={},
            notes=[]
        )
        
        # Mock the get_build method to return our invalid build
        with patch.object(self.build_loader, 'get_build', return_value=invalid_build):
            is_valid, errors = self.build_loader.validate_build('invalid_build')
            self.assertFalse(is_valid)
            self.assertGreater(len(errors), 0)
            
            # Check for specific error messages
            error_messages = [error.lower() for error in errors]
            self.assertTrue(any('name' in msg for msg in error_messages))
            self.assertTrue(any('description' in msg for msg in error_messages))
            self.assertTrue(any('profession' in msg for msg in error_messages))
            self.assertTrue(any('skill' in msg for msg in error_messages))


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBuildLoader,
        TestBuildMetadata,
        TestBuildEnums,
        TestBuildLoaderIntegration,
        TestBuildValidation
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 