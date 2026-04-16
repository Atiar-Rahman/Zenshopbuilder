from django.utils.text import slugify
import re

def generate_unique_slug(instance, field_name="name"):
    model = instance.__class__

    value = getattr(instance, field_name)
    base_slug = slugify(value)

    slugs = model.objects.filter(
        slug__startswith=base_slug
    ).values_list('slug', flat=True)

    if base_slug not in slugs:
        return base_slug

    pattern = re.compile(rf'^{base_slug}-(\d+)$')

    numbers = [
        int(m.group(1))
        for s in slugs
        if (m := pattern.match(s))
    ]

    return f"{base_slug}-{max(numbers, default=0) + 1}"