from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    # 注册信号：Django启动时加载signals.py
    def ready(self):
        import main.signals  # 导入你的signals.py（路径：app名.signals）