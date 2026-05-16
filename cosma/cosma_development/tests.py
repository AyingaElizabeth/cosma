from django.test import TestCase

# Create your tests here.
from cosma_development.models import ImpactStory
from django.utils.text import slugify

stories = ImpactStory.objects.all()

for story in stories:
    if not story.slug:
        story.slug = slugify(
            f"{story.name}-{story.location}"
        )
        story.save()

        print(f"Created slug: {story.slug}")

print("Done.")