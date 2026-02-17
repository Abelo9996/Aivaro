"""
Encryption utilities for securing sensitive data at rest.
"""
import base64
import hashlib
import secrets
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class CredentialEncryption:
    """
    Handles encryption/decryption of sensitive credentials.
    Uses Fernet (AES-128-CBC) for symmetric encryption.
    """
    
    def __init__(self, secret_key: str):
        """
        Initialize with the application's secret key.
        
        Args:
            secret_key: The application secret key (from settings)
        """
        # Derive a proper encryption key from the secret
        self._fernet = self._create_fernet(secret_key)
    
    def _create_fernet(self, secret_key: str) -> Fernet:
        """Create Fernet instance with derived key."""
        # Use PBKDF2 to derive a proper encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"aivaro_credential_salt",  # Static salt (key rotation would use different salts)
            iterations=100_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.
        
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""
        
        encrypted = self._fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.
        
        Returns:
            Original plaintext string
        
        Raises:
            ValueError: If decryption fails
        """
        if not ciphertext:
            return ""
        
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self._fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt credential: {e}")
            raise ValueError("Failed to decrypt credential")
    
    def encrypt_dict(self, data: dict, keys_to_encrypt: list[str]) -> dict:
        """
        Encrypt specific keys in a dictionary.
        
        Args:
            data: Dictionary with values to encrypt
            keys_to_encrypt: List of keys whose values should be encrypted
        
        Returns:
            Dictionary with encrypted values
        """
        result = data.copy()
        for key in keys_to_encrypt:
            if key in result and result[key]:
                result[key] = self.encrypt(str(result[key]))
        return result
    
    def decrypt_dict(self, data: dict, keys_to_decrypt: list[str]) -> dict:
        """
        Decrypt specific keys in a dictionary.
        
        Args:
            data: Dictionary with encrypted values
            keys_to_decrypt: List of keys whose values should be decrypted
        
        Returns:
            Dictionary with decrypted values
        """
        result = data.copy()
        for key in keys_to_decrypt:
            if key in result and result[key]:
                try:
                    result[key] = self.decrypt(str(result[key]))
                except ValueError:
                    # Keep original value if decryption fails
                    # (might be already decrypted or legacy unencrypted value)
                    pass
        return result


def generate_api_key(prefix: str = "av") -> str:
    """
    Generate a secure API key.
    
    Format: {prefix}_{random_32_chars}
    Example: av_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
    """
    random_part = secrets.token_urlsafe(24)  # 32 characters
    return f"{prefix}_{random_part}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage.
    Uses SHA-256 for fast comparison while still being secure.
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_webhook_secret() -> str:
    """Generate a secure webhook signing secret."""
    return f"whsec_{secrets.token_urlsafe(32)}"


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
    timestamp: Optional[int] = None,
    tolerance: int = 300  # 5 minutes
) -> bool:
    """
    Verify a webhook signature.
    
    Args:
        payload: The raw request body
        signature: The signature from the request header
        secret: The webhook secret
        timestamp: Optional timestamp from header
        tolerance: Max age of signature in seconds
    
    Returns:
        True if signature is valid
    """
    import hmac
    import time
    
    # Check timestamp if provided (replay protection)
    if timestamp:
        current_time = int(time.time())
        if abs(current_time - timestamp) > tolerance:
            logger.warning(f"Webhook signature timestamp too old: {timestamp}")
            return False
    
    # Compute expected signature
    if timestamp:
        signed_payload = f"{timestamp}.{payload.decode()}"
    else:
        signed_payload = payload.decode()
    
    expected_sig = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison
    return hmac.compare_digest(expected_sig, signature)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging/display.
    
    Example: "sk_live_abc123xyz" -> "sk_l****xyz"
    """
    if not data or len(data) <= visible_chars * 2:
        return "****"
    
    return f"{data[:visible_chars]}****{data[-visible_chars:]}"
