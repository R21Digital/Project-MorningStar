"""Test Batch 078 - Support System + Ticket Generator.

This test suite validates the support system functionality including ticket submission,
validation, notifications, and admin dashboard features.
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from api.tickets.post_ticket import (
    TicketManager,
    SupportTicket,
    TicketResponse,
    handle_ticket_submission
)
from discord_alerts.support_notifications import (
    SupportDiscordNotifier,
    SupportNotification,
    create_support_notifier
)


class TestTicketManager:
    """Test the TicketManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tickets_file = Path(self.temp_dir) / "support_tickets.json"
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test configuration files
        self._create_test_configs()
        
        # Initialize ticket manager
        self.manager = TicketManager(str(self.tickets_file))

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_test_configs(self):
        """Create test configuration files."""
        # Email config
        email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "noreply@ms11.com",
            "admin_email": "admin@ms11.com",
            "use_tls": True
        }
        
        with open(self.config_dir / "email_config.json", 'w') as f:
            json.dump(email_config, f)
        
        # Discord config
        discord_config = {
            "discord_token": "test_token",
            "support_webhook_url": "https://discord.com/api/webhooks/test",
            "support_channel_id": 123456789,
            "target_user_id": 987654321
        }
        
        with open(self.config_dir / "discord_config.json", 'w') as f:
            json.dump(discord_config, f)

    def test_validate_ticket_data_valid(self):
        """Test ticket data validation with valid data."""
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message with sufficient length.'
        }
        
        errors = self.manager.validate_ticket_data(valid_data)
        assert len(errors) == 0

    def test_validate_ticket_data_missing_fields(self):
        """Test ticket data validation with missing fields."""
        invalid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            # Missing category, priority, subject, message
        }
        
        errors = self.manager.validate_ticket_data(invalid_data)
        assert len(errors) > 0
        assert any('Missing required field' in error for error in errors)

    def test_validate_ticket_data_invalid_email(self):
        """Test ticket data validation with invalid email."""
        invalid_data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        errors = self.manager.validate_ticket_data(invalid_data)
        assert any('Invalid email format' in error for error in errors)

    def test_validate_ticket_data_invalid_category(self):
        """Test ticket data validation with invalid category."""
        invalid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'invalid_category',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        errors = self.manager.validate_ticket_data(invalid_data)
        assert any('Invalid category' in error for error in errors)

    def test_validate_ticket_data_invalid_priority(self):
        """Test ticket data validation with invalid priority."""
        invalid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'invalid_priority',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        errors = self.manager.validate_ticket_data(invalid_data)
        assert any('Invalid priority' in error for error in errors)

    def test_validate_ticket_data_short_message(self):
        """Test ticket data validation with short message."""
        invalid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'Short'
        }
        
        errors = self.manager.validate_ticket_data(invalid_data)
        assert any('at least 10 characters' in error for error in errors)

    def test_validate_ticket_data_long_message(self):
        """Test ticket data validation with long message."""
        invalid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'A' * 6000  # Too long
        }
        
        errors = self.manager.validate_ticket_data(invalid_data)
        assert any('less than 5000 characters' in error for error in errors)

    def test_generate_ticket_id(self):
        """Test ticket ID generation."""
        ticket_id = self.manager.generate_ticket_id()
        
        assert ticket_id.startswith('TKT-')
        assert len(ticket_id) > 10
        assert '-' in ticket_id

    def test_create_ticket(self):
        """Test ticket creation."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        ticket = self.manager.create_ticket(data)
        
        assert isinstance(ticket, SupportTicket)
        assert ticket.name == 'John Doe'
        assert ticket.email == 'john@example.com'
        assert ticket.category == 'software'
        assert ticket.priority == 'medium'
        assert ticket.subject == 'Test Subject'
        assert ticket.message == 'This is a test message.'
        assert ticket.status == 'open'
        assert ticket.ticket_id.startswith('TKT-')

    def test_add_ticket(self):
        """Test adding a ticket to the system."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        ticket = self.manager.create_ticket(data)
        success = self.manager.add_ticket(ticket)
        
        assert success is True
        assert len(self.manager.tickets) == 1
        assert self.manager.tickets[0]['ticket_id'] == ticket.ticket_id

    def test_get_ticket_stats(self):
        """Test getting ticket statistics."""
        # Add some test tickets
        tickets_data = [
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'category': 'software',
                'priority': 'high',
                'subject': 'High Priority Issue',
                'message': 'This is a high priority issue.'
            },
            {
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'category': 'account',
                'priority': 'medium',
                'subject': 'Account Issue',
                'message': 'This is an account issue.'
            },
            {
                'name': 'Bob Wilson',
                'email': 'bob@example.com',
                'category': 'general',
                'priority': 'low',
                'subject': 'General Question',
                'message': 'This is a general question.'
            }
        ]
        
        for data in tickets_data:
            ticket = self.manager.create_ticket(data)
            self.manager.add_ticket(ticket)
        
        stats = self.manager.get_ticket_stats()
        
        assert stats['total_tickets'] == 3
        assert stats['open_tickets'] == 3
        assert stats['closed_tickets'] == 0
        assert stats['categories']['software'] == 1
        assert stats['categories']['account'] == 1
        assert stats['categories']['general'] == 1
        assert stats['priorities']['high'] == 1
        assert stats['priorities']['medium'] == 1
        assert stats['priorities']['low'] == 1

    @patch('api.tickets.post_ticket.smtplib.SMTP')
    def test_send_email_notification(self, mock_smtp):
        """Test email notification sending."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'high',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        ticket = self.manager.create_ticket(data)
        
        # Mock SMTP
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        success = self.manager._send_email_notification(ticket)
        
        # Should fail without proper SMTP configuration
        assert success is False

    @patch('api.tickets.post_ticket.requests.post')
    def test_send_discord_notification(self, mock_post):
        """Test Discord notification sending."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'high',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        ticket = self.manager.create_ticket(data)
        
        # Mock successful Discord response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        success = self.manager._send_discord_notification(ticket)
        
        assert success is True
        mock_post.assert_called_once()

    def test_get_priority_color(self):
        """Test priority color mapping."""
        colors = {
            'low': 0x28a745,
            'medium': 0xffc107,
            'high': 0xdc3545
        }
        
        for priority, expected_color in colors.items():
            color = self.manager._get_priority_color(priority)
            assert color == expected_color


