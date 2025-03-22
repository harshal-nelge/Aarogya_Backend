from django.db import models

class ChatHistory(models.Model):
    hid = models.CharField(max_length=255, unique=True)
    conversation = models.JSONField(default=dict)  # Stores chat history

class DiagnosedDisease(models.Model):
    hid = models.ForeignKey(ChatHistory, on_delete=models.CASCADE, related_name="diseases")
    disease = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # To track when the disease was diagnosed
