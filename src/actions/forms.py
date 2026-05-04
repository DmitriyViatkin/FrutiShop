from django import forms
from .models import Declaration

class UploadForm(forms.ModelForm):
    """
    Form for uploading declaration files.

    This form allows users to upload declaration documents. It is linked to the
    Declaration model, which stores the uploaded file and metadata. The form
    includes validation to ensure that only valid files are uploaded.
    """
    class Meta:
        model = Declaration
        fields = ['file']