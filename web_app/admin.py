from django.contrib import admin
from web_app import models

# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_filter = ('role', )
    search_fields = ('email', 'username',)

admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.UserSession)
admin.site.register(models.CostSummarySection)
admin.site.register(models.CostSummary)
admin.site.register(models.ContractSumSection)
admin.site.register(models.ContractSum)