from .models import Category, Lead

def filter_leads_by_role(user):
    if user.is_organisor:
        queryset = Lead.objects.filter(
            organisation=user.userprofile
        )
    else:
        queryset = Lead.objects.filter(
            organisation=user.agent.organisation
        )
        queryset = queryset.filter(agent__user=user)
    return queryset

def filter_leads_by_category(user):
    if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
    else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
    return queryset 