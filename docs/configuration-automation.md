# MS11 Configuration Automation System

The MS11 Configuration Automation System provides comprehensive tools for managing, validating, and deploying configuration files across different environments. This system ensures consistency, reliability, and maintainability of your MS11 configurations.

## Overview

The configuration automation system consists of several key components:

1. **Configuration Automation Script** (`scripts/qa/configuration_automation.py`) - Main automation engine
2. **Configuration Validation** (`scripts/qa/validate_configurations.py`) - Validates configuration files
3. **Configuration Deployment** (`scripts/qa/deploy_configurations.py`) - Deploys configurations to environments
4. **Configuration Templates** (`config/templates/`) - Standardized configuration templates

## Features

- **Automated Configuration Management**: Centralized management of all MS11 configuration files
- **Multi-Environment Support**: Development, testing, staging, and production environments
- **Validation & Quality Assurance**: Automated validation of configuration syntax and content
- **Backup & Rollback**: Automatic backup creation and rollback capabilities
- **Template System**: Standardized configuration templates for consistency
- **Deployment Automation**: Automated deployment with validation and notifications

## Quick Start

### 1. Validate All Configurations

```bash
# Basic validation
python scripts/qa/validate_configurations.py

# Validation with auto-fix
python scripts/qa/validate_configurations.py --fix

# Generate validation report
python scripts/qa/validate_configurations.py --output validation_report.txt
```

### 2. Deploy to Environment

```bash
# Deploy to development environment
python scripts/qa/deploy_configurations.py deploy --environment development

# Deploy to production with dry-run first
python scripts/qa/deploy_configurations.py deploy --environment production --dry-run
python scripts/qa/deploy_configurations.py deploy --environment production

# Deploy specific configurations
python scripts/qa/deploy_configurations.py deploy --environment testing --configs combat_profiles.yaml travel_config.yaml
```

### 3. Sync Between Environments

```bash
# Sync from development to testing and staging
python scripts/qa/deploy_configurations.py sync --source-env development --target-envs testing staging

# Force sync (overwrite existing configurations)
python scripts/qa/deploy_configurations.py sync --source-env testing --target-envs staging --force
```

### 4. Rollback Configuration

```bash
# Rollback to most recent backup
python scripts/qa/deploy_configurations.py rollback --environment production

# Rollback to specific backup
python scripts/qa/deploy_configurations.py rollback --environment production --backup-timestamp 20240101_143022
```

## Configuration Templates

### Combat Profile Template

The combat profile template (`config/templates/combat_profile_template.yaml`) provides a standardized structure for combat automation:

```yaml
profile_name: "My Combat Profile"
description: "Custom combat behavior configuration"
version: "1.0.0"

behavior:
  aggression_level: "balanced"  # passive, balanced, aggressive
  target_priority:
    - "healers"
    - "support"
    - "damage_dealers"
  health_thresholds:
    auto_heal: 0.7      # Heal when health drops below 70%
    retreat: 0.3        # Retreat when health drops below 30%
```

### Travel Configuration Template

The travel configuration template (`config/templates/travel_config_template.yaml`) defines automated travel routes and locations:

```yaml
config_name: "My Travel Configuration"
description: "Custom travel automation settings"
version: "1.0.0"

settings:
  default_start_planet: "tatooine"
  default_start_city: "mos_eisley"
  max_travel_attempts: 3
  enable_safe_travel: true

shuttles:
  tatooine:
    - city: "mos_eisley"
      npc: "Shuttle Conductor"
      location:
        x: 3520
        y: -4800
        planet: "tatooine"
```

## Environment Management

### Environment Types

The system supports four environment types:

1. **Development** (`config/development/`)
   - Local development configurations
   - No notifications
   - Automatic backup and validation

2. **Testing** (`config/testing/`)
   - Test environment configurations
   - Notifications enabled
   - Automatic backup and validation

3. **Staging** (`config/staging/`)
   - Pre-production configurations
   - Notifications enabled
   - Automatic backup and validation

4. **Production** (`config/production/`)
   - Live production configurations
   - Notifications enabled
   - Automatic backup and validation
   - Requires approval for deployment

### Environment Configuration

Each environment can be customized in the `ConfigurationDeployer` class:

```python
'environments': {
    'production': {
        'path': 'config/production',
        'backup': True,           # Create backups before deployment
        'validate': True,          # Validate after deployment
        'notify': True,           # Send notifications
        'require_approval': True  # Require manual approval
    }
}
```

## Configuration Validation

### Validation Rules

The system automatically validates:

- **Required Fields**: Ensures essential configuration fields are present
- **Field Types**: Validates data types (strings, numbers, booleans)
- **Value Ranges**: Checks numeric values are within acceptable ranges
- **Health Thresholds**: Ensures health values are between 0.0 and 1.0
- **Coordinates**: Validates coordinate values are reasonable
- **Template Structure**: Verifies template files have proper metadata

### Custom Validation Rules

