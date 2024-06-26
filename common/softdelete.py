from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.fields.related_descriptors import (
    ReverseManyToOneDescriptor,
    ReverseOneToOneDescriptor,
)


def get_settings():
    default_settings = dict(
        cascade=True,
    )
    return getattr(settings, 'DJANGO_SOFTDELETE_SETTINGS', default_settings)


class SoftDeleteQuerySet(models.query.QuerySet):
    def delete(self, cascade=None):
        cascade = get_settings()['cascade']
        if cascade:  # delete one by one if cascade
            for obj in self.all():
                obj.delete(cascade=cascade)
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


class DeletedQuerySet(models.query.QuerySet):
    def restore(self, *args, **kwargs):
        qs = self.filter(*args, **kwargs)
        qs.update(is_deleted=False, deleted_at=None)


class DeletedManager(models.Manager):
    def get_queryset(self):
        return DeletedQuerySet(self.model, using=self._db).filter(is_deleted=True)


class GlobalManager(models.Manager):
    pass


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeleteManager()
    deleted_objects = DeletedManager()
    all_objects = GlobalManager()
    # global_objects = GlobalManager()

    class Meta:
        abstract = True

    def delete(self, cascade=None, *args, **kwargs):
        cascade = get_settings()['cascade']
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        self.after_delete()
        if cascade:
            self.delete_related_objects()
        # TODO: Call soft_delete_signals

    def restore(self, cascade=None):
        cascade = get_settings()['cascade']
        self.is_deleted = False
        self.deleted_at = None
        self.save()
        self.after_restore()
        if cascade:
            self.restore_related_objects()
        # TODO: Call soft_delete_signals

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def get_related_objects(self):
        attributes = vars(self._meta.model)
        reverse_attributes = [
            a
            for a, b in attributes.items()
            if type(b) in [ReverseManyToOneDescriptor, ReverseOneToOneDescriptor]
        ]
        related_objects = []
        for reverse_attribute in reverse_attributes:
            try:
                related_objects.extend(list(getattr(self, reverse_attribute).all()))
            except:
                pass
        return related_objects

    def delete_related_objects(self):
        for obj in self.get_related_objects():
            obj.delete()

    def restore_related_objects(self):
        for obj in self.get_related_objects():
            obj.restore()

    def after_delete(self):
        pass

    def after_restore(self):
        pass
