# Copyright (C) 2022-2023 CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from django.http import HttpResponseRedirect
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from allauth.account.adapter import DefaultAccountAdapter

class DefaultAccountAdapterEx(DefaultAccountAdapter):

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)
        superusers_emails = User.objects.filter(is_superuser=True).values_list('email')
        for superuser_email in superusers_emails:
            self.send_mail(email_template, superuser_email, ctx)            
		

    def respond_email_verification_sent(self, request, user):
        return HttpResponseRedirect(settings.ACCOUNT_EMAIL_VERIFICATION_SENT_REDIRECT_URL)
