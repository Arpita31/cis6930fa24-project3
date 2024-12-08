from django import forms

class UploadFileForm(forms.Form):
    url = forms.URLField(required=False)
