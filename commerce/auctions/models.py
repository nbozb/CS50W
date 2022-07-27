from cgi import print_exception
from email.errors import BoundaryError
from multiprocessing.dummy import active_children
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

import datetime

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.name}"

class AuctionItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    photo = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True, related_name="itemsInCat")
    active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits = 8, decimal_places=2)
    posted = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listedItems")
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="boughtItems")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="my_watchlist")

    def __str__(self):
        return f"Title: {self.title}, Category: {self.category}, Owned By: {self.owner}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="myBids")
    price = models.DecimalField(max_digits = 8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(AuctionItem, on_delete=models.PROTECT, related_name="bidsOnListing")

    def __str__(self):
        return f"Bidder: {self.user}, Price: {self.price}, Item: {self.item}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="myComments")
    comment = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(AuctionItem, on_delete=models.PROTECT, related_name="commentsOnListing")
    
    def __str__(self):
        return f"Bidder: {self.user}, Comment: {self.comment}, Item: {self.item}"