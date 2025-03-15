from django.db import models

class ChatHistory(models.Model):
    hid = models.CharField(max_length=255, unique=True)  # User ID
    conversation = models.JSONField(default=dict)  # Stores query-response history

    def __str__(self):
        return f"Chat History for {self.hid}"