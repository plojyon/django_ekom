from django.contrib import admin

from .models import Submission, Professor, Subject, AuthCode, Tag

admin.site.register(Submission)
admin.site.register(Professor)
admin.site.register(Subject)
admin.site.register(AuthCode)
admin.site.register(Tag)
