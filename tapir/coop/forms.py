from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.mail import EmailMessage
from django.forms import TextInput
from django.template.loader import render_to_string

from tapir.coop.models import ShareOwnership, DraftUser, ShareOwner
from tapir.coop.pdfs import get_membership_agreement_pdf
from tapir.utils.forms import DateInput


class CoopShareOwnershipForm(forms.ModelForm):
    class Meta:
        model = ShareOwnership
        fields = (
            "start_date",
            "end_date",
        )

    start_date = forms.DateField(widget=AdminDateWidget())
    end_date = forms.DateField(widget=AdminDateWidget(), required=False)


class DraftUserForm(forms.ModelForm):
    class Meta:
        model = DraftUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "birthdate",
            "street",
            "street_2",
            "postcode",
            "city",
            "attended_welcome_session",
        ]
        widgets = {
            "birthdate": DateInput(),
            "username": TextInput(attrs={"readonly": True}),
        }


class DraftUserRegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

    def save(self, commit=True):
        draft_user: DraftUser = super().save(commit)
        mail = EmailMessage(
            subject="Willkommen bei SuperCoop eG!",
            body=render_to_string(
                "coop/email/membership_confirmation_welcome.txt", {"owner": draft_user}
            ),
            from_email="mitglied@supercoop.de",
            to=[draft_user.email],
            attachments=[
                (
                    "Beteiligungserklärung %s.pdf" % draft_user.get_display_name(),
                    get_membership_agreement_pdf(draft_user).write_pdf(),
                    "application/pdf",
                )
            ],
        )
        mail.send()
        return draft_user

    class Meta:
        model = DraftUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "birthdate",
            "street",
            "street_2",
            "postcode",
            "city",
        ]
        required = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "birthdate",
            "street",
            "postcode",
            "city",
        ]
        widgets = {
            "birthdate": DateInput(),
            "username": TextInput(attrs={"readonly": True}),
            "phone_number": TextInput(attrs={"pattern": "^\\+?\\d{0,13}"}),
        }


class ShareOwnerForm(forms.ModelForm):
    class Meta:
        model = ShareOwner
        fields = [
            "first_name",
            "last_name",
            "email",
            "birthdate",
            "street",
            "street_2",
            "postcode",
            "city",
        ]
        widgets = {
            "birthdate": DateInput(),
        }
