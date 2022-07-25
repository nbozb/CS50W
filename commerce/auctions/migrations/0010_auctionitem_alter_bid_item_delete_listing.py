# Generated by Django 4.0.5 on 2022-07-15 02:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_bid_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuctionItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=2000)),
                ('photo', models.URLField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('starting_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='boughtItems', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='itemsInCat', to='auctions.category')),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='listedItems', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='bid',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bidsOnListing', to='auctions.auctionitem'),
        ),
        migrations.DeleteModel(
            name='Listing',
        ),
    ]
