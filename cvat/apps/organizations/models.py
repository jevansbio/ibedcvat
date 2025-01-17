# Copyright (C) 2021-2022 Intel Corporation
# Copyright (C) 2022-2023 CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from distutils.util import strtobool
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class Organization(models.Model):
    slug = models.SlugField(max_length=16, blank=False, unique=True)
    name = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    contact = models.JSONField(blank=True, default=dict)
    GB_limit = models.IntegerField(default=0)

    owner = models.ForeignKey(get_user_model(), null=True,
        blank=True, on_delete=models.SET_NULL, related_name='+')

    def get_filesize(self):
        filesize = 0
        noproject = self.tasks.filter(project__isnull=True)
        for x in noproject :
            filesize += x.get_filesize()
        for x in self.projects.all():
            filesize += x.get_filesize()
        return filesize

    def check_filesize(self, newfilesize):
        return (self.get_filesize()+newfilesize)>self.GB_limit*1073741824

    def __str__(self):
        return self.slug
    class Meta:
        default_permissions = ()

class Membership(models.Model):
    WORKER = 'worker'
    SUPERVISOR = 'supervisor'
    MAINTAINER = 'maintainer'
    OWNER = 'owner'

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
        null=True, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
        related_name='members')
    is_active = models.BooleanField(default=False)
    joined_date = models.DateTimeField(null=True)
    role = models.CharField(max_length=16, choices=[
        (WORKER, 'Worker'),
        (SUPERVISOR, 'Supervisor'),
        (MAINTAINER, 'Maintainer'),
        (OWNER, 'Owner'),
    ])

    class Meta:
        default_permissions = ()
        unique_together = ('user', 'organization')


# Inspried by https://github.com/bee-keeper/django-invitations
class Invitation(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)

    @property
    def organization_id(self):
        return self.membership.organization_id

    def send(self):
        if not strtobool(settings.ORG_INVITATION_CONFIRM):
            self.accept(self.created_date)

        # TODO: use email backend to send invitations as well

    def accept(self, date=None):
        if not self.membership.is_active:
            self.membership.is_active = True
            if date is None:
                self.membership.joined_date = timezone.now()
            else:
                self.membership.joined_date = date
            self.membership.save()

    class Meta:
        default_permissions = ()
