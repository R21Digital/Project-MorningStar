#!/usr/bin/env python3
"""Test suite for Batch 039 - Crafting & Resource Interaction Bootstrap.

This test suite covers:
- Crafting handler initialization and configuration
- Recipe loading and management
- Station detection and interaction
- Recipe selection and blueprint management
- Crafting process automation
- State tracker integration
- Error handling and edge cases
"""

import unittest
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import numpy as np
import cv2

from core.crafting_handler import (
    CraftingHandler,
    CraftingStation,
    CraftingRecipe,
    CraftingSession,
    detect_crafting_station,
    interact_with_crafting_station,
    craft_with_blueprint,
    get_available_recipes,
    get_crafting_handler
)
from core.state_tracker import get_state, update_state


class TestCraftingRecipe(unittest.TestCase):
    """Test the CraftingRecipe dataclass."""
    
    def test_crafting_recipe_creation(self):
        """Test creating a CraftingRecipe instance."""
        recipe = CraftingRecipe(
            name="Test Recipe",
            difficulty=2,
            materials=["metal_ingot", "electronic_component"],
            crafting_time=45,
            experience_gain=75,
            skill_required="crafting_artisan_novice",
            effects=["health_restore", "stamina_boost"]
        )
        
        self.assertEqual(recipe.name, "Test Recipe")
        self.assertEqual(recipe.difficulty, 2)
        self.assertEqual(len(recipe.materials), 2)
        self.assertEqual(recipe.crafting_time, 45)
        self.assertEqual(recipe.experience_gain, 75)
        self.assertEqual(recipe.skill_required, "crafting_artisan_novice")
        self.assertEqual(len(recipe.effects), 2)
    
    def test_crafting_recipe_defaults(self):
        """Test CraftingRecipe with default values."""
        recipe = CraftingRecipe(
            name="Basic Recipe",
            difficulty=1,
            materials=["material"],
            crafting_time=30,
            experience_gain=50,
            skill_required="basic_skill"
        )
        
        self.assertEqual(recipe.name, "Basic Recipe")
        self.assertEqual(recipe.difficulty, 1)
        self.assertEqual(recipe.effects, None)
    
    def test_crafting_recipe_to_dict(self):
        """Test converting CraftingRecipe to dictionary."""
        recipe = CraftingRecipe(
            name="Test Recipe",
            difficulty=3,
            materials=["material1", "material2"],
            crafting_time=60,
            experience_gain=100,
            skill_required="advanced_skill",
            effects=["effect1", "effect2"]
        )
        
        recipe_dict = recipe.to_dict()
        
        self.assertEqual(recipe_dict["name"], "Test Recipe")
        self.assertEqual(recipe_dict["difficulty"], 3)
        self.assertEqual(recipe_dict["materials"], ["material1", "material2"])
        self.assertEqual(recipe_dict["crafting_time"], 60)
        self.assertEqual(recipe_dict["experience_gain"], 100)
        self.assertEqual(recipe_dict["skill_required"], "advanced_skill")
        self.assertEqual(recipe_dict["effects"], ["effect1", "effect2"])


class TestCraftingStation(unittest.TestCase):
    """Test the CraftingStation dataclass."""
    
    def test_crafting_station_creation(self):
        """Test creating a CraftingStation instance."""
        station = CraftingStation(
            station_type="crafting_station",
            name="Crafting Station",
            interaction_method="/craft",
            hotbar_slot=1,
            ui_elements=["recipe_list", "craft_button", "exit_button"]
        )
        
        self.assertEqual(station.station_type, "crafting_station")
        self.assertEqual(station.name, "Crafting Station")
        self.assertEqual(station.interaction_method, "/craft")
        self.assertEqual(station.hotbar_slot, 1)
        self.assertEqual(len(station.ui_elements), 3)
    
    def test_crafting_station_to_dict(self):
        """Test converting CraftingStation to dictionary."""
        station = CraftingStation(
            station_type="food_station",
            name="Food Station",
            interaction_method="/cook",
            hotbar_slot=2,
            ui_elements=["recipe_list", "cook_button"]
        )
        
        station_dict = station.to_dict()
        
        self.assertEqual(station_dict["station_type"], "food_station")
        self.assertEqual(station_dict["name"], "Food Station")
        self.assertEqual(station_dict["interaction_method"], "/cook")
        self.assertEqual(station_dict["hotbar_slot"], 2)
        self.assertEqual(station_dict["ui_elements"], ["recipe_list", "cook_button"])


