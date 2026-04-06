import uuid
from django.db import models, transaction
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True, blank=True)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )

    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    # cyclic category prevent
    def clean(self):
        parent = self.parent
        while parent:
            if parent == self:
                raise ValidationError("Cyclic category detected")
            parent = parent.parent

    # race-condition safe slug
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            for i in range(10):
                slug = base_slug if i == 0 else f"{base_slug}-{i}"
                if not Category.objects.filter(slug=slug).exists():
                    self.slug = slug
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

from django.core.validators import MinValueValidator
from users.models import Company


class Product(models.Model):

    STATUS = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=180, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )

    short_description = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    thumbnail = models.ImageField(upload_to='products/thumbnails/', null=True, blank=True)

    live_preview_url = models.URLField(blank=True, null=True)
    tech_stack = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    is_active = models.BooleanField(default=True)

    total_sales = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)

    rating = models.FloatField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'is_active']),
        ]

    #slug safe
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            for i in range(10):
                slug = base_slug if i == 0 else f"{base_slug}-{i}"
                if not Product.objects.filter(slug=slug).exists():
                    self.slug = slug
                    break

        super().save(*args, **kwargs)

    # rating auto update
    def update_rating(self):
        reviews = self.reviews.all()
        total = reviews.count()

        if total == 0:
            self.rating = 0
            self.total_reviews = 0
        else:
            self.rating = sum(r.rating for r in reviews) / total
            self.total_reviews = total

        self.save(update_fields=['rating', 'total_reviews'])

    def __str__(self):
        return self.name

class ProductVersion(models.Model):

    LICENSE_TYPES = [
        ('regular', 'Regular License'),
        ('extended', 'Extended License'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version = models.CharField(max_length=50)
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPES)

    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    file = models.FileField(upload_to='products/files/')

    release_date = models.DateField(blank=True, null=True)
    changelog = models.TextField(blank=True, null=True)
    docs_url = models.URLField(blank=True, null=True)

    download_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'version', 'license_type')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
        ]

    def clean(self):
        if self.discount_price and self.discount_price > self.price:
            raise ValidationError("Discount price cannot be greater than price")

    def __str__(self):
        return f"{self.product.name} v{self.version} ({self.license_type})"




class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='products/images/')
    is_main = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_main=True),
                name='unique_main_image_per_product'
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} Image"
    


