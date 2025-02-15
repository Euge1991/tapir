import datetime

import django.contrib.auth.views as auth_views
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from tapir.accounts.forms import TapirUserForm, PasswordResetForm
from tapir.accounts.models import TapirUser
from tapir.shifts.models import ShiftAttendance, ShiftAttendanceTemplate


class UserDetailView(PermissionRequiredMixin, generic.DetailView):
    model = TapirUser
    context_object_name = "user"
    template_name = "accounts/user_detail.html"
    permission_required = "accounts.manage"

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        max_date = datetime.datetime.now() + datetime.timedelta(days=90)
        user: TapirUser = context_data["user"]
        context_data["shift_attendances"] = ShiftAttendance.objects.filter(
            user=user,
            state=ShiftAttendance.State.PENDING,
            shift__start_time__lt=max_date,
        ).order_by("shift__start_time")
        context_data[
            "shift_template_attendances"
        ] = ShiftAttendanceTemplate.objects.filter(user=user)
        return context_data


class UserMeView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("accounts:user_detail", args=[self.request.user.pk])


class UserUpdateView(PermissionRequiredMixin, generic.UpdateView):
    permission_required = "accounts.manage"
    model = TapirUser
    form_class = TapirUserForm
    template_name = "accounts/user_form.html"


class PasswordResetView(auth_views.PasswordResetView):
    # Form class to allow password reset despite unusable password in the db
    form_class = PasswordResetForm


@require_POST
@csrf_protect
@permission_required("accounts.manage")
def send_user_welcome_email(request, pk):
    u = get_object_or_404(TapirUser, pk=pk)
    u.send_welcome_email()
    messages.info(request, _("Welcome email sent."))

    return redirect(u.get_absolute_url())
