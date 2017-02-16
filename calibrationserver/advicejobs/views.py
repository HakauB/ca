import os
import threading
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile

from django.views.generic import *

import traceback
# Create your views here.
from advicejobs.forms import UploadFileForm, CreateAdviceJobForm, AdviceJobTable
from advicejobs.models import AdviceJob

from django_tables2 import RequestConfig
import django_tables2 as tables

class AdviceJobOwnerMixin(object):

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

class ListAdviceJobView(LoggedInMixin, ListView):

    template_name = 'contact_list.html'
    model = AdviceJob

    object_list = None

    # Want to only show items belonging to user
    def get_queryset(self):
        return AdviceJob.objects.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        object_list = AdviceJob.objects.filter(owner = self.request.user)
        data = AdviceJob.objects.filter(owner=self.request.user)
        table = AdviceJobTable(AdviceJob.objects.filter(owner = request.user), order_by='-id')
        RequestConfig(request).configure(table)
        context = self.get_context_data(**kwargs)
        context['table'] = table
        return self.render_to_response(context)

class CreateAdviceJobView(LoggedInMixin, AdviceJobOwnerMixin, CreateView):

    model = AdviceJob
    template_name = 'edit_contact.html'
    form_class = CreateAdviceJobForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.filename = obj.cal_file.name;
        obj.save()
        #try:
        print(str(AdviceJob.objects.count()))
        os.rename('jobs/'+str(AdviceJob.objects.count()), 'jobs/'+str(obj.id))
        #except:
        #    pass

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

class UpdateAdviceJobView(LoggedInMixin, AdviceJobOwnerMixin, UpdateView):

    model = AdviceJob
    template_name = 'edit_contact.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('contacts-list')

def AdviceJobDelete(request):
    if request.method == "POST":
        try:
            pks = request.POST.getlist("selection")
            selected_objects = AdviceJob.objects.filter(pk__in=pks)
            # do something with selected_objects
            selected_objects.delete()
            for item in pks:
                try:
                    os.remove('jobs/'+item)
                except OSError:
                    pass
            return HttpResponseRedirect("/")
        except:
            traceback.print_exc()
            return HttpResponseRedirect("/")
            
