# Generated by Django 3.2.5 on 2021-07-25 08:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_rename_authenticated data_product_authenticated_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='authenticated_data',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product', to='store.dataafterpurchase'),
        ),
    ]