"""Quest Planner - Planning and prerequisite analysis for Batch 045."""

import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
import logging

from .quest_master import QuestData, QuestStatus, QuestPriority
from .todo_manager import TodoItem, TodoCategory

logger = logging.getLogger(__name__)


@dataclass
class QuestChain:
    """Represents a chain of related quests."""
    id: str
    name: str
    quests: List[QuestData] = field(default_factory=list)
    total_xp: int = 0
    total_credits: int = 0
    estimated_time: int = 0  # in minutes
    difficulty: str = "normal"
    prerequisites: List[str] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'quests': [quest.id for quest in self.quests],
            'total_xp': self.total_xp,
            'total_credits': self.total_credits,
            'estimated_time': self.estimated_time,
            'difficulty': self.difficulty,
            'prerequisites': self.prerequisites,
            'rewards': self.rewards
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], quest_master) -> 'QuestChain':
        """Create from dictionary."""
        quests = [quest_master.get_quest(qid) for qid in data.get('quests', [])]
        quests = [q for q in quests if q is not None]
        
        return cls(
            id=data['id'],
            name=data['name'],
            quests=quests,
            total_xp=data.get('total_xp', 0),
            total_credits=data.get('total_credits', 0),
            estimated_time=data.get('estimated_time', 0),
            difficulty=data.get('difficulty', 'normal'),
            prerequisites=data.get('prerequisites', []),
            rewards=data.get('rewards', {})
        )


class PrerequisiteAnalyzer:
    """Analyzes quest prerequisites and dependencies."""
    
    def __init__(self, quest_master):
        """Initialize with quest master."""
        self.quest_master = quest_master
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependencies: Dict[str, Set[str]] = {}
        self._build_dependency_graph()
    
    def _build_dependency_graph(self):
        """Build dependency graph from quest data."""
        for quest_id, quest in self.quest_master.quests.items():
            self.dependency_graph[quest_id] = set(quest.prerequisites)
            
            # Build reverse dependencies
            for prereq_id in quest.prerequisites:
                if prereq_id not in self.reverse_dependencies:
                    self.reverse_dependencies[prereq_id] = set()
                self.reverse_dependencies[prereq_id].add(quest_id)
    
    def get_direct_prerequisites(self, quest_id: str) -> List[QuestData]:
        """Get direct prerequisites for a quest."""
        prereq_ids = self.dependency_graph.get(quest_id, set())
        return [self.quest_master.get_quest(qid) for qid in prereq_ids 
                if self.quest_master.get_quest(qid)]
    
    def get_all_prerequisites(self, quest_id: str) -> List[QuestData]:
        """Get all prerequisites (including prerequisites of prerequisites)."""
        all_prereqs = set()
        to_check = {quest_id}
        
        while to_check:
            current = to_check.pop()
            prereqs = self.dependency_graph.get(current, set())
            
            for prereq_id in prereqs:
                if prereq_id not in all_prereqs:
                    all_prereqs.add(prereq_id)
                    to_check.add(prereq_id)
        
        return [self.quest_master.get_quest(qid) for qid in all_prereqs 
                if self.quest_master.get_quest(qid)]
    
    def get_dependents(self, quest_id: str) -> List[QuestData]:
        """Get quests that depend on this quest."""
        dependent_ids = self.reverse_dependencies.get(quest_id, set())
        return [self.quest_master.get_quest(qid) for qid in dependent_ids 
                if self.quest_master.get_quest(qid)]
    
    def check_prerequisites_met(self, quest_id: str) -> bool:
        """Check if all prerequisites for a quest are met."""
        prereqs = self.get_direct_prerequisites(quest_id)
        return all(prereq.status == QuestStatus.COMPLETED for prereq in prereqs)
    
    def get_blocking_quests(self, quest_id: str) -> List[QuestData]:
        """Get quests that are blocking this quest (incomplete prerequisites)."""
        prereqs = self.get_direct_prerequisites(quest_id)
        return [prereq for prereq in prereqs if prereq.status != QuestStatus.COMPLETED]
    
    def get_quest_chain(self, quest_id: str) -> QuestChain:
        """Get the complete quest chain for a quest."""
        all_prereqs = self.get_all_prerequisites(quest_id)
        target_quest = self.quest_master.get_quest(quest_id)
        
        if not target_quest:
            return None
        
        # Create chain with all prerequisites + target quest
        chain_quests = all_prereqs + [target_quest]
        
        # Calculate totals
        total_xp = sum(q.xp_reward for q in chain_quests)
        total_credits = sum(q.credit_reward for q in chain_quests)
        estimated_time = sum(30 for q in chain_quests)  # Assume 30 min per quest
        
        # Determine difficulty based on quest difficulties
        difficulties = [q.difficulty for q in chain_quests]
        if 'hard' in difficulties:
            difficulty = 'hard'
        elif 'medium' in difficulties:
            difficulty = 'medium'
        else:
            difficulty = 'easy'
        
        return QuestChain(
            id=f"chain_{quest_id}",
            name=f"Quest Chain for {target_quest.name}",
            quests=chain_quests,
            total_xp=total_xp,
            total_credits=total_credits,
            estimated_time=estimated_time,
            difficulty=difficulty
        )
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the quest graph."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
            path.pop()
        
        for quest_id in self.quest_master.quests:
            if quest_id not in visited:
                dfs(quest_id, [])
        
        return cycles


