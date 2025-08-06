"""REST API endpoint for ticket submission.

This module handles POST requests for support ticket submission,
including validation, ticket generation, storage, and notifications.
"""

import json
import uuid
import smtplib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)


@dataclass
class SupportTicket:
    """Support ticket data structure."""
    ticket_id: str
    name: str
    email: str
    category: str
    priority: str
    subject: str
    message: str
    status: str
    created_at: str
    updated_at: str
    assigned_to: Optional[str] = None
    response: Optional[str] = None
    resolved_at: Optional[str] = None


@dataclass
class TicketResponse:
    """API response structure."""
    success: bool
    ticket_id: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None


class TicketManager:
    """Manages support ticket operations."""
    
    def __init__(self, tickets_file: str = "data/support_tickets.json"):
        """Initialize the ticket manager.
        
        Parameters
        ----------
        tickets_file : str
            Path to the tickets JSON file
        """
        self.tickets_file = Path(tickets_file)
        self.tickets_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing tickets
        self.tickets = self._load_tickets()
        
        # Email configuration
        self.email_config = self._load_email_config()
        
        # Discord configuration
        self.discord_config = self._load_discord_config()
        
        log_event("[TICKET_MANAGER] Ticket manager initialized")

    def _load_tickets(self) -> List[Dict[str, Any]]:
        """Load existing tickets from JSON file."""
        try:
            if self.tickets_file.exists():
                with open(self.tickets_file, 'r') as f:
                    tickets = json.load(f)
                log_event(f"[TICKET_MANAGER] Loaded {len(tickets)} existing tickets")
                return tickets
            else:
                log_event("[TICKET_MANAGER] No existing tickets file found")
                return []
        except Exception as e:
            log_event(f"[TICKET_MANAGER] Error loading tickets: {e}")
            return []

    def _save_tickets(self) -> bool:
        """Save tickets to JSON file."""
        try:
            with open(self.tickets_file, 'w') as f:
                json.dump(self.tickets, f, indent=2, default=str)
            log_event(f"[TICKET_MANAGER] Saved {len(self.tickets)} tickets")
            return True
        except Exception as e:
            log_event(f"[TICKET_MANAGER] Error saving tickets: {e}")
            return False

    def _load_email_config(self) -> Dict[str, Any]:
        """Load email configuration."""
        try:
            config_path = Path("config/email_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                log_event("[TICKET_MANAGER] Loaded email configuration")
                return config
            else:
                log_event("[TICKET_MANAGER] No email config file found")
                return {}
        except Exception as e:
            log_event(f"[TICKET_MANAGER] Error loading email config: {e}")
            return {}

    def _load_discord_config(self) -> Dict[str, Any]:
        """Load Discord configuration."""
        try:
            config_path = Path("config/discord_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                log_event("[TICKET_MANAGER] Loaded Discord configuration")
                return config
            else:
                log_event("[TICKET_MANAGER] No Discord config file found")
                return {}
        except Exception as e:
            log_event(f"[TICKET_MANAGER] Error loading Discord config: {e}")
            return {}

    def validate_ticket_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate ticket submission data.
        
        Parameters
        ----------
        data : dict
            Ticket submission data
            
        Returns
        -------
        List[str]
            List of validation errors
        """
        errors = []
        
        # Required fields
        required_fields = ['name', 'email', 'category', 'priority', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Email validation
        if data.get('email'):
            if '@' not in data['email'] or '.' not in data['email']:
                errors.append("Invalid email format")
        
        # Category validation
        valid_categories = ['account', 'software', 'general']
        if data.get('category') and data['category'] not in valid_categories:
            errors.append(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        # Priority validation
        valid_priorities = ['low', 'medium', 'high']
        if data.get('priority') and data['priority'] not in valid_priorities:
            errors.append(f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")
        
        # Message length validation
        if data.get('message'):
            if len(data['message'].strip()) < 10:
                errors.append("Message must be at least 10 characters long")
            if len(data['message']) > 5000:
                errors.append("Message must be less than 5000 characters")
        
        # Subject length validation
        if data.get('subject'):
            if len(data['subject'].strip()) < 3:
                errors.append("Subject must be at least 3 characters long")
            if len(data['subject']) > 200:
                errors.append("Subject must be less than 200 characters")
        
        return errors

    def generate_ticket_id(self) -> str:
        """Generate a unique ticket ID."""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"TKT-{timestamp}-{unique_id}"

    def create_ticket(self, data: Dict[str, Any]) -> SupportTicket:
        """Create a new support ticket.
        
        Parameters
        ----------
        data : dict
            Ticket submission data
            
        Returns
        -------
        SupportTicket
            Created ticket object
        """
        now = datetime.now().isoformat()
        
        ticket = SupportTicket(
            ticket_id=self.generate_ticket_id(),
            name=data['name'].strip(),
            email=data['email'].strip().lower(),
            category=data['category'].lower(),
            priority=data['priority'].lower(),
            subject=data['subject'].strip(),
            message=data['message'].strip(),
            status='open',
            created_at=now,
            updated_at=now
        )
        
        return ticket

    def add_ticket(self, ticket: SupportTicket) -> bool:
        """Add a ticket to the system.
        
        Parameters
        ----------
        ticket : SupportTicket
            Ticket to add
            
        Returns
        -------
        bool
            True if ticket was added successfully
        """
        try:
            # Convert to dict for JSON serialization
            ticket_dict = asdict(ticket)
            self.tickets.append(ticket_dict)
            
            # Save to file
            success = self._save_tickets()
            
            if success:
                log_event(f"[TICKET_MANAGER] Added ticket {ticket.ticket_id}")
                
                # Send notifications
                self._send_email_notification(ticket)
                self._send_discord_notification(ticket)
                
            return success
            
        except Exception as e:
            log_event(f"[TICKET_MANAGER] Error adding ticket: {e}")
            return False

    def _send_email_notification(self, ticket: SupportTicket) -> bool:
        """Send email notification for new ticket.
        
        Parameters
        ----------
        ticket : SupportTicket
            Ticket to notify about
            
        Returns
        -------
        bool
            True if email sent successfully
        """
        try:
            if not self.email_config:
                log_event("[TICKET_MANAGER] No email configuration available")
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('from_email', 'noreply@ms11.com')
            msg['To'] = self.email_config.get('admin_email', 'admin@ms11.com')
            msg['Subject'] = f"New Support Ticket: {ticket.ticket_id}"
            
            # Email body
            body = f"""
New support ticket submitted:

Ticket ID: {ticket.ticket_id}
Name: {ticket.name}
Email: {ticket.email}
Category: {ticket.category.title()}
Priority: {ticket.priority.title()}
Subject: {ticket.subject}

Message:
{ticket.message}

Submitted: {ticket.created_at}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            if self.email_config.get('smtp_server'):
                with smtplib.SMTP(self.email_config['smtp_server'], self.email_config.get('smtp_port', 587)) as server:
                    if self.email_config.get('use_tls', True):
                        server.starttls()
                    
                    if self.email_config.get('username') and self.email_config.get('password'):
                        server.login(self.email_config['username'], self.email_config['password'])
                    
                    server.send_message(msg)
                
                log_event(f"[TICKET_MANAGER] Email notification sent for ticket {ticket.ticket_id}")
                return True
            else:
                log_event("[TICKET_MANAGER] No SMTP server configured")
                return False
                
        except Exception as e:
            log_event(f"[TICKET_MANAGER] Error sending email notification: {e}")
            return False

    def _send_discord_notification(self, ticket: SupportTicket) -> bool:
        """Send Discord notification for new ticket.
        
        Parameters
        ----------
        ticket : SupportTicket
            Ticket to notify about
            
        Returns
        -------
        bool
            True if Discord notification sent successfully
        """
        try:
            if not self.discord_config.get('webhook_url'):
                log_event("[TICKET_MANAGER] No Discord webhook configured")
                return False
            
            import requests
            
            # Create Discord embed
            embed = {
                "title": f"New Support Ticket: {ticket.ticket_id}",
                "description": ticket.subject,
                "color": self._get_priority_color(ticket.priority),
                "fields": [
                    {
                        "name": "Name",
                        "value": ticket.name,
                        "inline": True
                    },
                    {
                        "name": "Email",
                        "value": ticket.email,
                        "inline": True
                    },
                    {
                        "name": "Category",
                        "value": ticket.category.title(),
                        "inline": True
                    },
                    {
                        "name": "Priority",
                        "value": ticket.priority.title(),
                        "inline": True
                    },
                    {
                        "name": "Message",
                        "value": ticket.message[:1000] + "..." if len(ticket.message) > 1000 else ticket.message,
                        "inline": False
                    }
                ],
                "timestamp": ticket.created_at,
                "footer": {
                    "text": "MS11 Support System"
                }
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.discord_config['webhook_url'],
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 204:
                log_event(f"[TICKET_MANAGER] Discord notification sent for ticket {ticket.ticket_id}")
                return True
            else:
                log_event(f"[TICKET_MANAGER] Discord notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            log_event(f"[TICKET_MANAGER] Error sending Discord notification: {e}")
            return False

    def _get_priority_color(self, priority: str) -> int:
        """Get Discord embed color for priority level."""
        colors = {
            'low': 0x28a745,      # Green
            'medium': 0xffc107,    # Yellow
            'high': 0xdc3545       # Red
        }
        return colors.get(priority, 0x667eea)  # Default blue

    def get_ticket_stats(self) -> Dict[str, Any]:
        """Get ticket statistics."""
        try:
            total_tickets = len(self.tickets)
            open_tickets = len([t for t in self.tickets if t.get('status') == 'open'])
            closed_tickets = len([t for t in self.tickets if t.get('status') == 'closed'])
            
            # Category breakdown
            categories = {}
            for ticket in self.tickets:
                category = ticket.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            # Priority breakdown
            priorities = {}
            for ticket in self.tickets:
                priority = ticket.get('priority', 'unknown')
                priorities[priority] = priorities.get(priority, 0) + 1
            
            return {
                'total_tickets': total_tickets,
                'open_tickets': open_tickets,
                'closed_tickets': closed_tickets,
                'categories': categories,
                'priorities': priorities
            }
            
        except Exception as e:
            log_event(f"[TICKET_MANAGER] Error getting ticket stats: {e}")
            return {}


def handle_ticket_submission(data: Dict[str, Any]) -> TicketResponse:
    """Handle ticket submission request.
    
    Parameters
    ----------
    data : dict
        Ticket submission data from request
        
    Returns
    -------
    TicketResponse
        API response with success status and ticket details
    """
    try:
        # Initialize ticket manager
        manager = TicketManager()
        
        # Validate input data
        errors = manager.validate_ticket_data(data)
        if errors:
            return TicketResponse(
                success=False,
                error="Validation failed",
                message="; ".join(errors)
            )
        
        # Create ticket
        ticket = manager.create_ticket(data)
        
        # Add ticket to system
        if manager.add_ticket(ticket):
            return TicketResponse(
                success=True,
                ticket_id=ticket.ticket_id,
                category=ticket.category,
                priority=ticket.priority,
                message="Ticket submitted successfully"
            )
        else:
            return TicketResponse(
                success=False,
                error="Database error",
                message="Failed to save ticket"
            )
            
    except Exception as e:
        log_event(f"[TICKET_API] Error handling ticket submission: {e}")
        return TicketResponse(
            success=False,
            error="Server error",
            message="Internal server error occurred"
        )


# Flask/FastAPI endpoint handler (example)
def create_ticket_endpoint():
    """Create Flask/FastAPI endpoint for ticket submission."""
    try:
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/api/tickets/submit', methods=['POST'])
        def submit_ticket():
            """Submit a new support ticket."""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No data provided'
                    }), 400
                
                # Handle ticket submission
                response = handle_ticket_submission(data)
                
                if response.success:
                    return jsonify(asdict(response)), 201
                else:
                    return jsonify(asdict(response)), 400
                    
            except Exception as e:
                log_event(f"[TICKET_API] Error in submit endpoint: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Server error',
                    'message': 'Internal server error'
                }), 500
        
        @app.route('/api/tickets/stats', methods=['GET'])
        def get_ticket_stats():
            """Get ticket statistics."""
            try:
                manager = TicketManager()
                stats = manager.get_ticket_stats()
                return jsonify(stats), 200
            except Exception as e:
                log_event(f"[TICKET_API] Error getting stats: {e}")
                return jsonify({'error': 'Failed to get stats'}), 500
        
        return app
        
    except ImportError:
        log_event("[TICKET_API] Flask not available, endpoint not created")
        return None


if __name__ == "__main__":
    # Test the ticket submission
    test_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'category': 'software',
        'priority': 'medium',
        'subject': 'Test Ticket',
        'message': 'This is a test ticket submission.'
    }
    
    response = handle_ticket_submission(test_data)
    print(f"Test response: {asdict(response)}") 