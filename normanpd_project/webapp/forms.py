from django import forms

class UploadFileForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    url = forms.URLField(required=False)
