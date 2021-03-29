from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import generic

from tapir.accounts.models import TapirUser
from tapir.shifts.models import ShiftAttendance


class UserDetailView(generic.DetailView):
    model = TapirUser
    context_object_name = "user"
    template_name = "accounts/user_detail.html"

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data["shift_attendances"] = ShiftAttendance.objects.filter(user=context_data["user"], state=ShiftAttendance.State.PENDING)
        return context_data


class UserMeView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("accounts:user_detail", args=[self.request.user.pk])