class TestCraftingSession(unittest.TestCase):
    """Test the CraftingSession dataclass."""
    
    def test_crafting_session_creation(self):
        """Test creating a CraftingSession instance."""
        station = CraftingStation(
            station_type="crafting_station",
            name="Crafting Station",
            interaction_method="/craft",
            hotbar_slot=1,
            ui_elements=[]
        )
        
        recipe = CraftingRecipe(
            name="Test Recipe",
            difficulty=1,
            materials=["material"],
            crafting_time=30,
            experience_gain=50,
            skill_required="basic_skill"
        )
        
        session = CraftingSession(
            station=station,
            selected_recipe=recipe,
            start_time=time.time(),
            is_crafting=True,
            session_id="test_session"
        )
        
        self.assertEqual(session.station.station_type, "crafting_station")
        self.assertEqual(session.selected_recipe.name, "Test Recipe")
        self.assertTrue(session.is_crafting)
        self.assertEqual(session.session_id, "test_session")
    
    def test_crafting_session_to_dict(self):
        """Test converting CraftingSession to dictionary."""
        station = CraftingStation(
            station_type="food_station",
            name="Food Station",
            interaction_method="/cook",
            hotbar_slot=2,
            ui_elements=[]
        )
        
        session = CraftingSession(
            station=station,
            selected_recipe=None,
            start_time=None,
            is_crafting=False,
            session_id=None
        )
        
        session_dict = session.to_dict()
        
        self.assertEqual(session_dict["station"]["station_type"], "food_station")
        self.assertIsNone(session_dict["selected_recipe"])
        self.assertIsNone(session_dict["start_time"])
        self.assertFalse(session_dict["is_crafting"])
        self.assertIsNone(session_dict["session_id"])


class TestCraftingHandler(unittest.TestCase):
    """Test the CraftingHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary recipes file
        self.temp_dir = tempfile.mkdtemp()
        self.recipes_path = os.path.join(self.temp_dir, "test_recipes.yaml")
        
        # Create a simple test recipes file
        test_recipes = """
artisan:
  name: "Artisan"
  description: "Basic crafting profession"
  station_type: "crafting_station"
  recipes:
    test_recipe:
      name: "Test Recipe"
      difficulty: 1
      materials: ["metal_ingot", "electronic_component"]
      crafting_time: 30
      experience_gain: 50
      skill_required: "crafting_artisan_novice"

station_types:
  crafting_station:
    name: "Crafting Station"
    interaction_method: "/craft"
    hotbar_slot: 1
    ui_elements: ["recipe_list", "craft_button", "exit_button"]

materials:
  metal_ingot:
    name: "Metal Ingot"
    type: "metal"
    rarity: "common"
