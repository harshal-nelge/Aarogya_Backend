from django.contrib import admin
from .models import ChatHistory, DiagnosedDisease


class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ("hid", "short_conversation")  # Show hid & conversation preview
    search_fields = ("hid",)  # Add search functionality

    def short_conversation(self, obj):
        """Display a short preview of the stored conversation in JSON format"""
        return str(obj.conversation)[:100] + "..." if len(str(obj.conversation)) > 100 else str(obj.conversation)
    
    short_conversation.short_description = "Conversation Preview"


class DiagnosedDiseaseAdmin(admin.ModelAdmin):
    list_display = ("hid", "disease", "created_at")  # Show hid, disease, and date
    search_fields = ("hid__hid", "disease")  # Allow search by hid or disease
    list_filter = ("created_at",)  # Filter by date

    def hid(self, obj):
        """Display the `hid` from the related `ChatHistory` model."""
        return obj.hid.hid

    hid.short_description = "Chat History ID"


# Register models with the admin site
admin.site.register(ChatHistory, ChatHistoryAdmin)
admin.site.register(DiagnosedDisease, DiagnosedDiseaseAdmin)
