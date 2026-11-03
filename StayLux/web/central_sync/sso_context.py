from django.conf import settings
def context_for(user):
    property_id=getattr(settings,"CENTRAL_PROPERTY_ID","")
    if not property_id:raise ValueError("Property binding required.")
    staff=getattr(user,"staff_profile",None)
    if not user.is_superuser and (not staff or not staff.is_active or str(staff.property_id)!=str(property_id)):raise ValueError("Local property membership required.")
    return {"active_property_id":int(property_id)}
