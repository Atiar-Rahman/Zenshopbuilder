from django.db import models
from django.utils import timezone
import uuid


#custom manager create

class SoftDeleteManager(models.Manager):
    """Return only active(not soft deleted) objects by default"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted = False)
    

class AllObjectsManager(models.Manager):
    """Return all objects including soft deleted"""
    def get_queryset(self):
        return super().get_queryset()

class DeleteObjectsManager(models.Manager):
    """Return all objects including soft deleted"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)



# Abstract Base Model

class SoftDeleteModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True,blank=True)
    deleted_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="deleted_%(class)ss")
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_%(class)ss")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # managers
    objects = AllObjectsManager() # default: all objects
    active_objects = SoftDeleteManager() # not delete
    deleted_objects = DeleteObjectsManager() # only deleted


    class Meta:
        abstract = True

    
    # soft delete methods

    def soft_delete(self, user=None):
        """Mark objects as deleted"""
        self.is_deleted = True
        self.deleted_at = timezone.now()

        if user:
            self.deleted_by = user

        self.save()


    def restore(self):
        """Restore a soft deleted objects"""
        self.is_deleted = False
        self.deleted_at = None  
        self.deleted_by = None
        self.save()