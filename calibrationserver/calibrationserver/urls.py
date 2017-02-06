"""calibrationserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from registration.forms import RegistrationForm
from contacts.forms import CustomRegistrationForm

from registration.backends.hmac.views import RegistrationView

import contacts.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, name='login',),
    url(r'^logout/$', auth_views.logout, name='logout',),
    url(r'^$', contacts.views.ListContactView.as_view(), name='contacts-list',),
    url(r'^new$', contacts.views.CreateContactView.as_view(), name='contacts-new',),
    url(r'^edit/(?P<pk>\d+)/$', contacts.views.UpdateContactView.as_view(), name='contacts-edit',),
    #url('^register/', CreateView.as_view(name = 'register', template_name='registration/registration_form.html', form_class=UserCreationForm, success_url='/')),
    #url('^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class = CustomRegistrationForm), name='registration_register',),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^captcha/', include('captcha.urls')),
]

urlpatterns += staticfiles_urlpatterns()