You can extend validation rules by modifying the `validation_rules` in `ConfigurationValidator`:

```python
self.validation_rules = {
    'required_fields': {
        'custom_config': ['name', 'description', 'version', 'custom_field']
    },
    'field_types': {
        'custom_field': str,
        'custom_number': (int, float)
    },
    'value_ranges': {
        'custom_number': (0, 100)
    }
}
```

## Backup and Recovery

### Automatic Backups

The system automatically creates backups before each deployment:

- **Backup Location**: `backups/config_deployments/`
- **Backup Naming**: `{environment}_{timestamp}/`
- **Backup Contents**: Complete environment configuration snapshot

### Backup Management

```bash
# Generate deployment report
python scripts/qa/deploy_configurations.py report --output deployment_report.txt

# Clean up old backups (keep last 30 days)
python scripts/qa/deploy_configurations.py cleanup --keep-days 30

# Clean up old backups (keep last 7 days)
python scripts/qa/deploy_configurations.py cleanup --keep-days 7
```

## Integration with CI/CD

### GitHub Actions Integration

The configuration automation system can be integrated with your CI/CD pipeline:

```yaml
# .github/workflows/config-validation.yml
name: Configuration Validation
on: [push, pull_request]
jobs:
  validate-configs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Configurations
        run: |
          python scripts/qa/validate_configurations.py --output validation_report.txt
      - name: Upload Validation Report
        uses: actions/upload-artifact@v2
        with:
          name: validation-report
          path: validation_report.txt
```

### Automated Deployment

```yaml
# .github/workflows/config-deployment.yml
name: Configuration Deployment
on:
  push:
    branches: [main]
    paths: ['config/**']
jobs:
  deploy-configs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Staging
        run: |
          python scripts/qa/deploy_configurations.py deploy --environment staging
      - name: Deploy to Production
        run: |
          python scripts/qa/deploy_configurations.py deploy --environment production
        if: github.ref == 'refs/heads/main'
```

## Best Practices

### 1. Configuration Structure

- Use consistent naming conventions
- Include version information in all configurations
- Provide clear descriptions for each configuration
- Use templates for new configurations

### 2. Environment Management

- Test configurations in development first
- Use staging environment for pre-production testing
- Always backup before production deployment
- Monitor deployment notifications

### 3. Validation

- Run validation before each deployment
- Fix warnings to maintain configuration quality
- Use auto-fix for common issues
- Review validation reports regularly

### 4. Backup Strategy

- Keep backups for at least 30 days
- Test rollback procedures regularly
- Document backup and recovery procedures
- Monitor backup storage usage

## Troubleshooting

### Common Issues

1. **Validation Errors**
   - Check required fields are present
   - Verify data types are correct
   - Ensure values are within acceptable ranges

2. **Deployment Failures**
   - Check target environment exists
   - Verify file permissions
   - Review deployment logs

3. **Rollback Issues**
   - Ensure backup exists
   - Check backup integrity
   - Verify target environment state

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python scripts/qa/validate_configurations.py --verbose
python scripts/qa/deploy_configurations.py deploy --environment testing --verbose
```

### Log Files

The system generates detailed logs:

- **Validation Logs**: Configuration validation details
- **Deployment Logs**: Deployment process information
- **Backup Logs**: Backup creation and management
- **Error Logs**: Error details and stack traces

## Advanced Usage

### Custom Configuration Types

Extend the system for custom configuration types:

```python
class CustomConfigurationValidator(ConfigurationValidator):
    def __init__(self, config_root: str = "config"):
        super().__init__(config_root)
        self.validation_rules['custom_config'] = {
            'required_fields': ['custom_field1', 'custom_field2'],
            'field_types': {'custom_field1': str},
            'value_ranges': {'custom_field1': (0, 100)}
        }
```

### Custom Deployment Logic

Extend deployment behavior:

```python
class CustomConfigurationDeployer(ConfigurationDeployer):
    def _custom_deployment_hook(self, environment: str, config_path: Path):
        # Custom logic before/after deployment
        pass
```

### Integration with External Systems

The system can be extended to integrate with:

- **Discord**: Deployment notifications
- **Email**: Status reports
- **Monitoring**: Configuration health checks
- **Databases**: Configuration version tracking

## Support and Maintenance

### Regular Maintenance

- **Daily**: Check deployment notifications
- **Weekly**: Review validation reports
- **Monthly**: Clean up old backups
- **Quarterly**: Review and update templates

### Monitoring

Monitor the following metrics:

- Configuration validation success rate
- Deployment success rate
- Backup creation success rate
- Rollback frequency and success rate

### Updates

Keep the configuration automation system updated:

- Regular dependency updates
- Template improvements
- Validation rule enhancements
- New environment support

## Conclusion

The MS11 Configuration Automation System provides a robust foundation for managing complex configuration requirements. By following the best practices outlined in this document, you can ensure reliable, maintainable, and scalable configuration management for your MS11 project.

For additional support or feature requests, please refer to the project documentation or contact the development team.
