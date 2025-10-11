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
    pass

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

