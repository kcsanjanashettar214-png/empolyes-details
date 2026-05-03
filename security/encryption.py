# Layer 6: Encryption - Encrypt responses
from cryptography.fernet import Fernet
import base64
import hashlib

class EncryptionManager:
    """Layer 6: Encryption - Encrypt/Decrypt sensitive data"""
    
    def __init__(self, key: str = None):
        """Initialize with encryption key"""
        if key is None:
            key = "your-encryption-key-32-chars-long"
        
        # Ensure key is 32 bytes for Fernet
        if len(key) < 32:
            key = key.ljust(32, '0')[:32]
        
        # Generate Fernet key from string
        key_bytes = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
        self.cipher = Fernet(key_bytes)
    
    def encrypt(self, data: str) -> str:
        """Encrypt data"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            return f"Encryption error: {str(e)}"
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            return f"Decryption error: {str(e)}"

# Create global encryption manager
encryption_manager = EncryptionManager()
