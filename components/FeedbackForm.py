#!/usr/bin/env python3
"""
Enhanced Feedback Form Component for SWGDB
Supports bug reports, suggestions, and mod conflicts with Discord integration
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from flask import Flask, render_template, request, jsonify, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, HiddenField
from wtforms.validators import DataRequired, Length, Optional as OptionalValidator
import requests
import logging
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackForm(FlaskForm):
    """Enhanced feedback form with comprehensive validation"""
    
    # Basic fields
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=5, max=100, message='Title must be between 5-100 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required'),
        Length(min=10, max=2000, message='Description must be between 10-2000 characters')
    ])
    
    # Category selection with auto-tagging
    category = SelectField('Category', choices=[
        ('bug', '🐞 Bug Report'),
        ('feature', '💡 Feature Request'),
        ('mod', '🛠 Mod Conflict'),
        ('UI', '🎨 UI/UX Issue'),
        ('content', '📝 Content Issue'),
        ('suggestion', '💭 General Suggestion')
    ], validators=[DataRequired()])
    
    # Priority level
    priority = SelectField('Priority', choices=[
        ('Low', 'Low - Minor issue'),
        ('Medium', 'Medium - Affects functionality'),
        ('High', 'High - Blocks usage')
    ], default='Medium', validators=[DataRequired()])
    
    # Optional fields
    screenshot = FileField('Screenshot (Optional)')
    user_contact = StringField('Contact (Optional)', validators=[
        OptionalValidator(),
        Length(max=100, message='Contact must be under 100 characters')
    ])
    
    # System info (hidden, populated via JavaScript)
    user_agent = HiddenField()
    page_url = HiddenField()
    
    # Mod-specific fields (shown conditionally)
    mod_name = StringField('Mod Name (if applicable)', validators=[
        OptionalValidator(),
        Length(max=50, message='Mod name must be under 50 characters')
    ])

class FeedbackManager:
    """Enhanced feedback management with Discord integration and file storage"""
    
    def __init__(self, base_dir: str = "feedback"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Initialize subdirectories
        (self.base_dir / "bug_reports").mkdir(exist_ok=True)
        (self.base_dir / "feature_requests").mkdir(exist_ok=True)
        (self.base_dir / "mod_conflicts").mkdir(exist_ok=True)
        (self.base_dir / "suggestions").mkdir(exist_ok=True)
        
        # Discord webhook URL (set via environment variable)
        self.discord_webhook_url = os.getenv('DISCORD_FEEDBACK_WEBHOOK_URL')
        
        # Legacy JSON file for compatibility
        self.json_file = Path("data/feedback_reports.json")
        self.json_file.parent.mkdir(exist_ok=True)
        
    def auto_tag_feedback(self, title: str, description: str, category: str) -> List[str]:
        """Automatically generate tags based on content analysis"""
        tags = [category]
        
        # Content-based tagging
        content = f"{title} {description}".lower()
        
        # Technical tags
        if any(word in content for word in ['crash', 'error', 'exception', 'fail']):
            tags.append('crash')
        if any(word in content for word in ['slow', 'lag', 'performance', 'fps']):
            tags.append('performance')
        if any(word in content for word in ['ui', 'interface', 'button', 'menu']):
            tags.append('ui')
        if any(word in content for word in ['quest', 'mission', 'npc']):
            tags.append('gameplay')
        if any(word in content for word in ['profession', 'skill', 'xp', 'level']):
            tags.append('progression')
        if any(word in content for word in ['combat', 'weapon', 'armor', 'stats']):
            tags.append('combat')
        if any(word in content for word in ['vendor', 'bazaar', 'shop', 'credits']):
            tags.append('economy')
        
        # Priority-based tags
        if any(word in content for word in ['urgent', 'critical', 'broken', 'unusable']):
            tags.append('urgent')
        if any(word in content for word in ['enhancement', 'improve', 'better', 'suggest']):
            tags.append('enhancement')
            
        return list(set(tags))  # Remove duplicates
    
    def create_feedback_id(self, category: str) -> str:
        """Generate unique feedback ID with category prefix"""
        prefix_map = {
            'bug': 'BUG',
            'feature': 'FEAT',
            'mod': 'MOD',
            'UI': 'UI',
            'content': 'CONT',
            'suggestion': 'SUGG'
        }
        
        prefix = prefix_map.get(category, 'FEED')
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = uuid.uuid4().hex[:6].upper()
        
        return f"{prefix}-{timestamp}-{unique_id}"
    
    def save_as_markdown(self, feedback_data: Dict) -> str:
        """Save feedback as Markdown file"""
        category = feedback_data['category']
        feedback_id = feedback_data['id']
        
        # Determine subdirectory
        subdir_map = {
            'bug': 'bug_reports',
            'feature': 'feature_requests', 
            'mod': 'mod_conflicts',
            'UI': 'bug_reports',
            'content': 'suggestions',
            'suggestion': 'suggestions'
        }
        
        subdir = self.base_dir / subdir_map.get(category, 'suggestions')
        file_path = subdir / f"{feedback_id}.md"
        
        # Generate Markdown content
        markdown_content = self._generate_markdown(feedback_data)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Feedback saved as Markdown: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving Markdown: {e}")
            raise
    
    def save_as_yaml(self, feedback_data: Dict) -> str:
        """Save feedback as YAML file for structured processing"""
        category = feedback_data['category']
        feedback_id = feedback_data['id']
        
        file_path = self.base_dir / f"{feedback_id}.yaml"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(feedback_data, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Feedback saved as YAML: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving YAML: {e}")
            raise
    
    def _generate_markdown(self, data: Dict) -> str:
        """Generate Markdown format for feedback"""
        tags_str = ", ".join(f"`{tag}`" for tag in data.get('tags', []))
        
        markdown = f"""# {data['title']}