class TestTicketSubmission:
    """Test ticket submission functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tickets_file = Path(self.temp_dir) / "support_tickets.json"

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_handle_ticket_submission_success(self):
        """Test successful ticket submission."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message with sufficient length.'
        }
        
        with patch('api.tickets.post_ticket.TicketManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            # Mock validation
            mock_manager.validate_ticket_data.return_value = []
            
            # Mock ticket creation
            mock_ticket = Mock()
            mock_ticket.ticket_id = 'TKT-20250101-TEST123'
            mock_ticket.category = 'software'
            mock_ticket.priority = 'medium'
            mock_manager.create_ticket.return_value = mock_ticket
            
            # Mock ticket addition
            mock_manager.add_ticket.return_value = True
            
            response = handle_ticket_submission(data)
            
            assert response.success is True
            assert response.ticket_id == 'TKT-20250101-TEST123'
            assert response.category == 'software'
            assert response.priority == 'medium'

    def test_handle_ticket_submission_validation_failure(self):
        """Test ticket submission with validation failure."""
        data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'Short'
        }
        
        with patch('api.tickets.post_ticket.TicketManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            # Mock validation failure
            mock_manager.validate_ticket_data.return_value = [
                'Invalid email format',
                'Message must be at least 10 characters long'
            ]
            
            response = handle_ticket_submission(data)
            
            assert response.success is False
            assert 'Validation failed' in response.error
            assert 'Invalid email format' in response.message

    def test_handle_ticket_submission_database_error(self):
        """Test ticket submission with database error."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message with sufficient length.'
        }
        
        with patch('api.tickets.post_ticket.TicketManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            # Mock validation
            mock_manager.validate_ticket_data.return_value = []
            
            # Mock ticket creation
            mock_ticket = Mock()
            mock_manager.create_ticket.return_value = mock_ticket
            
            # Mock ticket addition failure
            mock_manager.add_ticket.return_value = False
            
            response = handle_ticket_submission(data)
            
            assert response.success is False
            assert 'Database error' in response.error

    def test_handle_ticket_submission_exception(self):
        """Test ticket submission with exception."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        with patch('api.tickets.post_ticket.TicketManager') as mock_manager_class:
            mock_manager_class.side_effect = Exception("Test exception")
            
            response = handle_ticket_submission(data)
            
            assert response.success is False
            assert 'Server error' in response.error


class TestSupportDiscordNotifier:
    """Test the SupportDiscordNotifier class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test Discord config
        discord_config = {
            "support_webhook_url": "https://discord.com/api/webhooks/test",
            "discord_token": "test_token",
            "support_channel_id": 123456789
        }
        
        with open(self.config_dir / "discord_config.json", 'w') as f:
            json.dump(discord_config, f)
        
        # Initialize notifier
        self.notifier = SupportDiscordNotifier()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_get_priority_color(self):
        """Test priority color mapping."""
        colors = {
            'low': 'green',
            'medium': 'gold',
            'high': 'red',
            'urgent': 'dark_red'
        }
        
        for priority, expected_color in colors.items():
            color = self.notifier._get_priority_color(priority)
            assert color is not None

    def test_get_category_emoji(self):
        """Test category emoji mapping."""
        emojis = {
            'account': '👤',
            'software': '💻',
            'general': '❓',
            'bug': '🐛',
            'feature': '✨',
            'unknown': '📋'
        }
        
        for category, expected_emoji in emojis.items():
            emoji = self.notifier._get_category_emoji(category)
            assert emoji == expected_emoji

    def test_can_send_notification(self):
        """Test notification rate limiting."""
        # First notification should be allowed
        assert self.notifier._can_send_notification('test_type') is True
        
        # Second notification within rate limit should be blocked
        assert self.notifier._can_send_notification('test_type') is False
        
        # Different notification type should be allowed
        assert self.notifier._can_send_notification('different_type') is True

    @pytest.mark.asyncio
    async def test_send_new_ticket_notification(self):
        """Test new ticket notification."""
        ticket_data = {
            'ticket_id': 'TKT-20250101-TEST123',
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'category': 'software',
            'priority': 'high',
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'message': 'This is a test message.'
        }
        
        with patch('discord_alerts.support_notifications.aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 204
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            success = await self.notifier.send_new_ticket_notification(ticket_data)
            
            assert success is True

    @pytest.mark.asyncio
    async def test_send_priority_alert(self):
        """Test priority alert for high priority tickets."""
        ticket_data = {
            'ticket_id': 'TKT-20250101-TEST123',
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Urgent Issue',
            'category': 'software',
            'priority': 'high',
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'message': 'This is an urgent issue.'
        }
        
        with patch('discord_alerts.support_notifications.aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 204
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            success = await self.notifier.send_priority_alert(ticket_data)
            
            assert success is True

    @pytest.mark.asyncio
    async def test_send_status_update_notification(self):
        """Test status update notification."""
        ticket_data = {
            'ticket_id': 'TKT-20250101-TEST123',
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'category': 'software',
            'priority': 'medium',
            'status': 'in_progress',
            'created_at': datetime.now().isoformat(),
            'message': 'This is a test message.'
        }
        
        with patch('discord_alerts.support_notifications.aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 204
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            success = await self.notifier.send_status_update_notification(
                ticket_data, 'open', 'in_progress'
            )
            
            assert success is True

    @pytest.mark.asyncio
    async def test_send_daily_summary(self):
        """Test daily summary notification."""
        tickets_data = [
            {
                'ticket_id': 'TKT-20250101-TEST123',
                'name': 'John Doe',
                'email': 'john@example.com',
                'subject': 'Test Subject',
                'category': 'software',
                'priority': 'high',
                'status': 'open',
                'created_at': datetime.now().isoformat(),
                'message': 'This is a test message.'
            },
            {
                'ticket_id': 'TKT-20250101-TEST456',
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'subject': 'Another Subject',
                'category': 'account',
                'priority': 'medium',
                'status': 'resolved',
                'created_at': datetime.now().isoformat(),
                'message': 'This is another test message.'
            }
        ]
        
        with patch('discord_alerts.support_notifications.aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 204
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            success = await self.notifier.send_daily_summary(tickets_data)
            
            assert success is True

    def test_test_connection(self):
        """Test Discord connection testing."""
        # Test with configuration
        assert self.notifier.test_connection() is True
        
        # Test without configuration
        self.notifier.webhook_url = None
        self.notifier.bot_token = None
        self.notifier.channel_id = None
        
        assert self.notifier.test_connection() is False


class TestIntegration:
    """Integration tests for the support system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tickets_file = Path(self.temp_dir) / "support_tickets.json"
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test configurations
        self._create_test_configs()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_test_configs(self):
        """Create test configuration files."""
        # Email config
        email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "noreply@ms11.com",
            "admin_email": "admin@ms11.com",
            "use_tls": True
        }
        
        with open(self.config_dir / "email_config.json", 'w') as f:
            json.dump(email_config, f)
        
        # Discord config
        discord_config = {
            "support_webhook_url": "https://discord.com/api/webhooks/test",
            "discord_token": "test_token",
            "support_channel_id": 123456789
        }
        
        with open(self.config_dir / "discord_config.json", 'w') as f:
            json.dump(discord_config, f)

    def test_full_ticket_workflow(self):
        """Test the complete ticket workflow."""
        # Test data
        ticket_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'high',
            'subject': 'Critical Software Issue',
            'message': 'The software is not working properly and this is affecting my workflow significantly.'
        }
        
        # Submit ticket
        response = handle_ticket_submission(ticket_data)
        
        assert response.success is True
        assert response.ticket_id is not None
        assert response.category == 'software'
        assert response.priority == 'high'

    def test_multiple_ticket_submissions(self):
        """Test multiple ticket submissions."""
        tickets = [
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'category': 'software',
                'priority': 'high',
                'subject': 'Critical Issue',
                'message': 'This is a critical issue that needs immediate attention.'
            },
            {
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'category': 'account',
                'priority': 'medium',
                'subject': 'Account Access',
                'message': 'I cannot access my account after the recent update.'
            },
            {
                'name': 'Bob Wilson',
                'email': 'bob@example.com',
                'category': 'general',
                'priority': 'low',
                'subject': 'General Question',
                'message': 'I have a general question about the software features.'
            }
        ]
        
        responses = []
        for ticket_data in tickets:
            response = handle_ticket_submission(ticket_data)
            responses.append(response)
        
        # All submissions should be successful
        assert all(r.success for r in responses)
        assert len(set(r.ticket_id for r in responses)) == 3  # Unique ticket IDs

    @pytest.mark.asyncio
    async def test_notification_integration(self):
        """Test notification integration with ticket submission."""
        # Create notifier
        notifier = create_support_notifier()
        
        # Test ticket data
        ticket_data = {
            'ticket_id': 'TKT-20250101-TEST123',
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'category': 'software',
            'priority': 'high',
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'message': 'This is a test message for notification testing.'
        }
        
        # Test new ticket notification
        with patch('discord_alerts.support_notifications.aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 204
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            success = await notifier.send_new_ticket_notification(ticket_data)
            assert success is True

    def test_error_handling(self):
        """Test error handling in the support system."""
        # Test with invalid data
        invalid_data = {
            'name': '',  # Empty name
            'email': 'invalid-email',
            'category': 'invalid_category',
            'priority': 'invalid_priority',
            'subject': '',  # Empty subject
            'message': 'Short'  # Too short
        }
        
        response = handle_ticket_submission(invalid_data)
        
        assert response.success is False
        assert 'Validation failed' in response.error
        assert len(response.message.split(';')) > 1  # Multiple validation errors

    def test_data_persistence(self):
        """Test that ticket data is properly persisted."""
        # Submit a ticket
        ticket_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'category': 'software',
            'priority': 'medium',
            'subject': 'Test Subject',
            'message': 'This is a test message for persistence testing.'
        }
        
        response = handle_ticket_submission(ticket_data)
        assert response.success is True
        
        # Check that the ticket file was created
        tickets_file = Path("data/support_tickets.json")
        assert tickets_file.exists()
        
        # Load and verify the ticket data
        with open(tickets_file, 'r') as f:
            tickets = json.load(f)
        
        assert len(tickets) > 0
        ticket = tickets[0]
        assert ticket['name'] == 'John Doe'
        assert ticket['email'] == 'john@example.com'
        assert ticket['category'] == 'software'
        assert ticket['priority'] == 'medium'


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 