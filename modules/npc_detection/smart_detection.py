#!/usr/bin/env python3
"""Smart Detection Module for Batch 043.

This module provides the main orchestration for NPC quest signal detection,
matching, and acquisition logic.
"""

import logging
import time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from .quest_icon_detector import QuestIconDetector, NPCDetection
from .npc_matcher import NPCMatcher, NPCMatchResult
from .quest_acquisition import QuestAcquisition


@dataclass
class DetectionResult:
    """Represents the result of a complete detection cycle."""
    npc_detections: List[NPCDetection]
    match_results: List[NPCMatchResult]
    acquisition_results: List[Dict[str, Any]]
    total_detected: int
    total_matched: int
    total_acquired: int
    processing_time: float


class SmartDetection:
    """Main orchestrator for NPC quest signal detection and processing."""
    
    def __init__(self):
        """Initialize the smart detection system."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.icon_detector = QuestIconDetector()
        self.npc_matcher = NPCMatcher()
        self.quest_acquisition = QuestAcquisition()
        
        # Detection settings
        self.scan_interval = 2.0  # seconds between scans
        self.max_detections_per_scan = 10
        self.confidence_threshold = 0.3
        
        # Statistics
        self.stats = {
            'total_scans': 0,
            'total_detections': 0,
            'total_matches': 0,
            'total_acquisitions': 0,
            'total_unmatched': 0,
            'last_scan_time': None
        }
    
    def detect_quest_npcs(self, screen_region: Optional[Tuple[int, int, int, int]] = None) -> DetectionResult:
        """Perform a complete detection cycle for quest-giving NPCs."""
        start_time = time.time()
        self.logger.info("Starting quest NPC detection cycle")
        
        # Step 1: Detect quest icons
        quest_icons = self.icon_detector.detect_quest_icons(screen_region)
        self.logger.info(f"Detected {len(quest_icons)} quest icons")
        
        # Step 2: Scan for NPC names
        npc_detections = self.icon_detector.scan_npc_names(quest_icons)
        self.logger.info(f"Found {len(npc_detections)} NPCs with quest icons")
        
        # Step 3: Match NPCs to quests
        match_results = []
        for npc_detection in npc_detections:
            match_result = self.npc_matcher.match_npc_to_quests(npc_detection)
            match_results.append(match_result)
        
        # Step 4: Trigger quest acquisition
        acquisition_results = []
        for match_result in match_results:
            acquisition_result = self.quest_acquisition.trigger_quest_acquisition(match_result)
            acquisition_results.append(acquisition_result)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update statistics
        self._update_stats(npc_detections, match_results, acquisition_results)
        
        # Create result
        result = DetectionResult(
            npc_detections=npc_detections,
            match_results=match_results,
            acquisition_results=acquisition_results,
            total_detected=len(npc_detections),
            total_matched=len([r for r in match_results if r.best_match]),
            total_acquired=len([r for r in acquisition_results if r.get('success', False)]),
            processing_time=processing_time
        )
        
        self.logger.info(f"Detection cycle completed in {processing_time:.2f}s")
        self.logger.info(f"Results: {result.total_detected} detected, {result.total_matched} matched, {result.total_acquired} acquired")
        
        return result
    
    def process_npc_signals(self, continuous: bool = False, max_cycles: int = 10) -> List[DetectionResult]:
        """Process NPC signals continuously or for a limited number of cycles."""
        self.logger.info(f"Starting NPC signal processing (continuous: {continuous}, max_cycles: {max_cycles})")
        
        results = []
        cycle_count = 0
        
        try:
            while continuous or cycle_count < max_cycles:
                # Perform detection cycle
                result = self.detect_quest_npcs()
                results.append(result)
                
                # Log significant findings
                self._log_significant_findings(result)
                
                # Check if we should continue
                if not continuous:
                    cycle_count += 1
                
                # Wait before next scan
                if continuous or cycle_count < max_cycles:
                    time.sleep(self.scan_interval)
                    
        except KeyboardInterrupt:
            self.logger.info("NPC signal processing interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in NPC signal processing: {e}")
        
        self.logger.info(f"NPC signal processing completed. {len(results)} cycles performed.")
        return results
    
    def _log_significant_findings(self, result: DetectionResult):
        """Log significant findings from detection result."""
        if result.total_acquired > 0:
            self.logger.info(f"🎯 Acquired {result.total_acquired} quests!")
            for acquisition in result.acquisition_results:
                if acquisition.get('success', False):
                    self.logger.info(f"  ✅ {acquisition.get('quest_name', 'Unknown')} from {acquisition.get('npc_name', 'Unknown')}")
        
        if result.total_matched > 0:
            self.logger.info(f"🔍 Found {result.total_matched} NPC-quest matches")
            for match_result in result.match_results:
                if match_result.best_match:
                    self.logger.info(f"  📋 {match_result.best_match.quest_name} (confidence: {match_result.best_match.match_confidence:.2f})")
        
        if result.total_detected > 0:
            self.logger.info(f"👁️ Detected {result.total_detected} NPCs with quest icons")
            for detection in result.npc_detections:
                self.logger.info(f"  👤 {detection.name} at {detection.coordinates}")
    
    def _update_stats(self, npc_detections: List[NPCDetection], 
                     match_results: List[NPCMatchResult], 
                     acquisition_results: List[Dict[str, Any]]):
        """Update detection statistics."""
        self.stats['total_scans'] += 1
        self.stats['total_detections'] += len(npc_detections)
        self.stats['total_matches'] += len([r for r in match_results if r.best_match])
        self.stats['total_acquisitions'] += len([r for r in acquisition_results if r.get('success', False)])
        self.stats['total_unmatched'] += len([r for r in match_results if not r.best_match])
        self.stats['last_scan_time'] = time.time()
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get comprehensive detection statistics."""
        acquisition_stats = self.quest_acquisition.get_acquisition_stats()
        
        return {
            'detection_stats': self.stats,
            'acquisition_stats': acquisition_stats,
            'performance': {
                'avg_processing_time': self._calculate_avg_processing_time(),
                'detection_rate': self._calculate_detection_rate(),
                'match_rate': self._calculate_match_rate(),
                'acquisition_rate': self._calculate_acquisition_rate()
            }
        }
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time per scan."""
        # This would be calculated from actual timing data
        return 0.5  # Placeholder
    
    def _calculate_detection_rate(self) -> float:
        """Calculate detection rate (detections per scan)."""
        if self.stats['total_scans'] == 0:
            return 0.0
        return self.stats['total_detections'] / self.stats['total_scans']
    
    def _calculate_match_rate(self) -> float:
        """Calculate match rate (matches per detection)."""
        if self.stats['total_detections'] == 0:
            return 0.0
        return self.stats['total_matches'] / self.stats['total_detections']
    
    def _calculate_acquisition_rate(self) -> float:
        """Calculate acquisition rate (acquisitions per match)."""
        if self.stats['total_matches'] == 0:
            return 0.0
        return self.stats['total_acquisitions'] / self.stats['total_matches']
    
    def configure_detection(self, scan_interval: Optional[float] = None,
                          max_detections: Optional[int] = None,
                          confidence_threshold: Optional[float] = None):
        """Configure detection parameters."""
        if scan_interval is not None:
            self.scan_interval = scan_interval
            self.logger.info(f"Scan interval set to {scan_interval}s")
        
        if max_detections is not None:
            self.max_detections_per_scan = max_detections
            self.logger.info(f"Max detections per scan set to {max_detections}")
        
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold
            self.logger.info(f"Confidence threshold set to {confidence_threshold}")
    
    def reset_stats(self):
        """Reset detection statistics."""
        self.stats = {
            'total_scans': 0,
            'total_detections': 0,
            'total_matches': 0,
            'total_acquisitions': 0,
            'total_unmatched': 0,
            'last_scan_time': None
        }
        self.logger.info("Detection statistics reset")


def detect_quest_npcs(screen_region: Optional[Tuple[int, int, int, int]] = None) -> DetectionResult:
    """Perform a complete detection cycle for quest-giving NPCs."""
    detector = SmartDetection()
    return detector.detect_quest_npcs(screen_region)


def process_npc_signals(continuous: bool = False, max_cycles: int = 10) -> List[DetectionResult]:
    """Process NPC signals continuously or for a limited number of cycles."""
    detector = SmartDetection()
    return detector.process_npc_signals(continuous, max_cycles) 