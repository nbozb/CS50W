from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField("self", blank=True, null=True, symmetrical=False, related_name="following")

    def followInfo(self):
        return {
            "user":self.username,
            "numfollowers":self.followers.count(),
            "numfollowing":self.following.count()
        }

class Post(models.Model):
    poster = models.ForeignKey("User", on_delete=models.PROTECT, related_name="myPosts")
    content = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("User", blank=True, related_name="liked_posts")

    def serialize(self, me):
        meliked = False
        if self.likes.contains(me):
            meliked = True

        return {
            "id":self.id,
            "poster":self.poster.username,
            "content":self.content,
            "timestamp":self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "numlikes":self.likes.count(),
            "likes": [user.username for user in self.likes.all()],
            "meliked": meliked
        }