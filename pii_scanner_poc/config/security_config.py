"""
Security Configuration
Centralized security settings and policies
"""

import os
from pathlib import Path
from typing import Dict, Any


class SecurityConfig:
    """Security configuration and policies"""
    
    # Security policies
    POLICIES = {
        'password_requirements': {
            'min_length': 12,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special_chars': True,
            'max_age_days': 90
        },
        'session_management': {
            'session_timeout_minutes': 30,
            'max_concurrent_sessions': 3,
            'secure_cookies': True,
            'https_only': True
        },
        'data_protection': {
            'encryption_algorithm': 'AES-256',
            'key_rotation_days': 30,
            'data_retention_days': 365,
            'backup_encryption': True
        },
        'audit_logging': {
            'log_all_access': True,
            'log_failed_attempts': True,
            'log_data_changes': True,
            'retention_days': 2555  # 7 years
        }
    }
    
    # Security headers for web interfaces
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    @classmethod
    def get_policy(cls, policy_name: str) -> Dict[str, Any]:
        """Get specific security policy"""
        return cls.POLICIES.get(policy_name, {})
    
    @classmethod
    def validate_password(cls, password: str) -> Dict[str, Any]:
        """Validate password against security policy"""
        
        policy = cls.get_policy('password_requirements')
        result = {'valid': True, 'errors': []}
        
        if len(password) < policy['min_length']:
            result['valid'] = False
            result['errors'].append(f"Password must be at least {policy['min_length']} characters")
        
        if policy['require_uppercase'] and not any(c.isupper() for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain uppercase letters")
        
        if policy['require_lowercase'] and not any(c.islower() for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain lowercase letters")
        
        if policy['require_numbers'] and not any(c.isdigit() for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain numbers")
        
        if policy['require_special_chars'] and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            result['valid'] = False
            result['errors'].append("Password must contain special characters")
        
        return result
    
    @classmethod
    def get_secure_headers(cls) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return cls.SECURITY_HEADERS.copy()


# Global security config
security_config = SecurityConfig()
