import os
import threading
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile

from django.views.generic import TemplateView

# Create your views here.
from contacts.forms import UploadFileForm, CreateContactForm, ContactTable
from contacts.models import Contact

from django_tables2 import RequestConfig
import django_tables2 as tables

class ContactOwnerMixin(object):

    # Check user is owner of items requested
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg, None)
        queryset = queryset.filter(
            pk=pk,
            owner=self.request.user,
        )

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise PermissionDenied

        return obj

# Primarily used to check user is logged in
class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)

class ListContactView(LoggedInMixin, ListView):

    template_name = 'contact_list.html'
    model = Contact

    object_list = None

    # Want to only show items belonging to user
    def get_queryset(self):
        return Contact.objects.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        object_list = Contact.objects.filter(owner = self.request.user)
        data = Contact.objects.filter(owner=self.request.user)
        table = ContactTable(Contact.objects.filter(owner = request.user), order_by='-id')
        RequestConfig(request).configure(table)
        context = self.get_context_data(**kwargs)
        context['table'] = table
        return self.render_to_response(context)

class CreateContactView(LoggedInMixin, ContactOwnerMixin, CreateView):

    model = Contact
    template_name = 'edit_contact.html'
    form_class = CreateContactForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.filename = obj.cal_file.name;
        obj.save()

        # Handles email and configuartion in background as the email check seems to slow it
        def email_worker():
            msg = EmailMessage('Submission Received', 'You have submitted a file ' + obj.cal_file.name + '... wait a while', to=[str(obj.owner.email)])
            try:
                msg.send()
            except:
                pass
        threading.Thread(target = email_worker).start()
        return HttpResponseRedirect(self.get_success_url())

    # Redirects user to the contacts list on success - As I learnt dont add stuff here
    def get_success_url(self):
        return reverse('contacts-list')

class UpdateContactView(LoggedInMixin, ContactOwnerMixin, UpdateView):

    model = Contact
    template_name = 'edit_contact.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('contacts-list')
