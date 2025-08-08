from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class MediaStorage(S3Boto3Storage):
    location = settings.AWS_STORAGE_LOCATION
    file_overwrite = False  # Optional: prevent overwriting files with same name
    custom_domain = "media.liverealitygames.com"
