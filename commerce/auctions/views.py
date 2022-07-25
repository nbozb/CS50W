from operator import contains
from django import forms
from django.forms import ModelForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from flask_login import login_required

from .models import User, Category, Bid, AuctionItem, Comment

class NewListingForm(ModelForm):
    class Meta:
        model = AuctionItem
        fields = ['title', 'description', 'photo', 'category', 'price']
    
class NewBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price']

class NewCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']


def index(request):
    auction_items = AuctionItem.objects.exclude(active=False).all()
    return render(request, "auctions/index.html", {
        "listings": auction_items
    })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def new_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("login")
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            if (form.cleaned_data["price"] < 0):
                return HttpResponse("Price must be greater than 0")
            else:
                f = form.save(commit=False)
                f.owner = request.user
                f.price = form.cleaned_data["price"]
                f.save()
                form.save_m2m()
                return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponse("Error Saving Listing")
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })


def details(request, primkey):
    try:
        listing = AuctionItem.objects.get(pk=primkey)
        listing_id = listing.id
    except:
        return HttpResponse("Not Edjls")

    if (request.method == "POST"):

        # add bid
        if 'bid-button' in request.POST and request.user != listing.owner:
            form = NewBidForm(request.POST)
            if form.is_valid():
                if (Bid.objects.filter(item=listing).count() == 1):
                    if (listing.price > form.cleaned_data["price"]):
                        messages.error(request, "Bid must be greater than/equal to starting price")
                        return HttpResponseRedirect(reverse("details", args=[listing.id]))
                elif (listing.price >= form.cleaned_data["price"]):
                    messages.error(request, "Bid must be greater than current price")
                    return HttpResponseRedirect(reverse("details", args=[listing.id]))
                f = form.save(commit=False)
                f.user = request.user
                f.item = listing
                f.save()
                form.save_m2m()
                listing.price = form.cleaned_data["price"]
                listing.save()
                return HttpResponseRedirect(reverse("details", args=[listing.id]))

        # end bid
        elif 'end-bid-button' in request.POST:
            listing.buyer = Bid.objects.get(item=listing, price=listing.price).user
            listing.active = False
            listing.save(update_fields=['buyer', 'active'])
            return HttpResponseRedirect(reverse("details", args=[listing_id]))

        # add to watchlist
        elif 'add-watch' in request.POST:
            listing.watchlist.add(request.user)
            listing.save()
            messages.success(request, "Item added to watchlist.")
            return HttpResponseRedirect(reverse("details", args=[listing_id]))

        # remove from watchlist
        elif 'remove-watch' in request.POST:
            listing.watchlist.remove(request.user)
            listing.save()
            messages.success(request, "Item removed from watchlist.")
            return HttpResponseRedirect(reverse("details", args=[listing_id]))

        elif 'comment-button' in request.POST:
            form = NewCommentForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.user = request.user
                f.item = listing
                f.save()
                form.save_m2m()
                return HttpResponseRedirect(reverse("details", args=[listing.id]))
            messages.success(request, "Item removed from watchlist.")
            return HttpResponseRedirect(reverse("details", args=[listing_id]))
    
    # already in watchlist?
    in_watchlist = False
    if (listing.owner == request.user and request.user.is_authenticated):
        owner = True
        
    else:
        owner = False
        if request.user.my_watchlist.contains(listing):
            in_watchlist = True

    # item contains bids?
    bids = Bid.objects.filter(item=listing)
    if not bids:
        start_bid = Bid(user=listing.owner, price=listing.price, item=listing)
        start_bid.save()
        bids = Bid.objects.filter(item=listing)

    #comments
    comments = Comment.objects.filter(item=listing)

    return render(request, "auctions/details.html", {
        "listing":listing,
        "owner":owner,
        "bids":bids,
        "comments":comments,
        "in_watchlist":in_watchlist,
        "form":NewBidForm(),
        "addCommentForm":NewCommentForm()
    })


def categories(request):
    item_categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "item_categories":item_categories
    })

def category(request, url_cat):
    cur_cat = Category.objects.get(name=url_cat.title())
    if not cur_cat:
        return HttpResponse("fdshuoij")
    cat_items = AuctionItem.objects.filter(category=cur_cat, active=True)
    return render(request, "auctions/category.html", {
        "cat" : url_cat.title(),
        "listings": cat_items
    })

def my_history(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("login")
    bids = []
    offers = []
    won = []
    didnt_win = []

    my_cur_items = AuctionItem.objects.filter(owner=request.user).exclude(active=False).all()

    my_past_items = AuctionItem.objects.filter(owner=request.user, active=False).all()
    print(my_past_items)

    my_bids_full = request.user.myBids.all()
    for bid_item in my_bids_full:
        if bid_item.item.owner != request.user:
            if bid_item.item.active == True:
                if bid_item.price == bid_item.item.price:
                    bids.append(bid_item)
                else:
                    offers.append(bid_item)
            else:
                if bid_item.item.buyer == request.user:
                    won.append(bid_item)
                else:
                    didnt_win.append(bid_item)

    
    
    return render(request, "auctions/my_history.html", {
        "listings": my_cur_items,
        "past_listings": my_past_items,
        "bids": bids,
        "offers":offers,
        "won":won,
        "didnt_win":didnt_win
    })

def watchlist(request):
    watchlist_items_active = AuctionItem.objects.filter(watchlist=request.user, active=True)
    watchlist_items_closed = AuctionItem.objects.filter(watchlist=request.user, active=False)
    return render(request, "auctions/watchlist.html", {
        "watchlist_items_active":watchlist_items_active,
        "watchlist_items_closed":watchlist_items_closed
    })
