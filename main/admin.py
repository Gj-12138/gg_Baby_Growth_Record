from django.contrib import admin

from main.models import Record, BabyParent, Category, Articles, Tag, Photo, Measurement, Vaccine, VaccineRecord, \
    MilestoneType, Event, CheckupRecord, MedicationRecord


# Register your models here.

@admin.register(BabyParent)
class BabyParentAdmin(admin.ModelAdmin):
    pass

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    pass

@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ('name', 'code', 'category', 'dose', 'shot_age_days_start', 'shot_age_days_end')
    # 可搜索的字段
    search_fields = ('name', 'code', 'category')
    # 过滤条件
    list_filter = ('category',)
    # 编辑页字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'category')
        }),
        ('接种信息', {
            'fields': ('dose', 'shot_age_days_start', 'shot_age_days_end', 'interval_days')
        }),
        ('说明信息', {
            'fields': ('description', 'contraindication', 'side_effects')
        }),
    )

@admin.register(VaccineRecord)
class VaccineRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(MilestoneType)
class MilestoneTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass

@admin.register(MedicationRecord)
class MedicationRecordAdmin(admin.ModelAdmin):
    pass

@admin.register(CheckupRecord)
class CheckupRecordAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

@admin.register(Articles)
class ArticleAdmin(admin.ModelAdmin):
    pass


