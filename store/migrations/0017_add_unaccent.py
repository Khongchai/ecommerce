from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension

class Migration(migrations.Migration):

    dependencies = [
        ("store", "0016_alter_product_image_link")
    ]

    operations = [
        UnaccentExtension()
    ]