**ID:** `{data['id']}`  
**Category:** {data['category']}  
**Priority:** {data['priority']}  
**Status:** {data['status']}  
**Tags:** {tags_str}  
**Submitted:** {data['submitted_at']}  

## Description

{data['description']}

## Technical Details

- **User Agent:** `{data.get('user_agent', 'N/A')}`
- **Page URL:** `{data.get('page_url', 'N/A')}`
- **Contact:** `{data.get('user_contact', 'N/A')}`

"""
        
        # Add mod-specific information
        if data.get('mod_name'):
            markdown += f"- **Mod Name:** `{data['mod_name']}`\n"
        
        if data.get('screenshot_url'):
            markdown += f"\n## Screenshot\n\n![Screenshot]({data['screenshot_url']})\n"
        
        markdown += f"""
## Admin Notes

**Assigned To:** {data.get('assigned_to', 'Unassigned')}  
**Notes:** {data.get('notes', 'None')}  

---
*This feedback was automatically generated by SWGDB Feedback System*
"""
        
        return markdown
    
    def send_discord_notification(self, feedback_data: Dict) -> bool:
        """Send Discord webhook notification"""
        if not self.discord_webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False
        
        try:
            # Create Discord embed
            embed = {
                "title": f"New {feedback_data['category'].title()}: {feedback_data['title']}",
                "description": feedback_data['description'][:500] + "..." if len(feedback_data['description']) > 500 else feedback_data['description'],
                "color": self._get_priority_color(feedback_data['priority']),
                "fields": [
                    {
                        "name": "Category",
                        "value": feedback_data['category'],
                        "inline": True
                    },
                    {
                        "name": "Priority", 
                        "value": feedback_data['priority'],
                        "inline": True
                    },
                    {
                        "name": "ID",
                        "value": f"`{feedback_data['id']}`",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"SWGDB Feedback System • {feedback_data['submitted_at']}"
                },
                "timestamp": feedback_data['submitted_at']
            }
            
            # Add tags field if present
            if feedback_data.get('tags'):
                embed["fields"].append({
                    "name": "Tags",
                    "value": ", ".join(f"`{tag}`" for tag in feedback_data['tags']),
                    "inline": False
                })
            
            # Add mod name if present
            if feedback_data.get('mod_name'):
                embed["fields"].append({
                    "name": "Mod Name",
                    "value": f"`{feedback_data['mod_name']}`",
                    "inline": True
                })
            
            payload = {
                "embeds": [embed],
                "username": "SWGDB Feedback",
                "avatar_url": "https://via.placeholder.com/64x64.png?text=SWGDB"
            }
            
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info(f"Discord notification sent for feedback {feedback_data['id']}")
                return True
            else:
                logger.error(f"Discord webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False
    
    def _get_priority_color(self, priority: str) -> int:
        """Get Discord embed color based on priority"""
        color_map = {
            'Low': 0x95a5a6,      # Gray
            'Medium': 0xf39c12,   # Orange  
            'High': 0xe74c3c      # Red
        }
        return color_map.get(priority, 0x3498db)  # Default blue
    
    def save_to_legacy_json(self, feedback_data: Dict) -> bool:
        """Save to legacy JSON format for compatibility"""
        try:
            # Load existing data
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    "feedback_reports": [],
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "2.0",
                        "description": "Enhanced feedback system with Discord integration"
                    }
                }
            
            # Add new feedback
            data["feedback_reports"].append(feedback_data)
            
            # Save back to file
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving to legacy JSON: {e}")
            return False
    
    def submit_feedback(self, form_data: Dict) -> Tuple[bool, str, Dict]:
        """Process and save feedback submission"""
        try:
            # Create feedback object
            feedback_id = self.create_feedback_id(form_data['category'])
            
            feedback_data = {
                "id": feedback_id,
                "title": form_data['title'].strip(),
                "description": form_data['description'].strip(),
                "category": form_data['category'],
                "priority": form_data['priority'],
                "user_agent": form_data.get('user_agent', ''),
                "page_url": form_data.get('page_url', ''),
                "user_contact": form_data.get('user_contact', ''),
                "mod_name": form_data.get('mod_name', ''),
                "submitted_at": datetime.now().isoformat(),
                "status": "New",
                "assigned_to": None,
                "notes": "",
                "tags": self.auto_tag_feedback(form_data['title'], form_data['description'], form_data['category'])
            }
            
            # Save in multiple formats
            markdown_path = self.save_as_markdown(feedback_data)
            yaml_path = self.save_as_yaml(feedback_data) 
            json_saved = self.save_to_legacy_json(feedback_data)
            
            # Send Discord notification
            discord_sent = self.send_discord_notification(feedback_data)
            
            logger.info(f"Feedback {feedback_id} processed successfully")
            
            success_message = f"Thank you! Your feedback has been submitted with ID: {feedback_id}"
            if discord_sent:
                success_message += " Our team has been notified via Discord."
            
            return True, success_message, feedback_data
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return False, f"Error processing feedback: {str(e)}", {}

# Initialize global feedback manager
feedback_manager = FeedbackManager()