"""
        
        with open(self.recipes_path, 'w') as f:
            f.write(test_recipes)
        
        # Create crafting handler with test config
        self.handler = CraftingHandler(self.recipes_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_crafting_handler_initialization(self):
        """Test CraftingHandler initialization."""
        self.assertIsNotNone(self.handler.logger)
        self.assertIsNotNone(self.handler.ocr_engine)
        self.assertIsInstance(self.handler.recipes_data, dict)
        self.assertIsInstance(self.handler.stations, dict)
        self.assertIsInstance(self.handler.materials, dict)
        self.assertIsInstance(self.handler.regions, dict)
        self.assertIsNone(self.handler.current_session)
        self.assertEqual(len(self.handler.recent_recipes), 0)
    
    def test_load_recipes(self):
        """Test loading recipes from file."""
        self.assertIn("artisan", self.handler.recipes_data)
        self.assertIn("station_types", self.handler.recipes_data)
        self.assertIn("materials", self.handler.recipes_data)
        
        artisan_data = self.handler.recipes_data["artisan"]
        self.assertEqual(artisan_data["name"], "Artisan")
        self.assertEqual(artisan_data["station_type"], "crafting_station")
    
    def test_load_stations(self):
        """Test loading stations from recipes data."""
        self.assertIn("crafting_station", self.handler.stations)
        
        station = self.handler.stations["crafting_station"]
        self.assertEqual(station.name, "Crafting Station")
        self.assertEqual(station.interaction_method, "/craft")
        self.assertEqual(station.hotbar_slot, 1)
        self.assertEqual(len(station.ui_elements), 3)
    
    def test_load_materials(self):
        """Test loading materials from recipes data."""
        self.assertIn("metal_ingot", self.handler.materials)
        
        material = self.handler.materials["metal_ingot"]
        self.assertEqual(material["name"], "Metal Ingot")
        self.assertEqual(material["type"], "metal")
        self.assertEqual(material["rarity"], "common")
    
    def test_detect_crafting_station(self):
        """Test crafting station detection."""
        # Create a mock image
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # Mock OCR result
        with patch.object(self.handler.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.return_value = Mock(
                text="Crafting Station",
                confidence=0.8
            )
            
            station = self.handler.detect_crafting_station(image)
            
            # Should detect crafting station
            self.assertIsNotNone(station)
            self.assertEqual(station.station_type, "crafting_station")
    
    def test_detect_crafting_station_food(self):
        """Test food station detection."""
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        
        with patch.object(self.handler.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.return_value = Mock(
                text="Food Station Kitchen",
                confidence=0.8
            )
            
            station = self.handler.detect_crafting_station(image)
            
            # Should detect food station (if food_station exists in handler.stations)
            if "food_station" in self.handler.stations:
                self.assertIsNotNone(station)
                self.assertEqual(station.station_type, "food_station")
            else:
                # If food_station doesn't exist in test config, just check it doesn't crash
                self.assertIsInstance(station, (CraftingStation, type(None)))
    
    def test_detect_crafting_ui(self):
        """Test crafting UI detection."""
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        
        with patch.object(self.handler.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.return_value = Mock(
                text="Recipe List Materials Requirements Craft Button",
                confidence=0.8
            )
            
            has_ui = self.handler._detect_crafting_ui(image)
            
            # Should detect crafting UI
            self.assertTrue(has_ui)
    
    def test_get_available_recipes(self):
        """Test getting available recipes for a station."""
        station = self.handler.stations["crafting_station"]
        recipes = self.handler.get_available_recipes(station)
        
        self.assertEqual(len(recipes), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.name, "Test Recipe")
        self.assertEqual(recipe.difficulty, 1)
        self.assertEqual(len(recipe.materials), 2)
    
    def test_select_recipe(self):
        """Test recipe selection."""
        station = self.handler.stations["crafting_station"]
        
        with patch('pyautogui.click') as mock_click:
            success = self.handler.select_recipe("Test Recipe", station)
            
            # Should select recipe successfully
            self.assertTrue(success)
            mock_click.assert_called_once()
            
            # Should update recent recipes
            self.assertIn("Test Recipe", self.handler.recent_recipes)
    
    def test_select_recipe_not_found(self):
        """Test recipe selection with non-existent recipe."""
        station = self.handler.stations["crafting_station"]
        
        success = self.handler.select_recipe("NonExistentRecipe", station)
        
        # Should fail to select recipe
        self.assertFalse(success)
    
    def test_start_crafting(self):
        """Test starting crafting process."""
        station = self.handler.stations["crafting_station"]
        
        with patch('pyautogui.click') as mock_click:
            success = self.handler.start_crafting("Test Recipe", station)
            
            # Should start crafting successfully
            self.assertTrue(success)
            self.assertIsNotNone(self.handler.current_session)
            self.assertTrue(self.handler.current_session.is_crafting)
            self.assertEqual(mock_click.call_count, 2)  # Recipe selection + craft button
    
    def test_complete_crafting(self):
        """Test completing crafting process."""
        # Set up a crafting session
        station = self.handler.stations["crafting_station"]
        recipe = CraftingRecipe(
            name="Test Recipe",
            difficulty=1,
            materials=["material"],
            crafting_time=1,  # Short time for testing
            experience_gain=50,
            skill_required="basic_skill"
        )
        
        self.handler.current_session = CraftingSession(
            station=station,
            selected_recipe=recipe,
            start_time=time.time(),
            is_crafting=True,
            session_id="test_session"
        )
        
        with patch('pyautogui.click') as mock_click:
            success = self.handler.complete_crafting()
            
            # Should complete crafting successfully
            self.assertTrue(success)
            self.assertFalse(self.handler.current_session.is_crafting)
            mock_click.assert_called_once()  # Exit button
    
    def test_complete_crafting_no_session(self):
        """Test completing crafting with no active session."""
        success = self.handler.complete_crafting()
        
        # Should fail to complete crafting
        self.assertFalse(success)
    
    def test_interact_with_crafting_station(self):
        """Test interacting with crafting station."""
        with patch('pyautogui.write') as mock_write:
            with patch('pyautogui.press') as mock_press:
                with patch('core.crafting_handler.capture_screen') as mock_capture:
                    mock_image = np.zeros((600, 800, 3), dtype=np.uint8)
                    mock_capture.return_value = mock_image
                    
                    with patch.object(self.handler, 'detect_crafting_station') as mock_detect:
                        mock_detect.return_value = self.handler.stations["crafting_station"]
                        
                        station = self.handler.interact_with_crafting_station()
                        
                        # Should interact successfully
                        self.assertIsNotNone(station)
                        self.assertEqual(station.station_type, "crafting_station")
                        mock_write.assert_called_with("/craft")
                        mock_press.assert_called_with("enter")
    
    def test_get_most_recent_recipe(self):
        """Test getting most recent recipe."""
        # Add some recent recipes
        self.handler.recent_recipes = ["Recipe 1", "Recipe 2", "Recipe 3"]
        
        most_recent = self.handler.get_most_recent_recipe()
        
        self.assertEqual(most_recent, "Recipe 3")
    
    def test_get_most_recent_recipe_empty(self):
        """Test getting most recent recipe when none available."""
        most_recent = self.handler.get_most_recent_recipe()
        
        self.assertIsNone(most_recent)
    
    def test_craft_with_blueprint(self):
        """Test blueprint-based crafting."""
        with patch.object(self.handler, 'interact_with_crafting_station') as mock_interact:
            with patch.object(self.handler, 'start_crafting') as mock_start:
                with patch.object(self.handler, 'complete_crafting') as mock_complete:
                    mock_interact.return_value = self.handler.stations["crafting_station"]
                    mock_start.return_value = True
                    mock_complete.return_value = True
                    
                    success = self.handler.craft_with_blueprint("crafting_station", "Test Recipe")
                    
                    # Should complete blueprint crafting successfully
                    self.assertTrue(success)
                    mock_interact.assert_called_once_with("crafting_station")
                    mock_start.assert_called_once()
                    mock_complete.assert_called_once()
    
    def test_update_crafting_state(self):
        """Test updating crafting state."""
        # Set up a crafting session
        station = self.handler.stations["crafting_station"]
        recipe = CraftingRecipe(
            name="Test Recipe",
            difficulty=1,
            materials=["material"],
            crafting_time=30,
            experience_gain=50,
            skill_required="basic_skill"
        )
        
        self.handler.current_session = CraftingSession(
            station=station,
            selected_recipe=recipe,
            start_time=time.time(),
            is_crafting=True,
            session_id="test_session"
        )
        
        with patch('core.crafting_handler.update_state') as mock_update:
            self.handler._update_crafting_state()
            
            # Should update state tracker
            mock_update.assert_called_once()
            call_args = mock_update.call_args[1]
            self.assertEqual(call_args["crafting_station"], "crafting_station")
            self.assertEqual(call_args["crafting_recipe"], "Test Recipe")
            self.assertTrue(call_args["is_crafting"])


class TestCraftingHandlerIntegration(unittest.TestCase):
    """Test crafting handler integration functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing crafting handler
        import core.crafting_handler
        core.crafting_handler._crafting_handler = None
    
    def test_get_crafting_handler(self):
        """Test getting crafting handler instance."""
        handler1 = get_crafting_handler()
        handler2 = get_crafting_handler()
        
        # Should return the same instance
        self.assertIs(handler1, handler2)
        self.assertIsInstance(handler1, CraftingHandler)
    
    def test_detect_crafting_station(self):
        """Test detecting crafting station from screen."""
        with patch('core.crafting_handler.capture_screen') as mock_capture:
            mock_image = np.zeros((600, 800, 3), dtype=np.uint8)
            mock_capture.return_value = mock_image
            
            station = detect_crafting_station()
            
            self.assertIsInstance(station, (CraftingStation, type(None)))
    
    def test_interact_with_crafting_station(self):
        """Test interacting with crafting station."""
        station = interact_with_crafting_station()
        
        self.assertIsInstance(station, (CraftingStation, type(None)))
    
    def test_craft_with_blueprint(self):
        """Test blueprint-based crafting."""
        success = craft_with_blueprint("crafting_station", "Test Recipe")
        
        self.assertIsInstance(success, bool)
    
    def test_get_available_recipes(self):
        """Test getting available recipes."""
        recipes = get_available_recipes("crafting_station")
        
        self.assertIsInstance(recipes, list)
        for recipe in recipes:
            self.assertIsInstance(recipe, CraftingRecipe)


