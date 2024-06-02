from django.db import models
from .softdelete import SoftDeleteModel


class BaseModel(SoftDeleteModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # To prevent django migrations
