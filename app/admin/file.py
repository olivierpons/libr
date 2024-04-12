from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class BaseFileAdmin(admin.ModelAdmin):

    def file_link(self, obj):
        if obj is None:
            return '?'
        return format_html(f'<a href="{obj.url()}" target="_blank">'
                           f'{obj.str_clean(str(obj), max_len=50)}'
                           f'</a>')
    file_link.allow_tags = True
    file_link.short_description = _("Link")

    def os_full_filename(self, obj):
        if obj is None:
            return '?'
        return format_html(f'<a href="{obj.url()}" target="_blank">'
                           f'{str(obj.os_full_filename)}'
                           f'</a>')
    os_full_filename.allow_tags = True
    os_full_filename.short_description = _("Full os file name:")

    fields = ('file_link', 'os_full_filename',
              'creator', 'informations', 'original_filename',)
    readonly_fields = ('file_link', 'os_full_filename')
    raw_id_fields = ('creator',)


class ImageFileAdmin(BaseFileAdmin):

    @staticmethod
    def img_preview(obj):
        if obj is None:
            return '?'
        return format_html(
            f'<a href="{obj.url()}" target="_blank">'
            f'<img src="{obj.url_thumbnail()}" '
            f'style="width: auto; max-height:150px" />'
            f'</a>')

    img_preview.allow_tags = True
    img_preview.short_description = _("Preview")

    fields = ('img_preview',) + BaseFileAdmin.fields + ('image_file',)
    readonly_fields = ('file_link', 'os_full_filename', 'img_preview')


class DocumentFileAdmin(BaseFileAdmin):
    fields = BaseFileAdmin.fields + ('actual_file',)
