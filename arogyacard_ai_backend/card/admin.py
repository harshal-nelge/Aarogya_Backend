from django.contrib import admin
from .models import ChatHistory

class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ("hid", "display_conversation",)  # Show hid & conversation preview
    search_fields = ("hid",)  # Add search functionality

    def display_conversation(self, obj):
        """Display a short preview of the stored conversation in JSON format"""
        return str(obj.conversation)[:100] + "..." if len(str(obj.conversation)) > 100 else str(obj.conversation)
    
    display_conversation.short_description = "Conversation History"

# Register the model
admin.site.register(ChatHistory, ChatHistoryAdmin)
