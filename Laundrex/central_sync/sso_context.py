from django.conf import settings
from apps.accounts.models import StaffProfile
from apps.accounts.utils import user_can_view_all_branches
def context_for(user):
    profile=StaffProfile.objects.select_related("branch").filter(user=user).first()
    branch=profile.branch.code if profile and profile.branch else ""
    if not branch and user_can_view_all_branches(user):branch=getattr(settings,"CENTRAL_BRANCH_CODE","")
    if not branch:raise ValueError("An explicit local branch is required.")
    return {"active_branch":branch,"django_language":profile.preferred_language if profile else "en"}
