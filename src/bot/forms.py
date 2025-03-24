from django import forms
from easy_select2 import select2_modelform

from bot.models import Subscription, Category, Message, MessageStatus


class ActivateSubscriptionForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    subscription = forms.ModelChoiceField(queryset=Subscription.objects.all(), label="Подписка", required=True)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Категория", required=True)


class MassMessageForm(forms.ModelForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    class Meta:
        model = Message
        fields = ("name", "text", "loaded_file", "loaded_file_id", "message_type", "parse_mode")


StatusMessageForm = select2_modelform(MessageStatus, attrs={'width': '250px'})

MessageForm = select2_modelform(Message, attrs={'width': '250px'})
