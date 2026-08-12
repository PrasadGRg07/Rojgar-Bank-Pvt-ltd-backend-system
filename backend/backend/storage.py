import os
from django.core.files.storage import FileSystemStorage

def get_raw_storage():
    """
    Returns RawMediaCloudinaryStorage if CLOUDINARY_URL is present,
    otherwise returns the default FileSystemStorage.
    This ensures that raw files like PDFs are not uploaded as images to Cloudinary,
    which would otherwise convert them to images or fail.
    """
    if os.environ.get('CLOUDINARY_URL'):
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        return RawMediaCloudinaryStorage()
    return FileSystemStorage()
