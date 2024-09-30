from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    def formatted_datetime(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')

    formatted_datetime.admin_order_field = 'timestamp'
    formatted_datetime.short_description = 'timestamp Formatted DateTime'
