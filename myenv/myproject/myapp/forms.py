from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['identity', 'address', 'income', 'medical_history', 'prev_insurance']
