from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Nombre"}),
            "last_name":  forms.TextInput(attrs={"placeholder": "Apellidos"}),
            "email":      forms.EmailInput(attrs={"placeholder": "correo@ejemplo.com"}),
            "username":   forms.TextInput(attrs={"placeholder": "Nombre de usuario"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if email and User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return email
