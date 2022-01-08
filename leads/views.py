from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from agents.mixins import OrganisorAndLoginRequiredMixin
from leads.forms import LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm
from .models import Lead
from django.views import generic
from .helpers import filter_leads_by_category, filter_leads_by_role

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm
    
    def get_success_url(self):
        return reverse("login")

class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    
    def get_queryset(self):
        user = self.request.user
        queryset = filter_leads_by_role(user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile, 
                agent__isnull=True
            )
            context.update({
                "unassigned_leads": queryset
            })
        return context

class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"
    
    def get_queryset(self):
        user = self.request.user
        queryset = filter_leads_by_role(user)
        return queryset
    
class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm
    
    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        return super(LeadCreateView, self).form_valid(form)
    
class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
           return Lead.objects.filter(organisation=user.userprofile)
        
    def get_success_url(self):
        return reverse("leads:lead-list")
    
class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
           return Lead.objects.filter(organisation=user.userprofile)
       
    def get_success_url(self):
        return reverse("leads:lead-list")
    
class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs
        
    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)

class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"
    
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        queryset = filter_leads_by_role(user)
        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count(),
            "assigned_leads": queryset.filter(category__isnull=False)
        })
        return context
    
    def get_queryset(self):
        user = self.request.user
        queryset = filter_leads_by_category(user)
        return queryset
 
class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        queryset = filter_leads_by_role(user)
        context.update({
            "leads": queryset.filter(category__isnull=False)
        })
        return context
    
    def get_queryset(self):
        user = self.request.user
        queryset = filter_leads_by_category(user)
        return queryset
            
class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm
    
    def get_queryset(self):
        user = self.request.user
        queryset = filter_leads_by_role(user)
        return queryset
            
    def get_success_url(self):
     return reverse("leads:lead-detail", kwargs={"pk":self.get_object().id})