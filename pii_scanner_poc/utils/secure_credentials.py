"""
Secure Credential Management System
Handles encryption and secure storage of sensitive credentials
"""

import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Optional


class SecureCredentialManager:
    """Secure credential storage and retrieval system"""
    
    def __init__(self, master_password: str = None):
        self.credentials_file = Path("secure_credentials.enc")
        self.salt_file = Path("credential_salt.key")
        
        # Initialize encryption key
        if master_password:
            self.encryption_key = self._derive_key(master_password.encode())
        else:
            self.encryption_key = self._get_or_create_key()
        
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _derive_key(self, password: bytes) -> bytes:
        """Derive encryption key from master password"""
        
        # Get or create salt
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _get_or_create_key(self) -> bytes:
        """Get existing encryption key or create new one"""
        key_file = Path("encryption.key")
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key
    
    def store_credential(self, service: str, credential_type: str, value: str):
        """Securely store a credential"""
        
        # Load existing credentials
        credentials = self._load_credentials()
        
        # Add new credential
        if service not in credentials:
            credentials[service] = {}
        
        # Encrypt the credential value
        encrypted_value = self.cipher_suite.encrypt(value.encode())
        credentials[service][credential_type] = base64.b64encode(encrypted_value).decode()
        
        # Save back to file
        self._save_credentials(credentials)
    
    def get_credential(self, service: str, credential_type: str) -> Optional[str]:
        """Retrieve and decrypt a credential"""
        
        credentials = self._load_credentials()
        
        if service in credentials and credential_type in credentials[service]:
            encrypted_value = base64.b64decode(credentials[service][credential_type])
            decrypted_value = self.cipher_suite.decrypt(encrypted_value)
            return decrypted_value.decode()
        
        return None
    
    def _load_credentials(self) -> Dict:
        """Load encrypted credentials from file"""
        
        if not self.credentials_file.exists():
            return {}
        
        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        
        except Exception:
            return {}
    
    def _save_credentials(self, credentials: Dict):
        """Encrypt and save credentials to file"""
        
        # Convert to JSON and encrypt
        json_data = json.dumps(credentials, indent=2)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode())
        
        # Save to file with restrictive permissions
        with open(self.credentials_file, 'wb') as f:
            f.write(encrypted_data)
        
        os.chmod(self.credentials_file, 0o600)
    
    def list_services(self) -> list:
        """List all services with stored credentials"""
        credentials = self._load_credentials()
        return list(credentials.keys())
    
    def delete_credential(self, service: str, credential_type: str = None):
        """Delete a specific credential or entire service"""
        
        credentials = self._load_credentials()
        
        if service in credentials:
            if credential_type:
                # Delete specific credential type
                if credential_type in credentials[service]:
                    del credentials[service][credential_type]
                    
                # Remove service if no credentials left
                if not credentials[service]:
                    del credentials[service]
            else:
                # Delete entire service
                del credentials[service]
            
            self._save_credentials(credentials)


# Global credential manager instance
credential_manager = SecureCredentialManager()
