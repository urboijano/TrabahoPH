"""File validators for the jobs app"""

import logging
import mimetypes
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.utils.deconstruct import deconstructible

logger = logging.getLogger(__name__)


@deconstructible
class FileValidator:
    """Validate file type, size and other properties"""
    
    def __init__(self, allowed_extensions=None, allowed_mimetypes=None, max_size=None):
        """
        Initialize validator
        
        Args:
            allowed_extensions: List of allowed file extensions (e.g., ['pdf', 'jpg', 'png'])
            allowed_mimetypes: List of allowed MIME types (e.g., ['application/pdf', 'image/jpeg'])
            max_size: Maximum file size in bytes
        """
        self.allowed_extensions = allowed_extensions or []
        self.allowed_mimetypes = allowed_mimetypes or []
        self.max_size = max_size
    
    def __call__(self, file_obj):
        """Validate the file"""
        if not file_obj:
            raise ValidationError("No file provided")
        
        # Check file size
        if self.max_size and file_obj.size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            raise ValidationError(f"File size exceeds maximum allowed size of {max_mb:.1f}MB")
        
        # Get file extension
        file_name = file_obj.name.lower()
        file_ext = file_name.split('.')[-1] if '.' in file_name else ''
        
        # Check extension
        if self.allowed_extensions and file_ext not in self.allowed_extensions:
            extensions_str = ', '.join(self.allowed_extensions)
            raise ValidationError(f"File extension '.{file_ext}' is not allowed. Allowed types: {extensions_str}")
        
        # Check MIME type
        if self.allowed_mimetypes:
            mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
            if mime_type not in self.allowed_mimetypes:
                raise ValidationError(f"File type '{mime_type}' is not allowed")
    
    def __eq__(self, other):
        return (isinstance(other, FileValidator) and
                self.allowed_extensions == other.allowed_extensions and
                self.allowed_mimetypes == other.allowed_mimetypes and
                self.max_size == other.max_size)


class DTIPermitValidator:
    """Validate DTI permit files: PDF, JPG, PNG only, max 5MB"""
    
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
    ALLOWED_MIMETYPES = [
        'application/pdf',
        'image/jpeg',
        'image/png',
    ]
    
    @classmethod
    def validate(cls, file_obj):
        """Validate a DTI permit file
        
        Args:
            file_obj: The file object to validate
            
        Raises:
            ValidationError: If the file doesn't meet requirements
        """
        if not file_obj:
            raise ValidationError("DTI permit file is required")
        
        # Check file size
        if file_obj.size > cls.MAX_SIZE:
            raise ValidationError(f"DTI permit file size exceeds maximum of 5MB. Current size: {file_obj.size / (1024*1024):.1f}MB")
        
        # Get file extension
        file_name = file_obj.name.lower()
        file_ext = file_name.split('.')[-1] if '.' in file_name else ''
        
        # Check extension
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError(f"DTI permit must be PDF, JPG, or PNG. Received: .{file_ext}")
        
        # Verify MIME type
        mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        if mime_type not in cls.ALLOWED_MIMETYPES:
            logger.warning(f"Suspicious MIME type for DTI permit: {mime_type}")
            raise ValidationError(f"Invalid file type: {mime_type}")
        
        logger.info(f"DTI permit validated: {file_name} ({file_obj.size} bytes)")


class ProfileImageValidator:
    """Validate profile image files: JPG, PNG only, max 2MB"""
    
    MAX_SIZE = 2 * 1024 * 1024  # 2MB
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
    ALLOWED_MIMETYPES = [
        'image/jpeg',
        'image/png',
    ]
    
    @classmethod
    def validate(cls, file_obj):
        """Validate a profile image file
        
        Args:
            file_obj: The file object to validate
            
        Raises:
            ValidationError: If the file doesn't meet requirements
        """
        if not file_obj:
            raise ValidationError("Profile image file is required")
        
        # Check file size
        if file_obj.size > cls.MAX_SIZE:
            raise ValidationError(f"Profile image file size exceeds maximum of 2MB. Current size: {file_obj.size / (1024*1024):.1f}MB")
        
        # Get file extension
        file_name = file_obj.name.lower()
        file_ext = file_name.split('.')[-1] if '.' in file_name else ''
        
        # Check extension
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError(f"Profile image must be JPG or PNG. Received: .{file_ext}")
        
        # Verify MIME type
        mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        if mime_type not in cls.ALLOWED_MIMETYPES:
            logger.warning(f"Suspicious MIME type for profile image: {mime_type}")
            raise ValidationError(f"Invalid file type: {mime_type}")
        
        logger.info(f"Profile image validated: {file_name} ({file_obj.size} bytes)")


def validate_dti_permit(file_obj):
    """Standalone function to validate DTI permit"""
    DTIPermitValidator.validate(file_obj)


def validate_profile_image(file_obj):
    """Standalone function to validate profile image"""
    ProfileImageValidator.validate(file_obj)