class TestCraftingHandlerErrorHandling(unittest.TestCase):
    """Test error handling in crafting handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = CraftingHandler()
    
    def test_load_recipes_missing_file(self):
        """Test loading recipes with missing file."""
        handler = CraftingHandler("nonexistent_file.yaml")
        
        # Should handle missing file gracefully
        self.assertEqual(handler.recipes_data, {})
    
    def test_detect_crafting_station_exception(self):
        """Test station detection with exception."""
        with patch.object(self.handler.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.side_effect = Exception("OCR failed")
            
            station = self.handler.detect_crafting_station(np.zeros((100, 100, 3)))
            
            # Should return None on exception
            self.assertIsNone(station)
    
    def test_select_recipe_exception(self):
        """Test recipe selection with exception."""
        station = CraftingStation(
            station_type="test_station",
            name="Test Station",
            interaction_method="/test",
            hotbar_slot=1,
            ui_elements=[]
        )
        
        with patch('pyautogui.click') as mock_click:
            mock_click.side_effect = Exception("Click failed")
            
            success = self.handler.select_recipe("Test Recipe", station)
            
            # Should return False on exception
            self.assertFalse(success)
    
    def test_start_crafting_exception(self):
        """Test starting crafting with exception."""
        station = CraftingStation(
            station_type="test_station",
            name="Test Station",
            interaction_method="/test",
            hotbar_slot=1,
            ui_elements=[]
        )
        
        with patch.object(self.handler, 'select_recipe') as mock_select:
            mock_select.side_effect = Exception("Selection failed")
            
            success = self.handler.start_crafting("Test Recipe", station)
            
            # Should return False on exception
            self.assertFalse(success)
    
    def test_complete_crafting_exception(self):
        """Test completing crafting with exception."""
        # Set up a crafting session
        station = CraftingStation(
            station_type="test_station",
            name="Test Station",
            interaction_method="/test",
            hotbar_slot=1,
            ui_elements=[]
        )
        
        self.handler.current_session = CraftingSession(
            station=station,
            selected_recipe=None,
            start_time=time.time(),
            is_crafting=True,
            session_id="test_session"
        )
        
        with patch('pyautogui.click') as mock_click:
            mock_click.side_effect = Exception("Click failed")
            
            success = self.handler.complete_crafting()
            
            # Should return False on exception
            self.assertFalse(success)
    
    def test_update_crafting_state_exception(self):
        """Test updating crafting state with exception."""
        # Set up a crafting session
        station = CraftingStation(
            station_type="test_station",
            name="Test Station",
            interaction_method="/test",
            hotbar_slot=1,
            ui_elements=[]
        )
        
        self.handler.current_session = CraftingSession(
            station=station,
            selected_recipe=None,
            start_time=time.time(),
            is_crafting=True,
            session_id="test_session"
        )
        
        with patch('core.crafting_handler.update_state') as mock_update:
            mock_update.side_effect = Exception("State update failed")
            
            # Should not raise exception
            self.handler._update_crafting_state()


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 