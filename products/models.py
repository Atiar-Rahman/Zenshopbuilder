
from django.db import models, transaction
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from users.models import Company
from core.models import SoftDeleteModel
from django.db import IntegrityError
from django.db.models import Avg,Count
from cloudinary.models import CloudinaryField

class Category(SoftDeleteModel):

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
    image = CloudinaryField('image', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
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
        # run validation only on create/update explicitly safe
        if not kwargs.get("raw", False):
            self.full_clean()

        # slug generation
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class TechStack(SoftDeleteModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Tag(SoftDeleteModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Product(SoftDeleteModel):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

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

    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True, null=True)

    thumbnail = CloudinaryField('image',null=True, blank=True)

    live_preview_url = models.URLField(blank=True, null=True)
    tech_stack = models.ManyToManyField(
        TechStack,
        blank=True,
        related_name='products'
    )
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_active = models.BooleanField(default=True)

    total_sales = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)
    total_wishlist = models.PositiveIntegerField(default=0)

    rating = models.FloatField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')


    class Meta:
        indexes = [
            models.Index(fields=['status', 'is_active']),
        ]
        
    #slug safe
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1

            while True:
                try:
                    self.slug = slug
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    slug = f"{base_slug}-{n}"
                    n += 1
        else:
            super().save(*args, **kwargs)
            
    def update_rating(self):
        data = self.reviews.aggregate(
            avg=Avg('rating'),
            total=Count('id')
        )

        self.rating = data['avg'] or 0
        self.total_reviews = data['total']

        print("checked")

        self.save(update_fields=['rating', 'total_reviews'])

class ProductVersion(SoftDeleteModel):
    REGULAR = 'regular'
    EXTENDED = 'extended'

    LICENSE_TYPES = [
        (REGULAR, 'Regular License'),
        (EXTENDED, 'Extended License'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version = models.CharField(max_length=50)
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPES)
    slug = models.SlugField(max_length=200, unique=True, db_index=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    file = models.FileField(upload_to='products/files/',null=True,blank=True)

    release_date = models.DateField(blank=True, null=True)
    changelog = models.TextField(blank=True, null=True)
    docs_url = models.URLField(blank=True, null=True)

    download_count = models.PositiveIntegerField(default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)


    class Meta:
        unique_together = ('product', 'version', 'license_type')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_featured','version']),
        ]

    # validation discout price
    def clean(self):
        if self.discount_price and self.discount_price > self.price:
            raise ValidationError("Discount price cannot be greater than price")
    # race-condition safe slug
    def save(self, *args, **kwargs):
        # run validation only on create/update explicitly safe
        if not kwargs.get("raw", False):
            self.full_clean()

        # slug generation
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1

            self.slug = slug

        super().save(*args, **kwargs)
    


    def __str__(self):
        return f"{self.product.name} v{self.version} ({self.license_type})"


class ProductVersionImage(SoftDeleteModel):
    product_version = models.ForeignKey(
        ProductVersion,
        on_delete=models.CASCADE,
        related_name='version_images'
    )
    image = CloudinaryField('image',null=True, blank=True)
    caption = models.CharField(max_length=100)

    def __str__(self):
        return self.product_version.version



class ProductImage(SoftDeleteModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = CloudinaryField('image', null=True, blank=True)
    is_main = models.BooleanField(default=False)


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
    


