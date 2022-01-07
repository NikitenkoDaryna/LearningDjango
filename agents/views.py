import random
from django.core.mail import send_mail
from django.shortcuts import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from leads.models import Agent
from .forms import AgentModelForm
from .mixins import OrganisorAndLoginRequiredMixin

# Create your views here.
class AgentListView(OrganisorAndLoginRequiredMixin, generic.ListView):
     template_name = "agents/agent_list.html"
    
     def get_queryset(self):
         organisation = self.request.user.userprofile
         return Agent.objects.filter(organisation=organisation)
     
class AgentCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    form_class =AgentModelForm
    
    def get_success_url(self):
        return reverse("agents:agent-list")
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True 
        user.is_organisor = False
        user.set_password(f"{random.randint(0, 1000000)}")
        user.save()
        Agent.objects.create(
            user=user,
            organisation=self.request.user.userprofile,
        )
        send_mail(
            subject="You're invited to be an agent",
            message = "You were added as an agent on DJCRM. Please come login to start working.",
            from_email="admin@test.com",
            recipient_list=[user.email],
        )
        return super(AgentCreateView, self).form_valid(form)
    
class AgentDetailView(OrganisorAndLoginRequiredMixin, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"
    
    def get_queryset(self):
         organisation = self.request.user.userprofile
         return Agent.objects.filter(organisation=organisation)
     
class AgentUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent_update.html"
    form_class =AgentModelForm
    
    def get_form_kwargs(self, **kwargs):
     kwargs = super().get_form_kwargs()
     if hasattr(self, 'object'):
        print(self.object)
        kwargs.update({'instance': self.object})
     return kwargs
    
    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        email_addres = form.cleaned_data.get("email")
        agent = form.save()
        agent.user.username = username
        agent.user.first_name = first_name
        agent.user.last_name = last_name
        agent.user.email = email_addres
        agent.user.save()
        return super(AgentUpdateView, self).form_valid(form)
    
    def get_queryset(self):
         organisation = self.request.user.userprofile
         return Agent.objects.filter(organisation=organisation)
    
    def get_success_url(self):
        return reverse("agents:agent-list")
 
class AgentDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    def get_queryset(self):
         organisation = self.request.user.userprofile
         return Agent.objects.filter(organisation=organisation)
    
    def get_success_url(self):
        return reverse("agents:agent-list")


    