class QuestPlanner:
    """Plans quest completion strategies."""
    
    def __init__(self, quest_master, todo_manager):
        """Initialize planner with managers."""
        self.quest_master = quest_master
        self.todo_manager = todo_manager
        self.prerequisite_analyzer = PrerequisiteAnalyzer(quest_master)
        self.plans: Dict[str, Dict[str, Any]] = {}
    
    def create_optimization_plan(self, target_quests: List[str] = None, 
                                max_time: int = 480) -> Dict[str, Any]:
        """Create an optimized quest completion plan."""
        if target_quests is None:
            # Get all available quests
            target_quests = [q.id for q in self.quest_master.get_available_quests()]
        
        plan = {
            'target_quests': target_quests,
            'max_time': max_time,
            'estimated_time': 0,
            'total_xp': 0,
            'total_credits': 0,
            'quest_order': [],
            'prerequisites': [],
            'blockers': [],
            'efficiency_score': 0.0
        }
        
        # Analyze each target quest
        for quest_id in target_quests:
            quest = self.quest_master.get_quest(quest_id)
            if not quest:
                continue
            
            # Get quest chain
            chain = self.prerequisite_analyzer.get_quest_chain(quest_id)
            if not chain:
                continue
            
            # Check if prerequisites are met
            if self.prerequisite_analyzer.check_prerequisites_met(quest_id):
                plan['quest_order'].append({
                    'quest_id': quest_id,
                    'quest_name': quest.name,
                    'xp_reward': quest.xp_reward,
                    'credit_reward': quest.credit_reward,
                    'estimated_time': 30,
                    'status': 'ready'
                })
                plan['estimated_time'] += 30
                plan['total_xp'] += quest.xp_reward
                plan['total_credits'] += quest.credit_reward
            else:
                # Add prerequisites to plan
                blockers = self.prerequisite_analyzer.get_blocking_quests(quest_id)
                for blocker in blockers:
                    plan['prerequisites'].append({
                        'quest_id': blocker.id,
                        'quest_name': blocker.name,
                        'xp_reward': blocker.xp_reward,
                        'credit_reward': blocker.credit_reward,
                        'estimated_time': 30,
                        'blocks': quest_id
                    })
                    plan['estimated_time'] += 30
                    plan['total_xp'] += blocker.xp_reward
                    plan['total_credits'] += blocker.credit_reward
                
                plan['blockers'].append({
                    'quest_id': quest_id,
                    'quest_name': quest.name,
                    'blocked_by': [b.id for b in blockers]
                })
        
        # Calculate efficiency score
        if plan['estimated_time'] > 0:
            plan['efficiency_score'] = (plan['total_xp'] + plan['total_credits'] / 100) / plan['estimated_time']
        
        return plan
    
    def create_planet_completion_plan(self, planet: str) -> Dict[str, Any]:
        """Create a plan for completing all quests on a specific planet."""
        planet_quests = self.quest_master.get_quests_by_planet(planet)
        quest_ids = [q.id for q in planet_quests]
        
        return self.create_optimization_plan(quest_ids)
    
    def create_priority_plan(self, priority: QuestPriority) -> Dict[str, Any]:
        """Create a plan for completing all quests of a specific priority."""
        priority_quests = self.quest_master.get_quests_by_priority(priority)
        quest_ids = [q.id for q in priority_quests]
        
        return self.create_optimization_plan(quest_ids)
    
    def create_time_based_plan(self, available_time: int) -> Dict[str, Any]:
        """Create a plan that fits within available time."""
        available_quests = self.quest_master.get_available_quests()
        
        # Sort by efficiency (XP + credits per time)
        quest_efficiency = []
        for quest in available_quests:
            efficiency = (quest.xp_reward + quest.credit_reward / 100) / 30  # 30 min per quest
            quest_efficiency.append((quest, efficiency))
        
        # Sort by efficiency (highest first)
        quest_efficiency.sort(key=lambda x: x[1], reverse=True)
        
        plan = {
            'available_time': available_time,
            'used_time': 0,
            'quests': [],
            'total_xp': 0,
            'total_credits': 0,
            'efficiency_score': 0.0
        }
        
        for quest, efficiency in quest_efficiency:
            if plan['used_time'] + 30 <= available_time:
                plan['quests'].append({
                    'quest_id': quest.id,
                    'quest_name': quest.name,
                    'xp_reward': quest.xp_reward,
                    'credit_reward': quest.credit_reward,
                    'efficiency': efficiency
                })
                plan['used_time'] += 30
                plan['total_xp'] += quest.xp_reward
                plan['total_credits'] += quest.credit_reward
        
        if plan['used_time'] > 0:
            plan['efficiency_score'] = (plan['total_xp'] + plan['total_credits'] / 100) / plan['used_time']
        
        return plan
    
    def get_quest_recommendations(self, player_level: int = None, 
                                 preferred_planets: List[str] = None) -> List[Dict[str, Any]]:
        """Get personalized quest recommendations."""
        recommendations = []
        
        # Get available quests
        available_quests = self.quest_master.get_available_quests()
        
        for quest in available_quests:
            score = 0
            reasons = []
            
            # Score based on XP reward
            if quest.xp_reward > 1000:
                score += 3
                reasons.append("High XP reward")
            elif quest.xp_reward > 500:
                score += 2
                reasons.append("Good XP reward")
            else:
                score += 1
                reasons.append("Low XP reward")
            
            # Score based on credit reward
            if quest.credit_reward > 5000:
                score += 2
                reasons.append("High credit reward")
            elif quest.credit_reward > 1000:
                score += 1
                reasons.append("Good credit reward")
            
            # Score based on planet preference
            if preferred_planets and quest.planet in preferred_planets:
                score += 2
                reasons.append("Preferred planet")
            
            # Score based on priority
            if quest.priority == QuestPriority.CRITICAL:
                score += 3
                reasons.append("Critical priority")
            elif quest.priority == QuestPriority.HIGH:
                score += 2
                reasons.append("High priority")
            elif quest.priority == QuestPriority.MEDIUM:
                score += 1
                reasons.append("Medium priority")
            
            # Score based on difficulty
            if quest.difficulty == "easy":
                score += 1
                reasons.append("Easy quest")
            elif quest.difficulty == "hard":
                score -= 1
                reasons.append("Hard quest")
            
            recommendations.append({
                'quest_id': quest.id,
                'quest_name': quest.name,
                'planet': quest.planet,
                'xp_reward': quest.xp_reward,
                'credit_reward': quest.credit_reward,
                'priority': quest.priority.value,
                'difficulty': quest.difficulty,
                'score': score,
                'reasons': reasons
            })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def save_plan(self, plan_name: str, plan_data: Dict[str, Any]):
        """Save a plan for later use."""
        self.plans[plan_name] = {
            'data': plan_data,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        logger.info(f"Saved plan: {plan_name}")
    
    def load_plan(self, plan_name: str) -> Optional[Dict[str, Any]]:
        """Load a saved plan."""
        if plan_name in self.plans:
            return self.plans[plan_name]['data']
        return None
    
    def list_plans(self) -> List[str]:
        """List all saved plans."""
        return list(self.plans.keys())
    
    def delete_plan(self, plan_name: str):
        """Delete a saved plan."""
        if plan_name in self.plans:
            del self.plans[plan_name]
            logger.info(f"Deleted plan: {plan_name}")
    
    def export_plan(self, plan_name: str, output_file: str):
        """Export a plan to JSON file."""
        plan = self.load_plan(plan_name)
        if plan:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported plan {plan_name} to {output_file}")
    
    def import_plan(self, input_file: str, plan_name: str):
        """Import a plan from JSON file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            self.save_plan(plan_name, plan_data)
            logger.info(f"Imported plan from {input_file} as {plan_name}")
            
        except Exception as e:
            logger.error(f"Error importing plan from {input_file}: {e}") 