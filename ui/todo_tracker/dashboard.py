"""Dashboard - HTML dashboard interface for Batch 045."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .quest_master import QuestData, QuestStatus, QuestPriority
from .todo_manager import TodoItem, TodoCategory
from .progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class TodoDashboard:
    """Manages the HTML dashboard interface."""
    
    def __init__(self, output_dir: str = "dashboard"):
        """Initialize TodoDashboard with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = Path(__file__).parent / "templates"
    
    def generate_dashboard(self, quests: List[QuestData], todos: List[TodoItem], 
                          progress_tracker: ProgressTracker) -> str:
        """Generate the main dashboard HTML."""
        progress_summary = progress_tracker.get_progress_summary()
        completion_trends = progress_tracker.get_completion_trends()
        planet_progress = progress_tracker.get_planet_progress()
        category_progress = progress_tracker.get_category_progress()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SWGR Todo Tracker Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #6c757d;
            margin-top: 5px;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
        .content-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            padding: 30px;
        }}
        .section {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .section h2 {{
            margin-top: 0;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 10px;
        }}
        .quest-list {{
            max-height: 400px;
            overflow-y: auto;
        }}
        .quest-item {{
            background: white;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #dee2e6;
            transition: all 0.2s ease;
        }}
        .quest-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .quest-item.completed {{
            border-left-color: #28a745;
            opacity: 0.7;
        }}
        .quest-item.in-progress {{
            border-left-color: #ffc107;
        }}
        .quest-item.not-started {{
            border-left-color: #6c757d;
        }}
        .quest-title {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .quest-meta {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        .priority-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .priority-critical {{ background: #dc3545; color: white; }}
        .priority-high {{ background: #fd7e14; color: white; }}
        .priority-medium {{ background: #ffc107; color: black; }}
        .priority-low {{ background: #6c757d; color: white; }}
        .chart-container {{
            height: 300px;
            margin-top: 20px;
        }}
        .trend-chart {{
            width: 100%;
            height: 200px;
            background: white;
            border-radius: 6px;
            padding: 15px;
            margin-top: 10px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}
        @media (max-width: 768px) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SWGR Todo Tracker</h1>
            <p>Track your progress toward 100% completion</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{progress_summary['total_items']}</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{progress_summary['completed_items']}</div>
                <div class="stat-label">Completed</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress_summary['completion_percentage']:.1f}%"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{progress_summary['xp_gained']:,}</div>
                <div class="stat-label">XP Gained</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{progress_summary['credits_gained']:,}</div>
                <div class="stat-label">Credits Earned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{progress_summary['planets_visited']}</div>
                <div class="stat-label">Planets Visited</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{progress_summary['completion_streak']}</div>
                <div class="stat-label">Day Streak</div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="main-content">
                <div class="section">
                    <h2>📋 Recent Quests</h2>
                    <div class="quest-list">
                        {self._generate_quest_list_html(quests[:10])}
                    </div>
                </div>
                
                <div class="section">
                    <h2>✅ Recent Todos</h2>
                    <div class="quest-list">
                        {self._generate_todo_list_html(todos[:10])}
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="section">
                    <h2>📊 Progress Trends</h2>
                    <div class="trend-chart">
                        <canvas id="trendChart"></canvas>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🌍 Planet Progress</h2>
                    {self._generate_planet_progress_html(planet_progress)}
                </div>
                
                <div class="section">
                    <h2>📂 Category Progress</h2>
                    {self._generate_category_progress_html(category_progress)}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Last updated: {progress_summary['last_updated']}</p>
            <p>Generated by SWGR Todo Tracker v1.0</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Chart.js configuration for trends
        const ctx = document.getElementById('trendChart').getContext('2d');
        const trendData = {json.dumps(completion_trends['daily'][-7:])};
        
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: trendData.map(item => item[0]),
                datasets: [{{
                    label: 'Daily Completions',
                    data: trendData.map(item => item[1]),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        return html
    
    def _generate_quest_list_html(self, quests: List[QuestData]) -> str:
        """Generate HTML for quest list."""
        if not quests:
            return "<p>No quests available.</p>"
        
        html_parts = []
        for quest in quests:
            status_class = quest.status.value.replace('_', '-')
            priority_class = f"priority-{quest.priority.value}"
            
            html_parts.append(f"""
                <div class="quest-item {status_class}">
                    <div class="quest-title">
                        {quest.name}
                        <span class="priority-badge {priority_class}">{quest.priority.value.upper()}</span>
                    </div>
                    <div class="quest-meta">
                        🌍 {quest.planet} • 🎯 {quest.xp_reward} XP • 💰 {quest.credit_reward} Credits
                        {f' • 👤 {quest.npc}' if quest.npc else ''}
                    </div>
                </div>
            """)
        
        return ''.join(html_parts)
    
    def _generate_todo_list_html(self, todos: List[TodoItem]) -> str:
        """Generate HTML for todo list."""
        if not todos:
            return "<p>No todos available.</p>"
        
        html_parts = []
        for todo in todos:
            status_class = todo.status.value.replace('_', '-')
            priority_class = f"priority-{todo.priority.value}"
            
            html_parts.append(f"""
                <div class="quest-item {status_class}">
                    <div class="quest-title">
                        {todo.title}
                        <span class="priority-badge {priority_class}">{todo.priority.value.upper()}</span>
                    </div>
                    <div class="quest-meta">
                        📂 {todo.category.value.title()} • 🌍 {todo.planet or 'Any'}
                        {f' • ⏱️ {todo.estimated_time} min' if todo.estimated_time else ''}
                    </div>
                </div>
            """)
        
        return ''.join(html_parts)
    
    def _generate_planet_progress_html(self, planet_progress: Dict[str, Dict[str, Any]]) -> str:
        """Generate HTML for planet progress."""
        if not planet_progress:
            return "<p>No planet data available.</p>"
        
        html_parts = []
        for planet, data in planet_progress.items():
            completion_pct = data.get('completion_percentage', 0)
            html_parts.append(f"""
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <strong>{planet.title()}</strong>
                        <span>{completion_pct:.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {completion_pct}%"></div>
                    </div>
                </div>
            """)
        
        return ''.join(html_parts)
    
    def _generate_category_progress_html(self, category_progress: Dict[str, Dict[str, Any]]) -> str:
        """Generate HTML for category progress."""
        if not category_progress:
            return "<p>No category data available.</p>"
        
        html_parts = []
        for category, count in category_progress.items():
            html_parts.append(f"""
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span>{category.title()}</span>
                    <strong>{count}</strong>
                </div>
            """)
        
        return ''.join(html_parts)
    
    def save_dashboard(self, quests: List[QuestData], todos: List[TodoItem], 
                      progress_tracker: ProgressTracker) -> str:
        """Generate and save the dashboard HTML file."""
        html_content = self.generate_dashboard(quests, todos, progress_tracker)
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Dashboard saved to {output_file}")
        return str(output_file)


def generate_html_dashboard(quests: List[QuestData], todos: List[TodoItem], 
                          progress_tracker: ProgressTracker, output_dir: str = "dashboard") -> str:
    """Convenience function to generate and save dashboard."""
    dashboard = TodoDashboard(output_dir)
    return dashboard.save_dashboard(quests, todos, progress_tracker) 