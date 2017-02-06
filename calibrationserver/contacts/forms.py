from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import EmailMessage
from django.forms import ModelForm

from contacts.models import Contact

from registration.forms import RegistrationForm
from captcha.fields import CaptchaField

import django_tables2 as tables

fs = FileSystemStorage(location='/jobs/processes')
configuration_choices = (
    ('foss', 'FOSS'),
    ('multispec', 'Multispec'),
    ('csv', 'CSV'),
)

class UploadFileForm(forms.Form):
    model = Contact
    title = forms.CharField(max_length=50)
    file = forms.FileField()

class CreateContactForm(forms.ModelForm):

    cal_file = forms.FileField(required = True)
    calibration = forms.CharField(max_length = 255, required = True)
    #comments = forms.CharField(max_length = 255, initial="")
    configuration = forms.ChoiceField(choices=configuration_choices)

    # Adds a HTML class tag
    cal_file.widget.attrs.update({'class' : 'file_field'})
    calibration.widget.attrs.update({'class' : 'cal_field'})
    #comments.widget.attrs.update({'class' : 'comment_field'})

    class Meta:
        model = Contact
        fields = ('cal_file', 'calibration', 'configuration')

class CustomRegistrationForm(RegistrationForm):
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ContactTable(tables.Table):

    class Meta:
        model = Contact
        exclude = ('cal_file', 'owner')
        sequence = ('processed', 'id', 'timestamp', 'filename', 'calibration', 'comments')
        attrs = {"class": "paleblue"
                ,"style": "width: 100%;"}
