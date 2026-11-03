from django.conf import settings
def context_for(user):
    return {settings.ACTIVE_BRANCH_SESSION_KEY:user.default_branch_id,"ui_lang":user.preferred_language or "en"}
