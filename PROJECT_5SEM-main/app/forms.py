from django import forms
from .models import TimeTable

class TimeTableForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        fields = '__all__'


from .models import student  # adjust to your actual model
import os

class StudentForm(forms.ModelForm):
    class Meta:
        model = student
        fields = [
            'profile_pic', 'first_name', 'last_name', 'email',
            'username', 'password', 'address', 'phone_number',
            'gender', 'course', 'session_year'
        ]

    def clean_first_name(self):
        first = self.cleaned_data.get('first_name', '').strip()
        if not first:
            raise forms.ValidationError('First name is required.')
        if not first[0].isalpha():
            raise forms.ValidationError('First name must start with an alphabet letter.')
        return first

    def clean_last_name(self):
        last = self.cleaned_data.get('last_name', '').strip()
        if not last:
            raise forms.ValidationError('Last name is required.')
        if not last[0].isalpha():
            raise forms.ValidationError('Last name must start with an alphabet letter.')
        return last

    def clean_profile_pic(self):
        pic = self.cleaned_data.get('profile_pic')
        if not pic:
            return pic  # handle required elsewhere if needed
        content_type = pic.content_type
        valid_mime = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if content_type not in valid_mime:
            raise forms.ValidationError('Only JPEG, PNG, GIF, and WEBP image formats are allowed.')
        # Optional: check extension
        ext = os.path.splitext(pic.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            raise forms.ValidationError('Invalid image file extension.')
        # Optional: size limit (e.g., 5MB)
        if pic.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Image file too large (max 5MB).')
        return pic
