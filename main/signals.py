# signals.py
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from PIL import Image
from .models import Photo


@receiver(post_save, sender=Photo)
def generate_thumbnail(sender, instance, created, **kwargs):
    """照片上传后自动生成缩略图（仅处理图片类型，视频无需缩略图）"""
    if instance.media_type == "photo" and not instance.thumbnail and instance.file:
        original_path = instance.file.path
        thumb_dir = os.path.join(os.path.dirname(original_path), "thumbs")
        os.makedirs(thumb_dir, exist_ok=True)

        original_filename = os.path.basename(original_path)
        thumb_filename = os.path.splitext(original_filename)[0] + "_thumb.jpg"
        thumb_path = os.path.join(thumb_dir, thumb_filename)

        try:
            with Image.open(original_path) as img:
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumb_path, "JPEG", quality=80, optimize=True)

            relative_thumb_path = os.path.relpath(thumb_path, settings.MEDIA_ROOT)
            instance.thumbnail.name = relative_thumb_path
            instance.save(update_fields=["thumbnail"])

        except Exception as e:
            print(f"生成缩略图失败（照片ID：{instance.id}）：{str(e)}")