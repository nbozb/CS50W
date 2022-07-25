from django.contrib import admin
from .models import User, AuctionItem, Bid, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "owner", "price")

# Register your models here.
admin.site.register(User)
admin.site.register(AuctionItem, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Category, CategoryAdmin)