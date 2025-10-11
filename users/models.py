import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# Create your models here.
class User(AbstractUser):
    """自定义用户模型 - 扩展Django默认用户模型"""
    # 使用UUID作为主键，提高安全性
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 手机号字段，用于用户登录和联系
    phone = models.CharField(verbose_name="手机号", max_length=11, unique=True, blank=True, null=True)
    # 用户头像，按年月分类存储
    avatar = models.ImageField(verbose_name="头像", upload_to="user/avatars", default="default.jpg", blank=True,
                               null=True)
    # 标记用户身份，区分家长和其他类型用户
    is_parent = models.BooleanField(verbose_name="是否是家长", default=True)
    # 标记用户身份，区分VIP和其他类型用户
    is_vip= models.BooleanField(verbose_name="是否是VIP", default=False)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        ordering = ['-id']
        # 数据库索引优化
        indexes = [
            models.Index(fields=['is_vip']),  # 按 VIP 查询
        ]

class Baby(models.Model):
    """宝宝档案 - 存储宝宝的基本信息和健康档案"""
    # 性别选择项
    GENDER_CHOICES = (("M", "男"), ("F", "女"), ("U", "保密"))

    # UUID主键，避免顺序ID泄露信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 宝宝正式姓名
    name = models.CharField(verbose_name='姓名', max_length=100)
    # 宝宝昵称或小名
    nickname = models.CharField(verbose_name="小名", max_length=50, blank=True)
    # 宝宝性别
    gender = models.CharField(verbose_name="性别", max_length=1, choices=GENDER_CHOICES, default="U")
    # 出生日期，用于计算年龄和发育指标
    birthday = models.DateField(verbose_name="出生日期", null=True, blank=True)
    # 出生体重，精确到克
    birth_weight = models.DecimalField(verbose_name="出生体重(kg)", max_digits=5, decimal_places=3, blank=True,
                                       null=True)
    # 出生身高
    birth_height = models.DecimalField(verbose_name="出生身高(cm)", max_digits=5, decimal_places=1, blank=True,
                                       null=True)
    # 孕周信息，用于早产儿发育评估
    gestational_age = models.PositiveSmallIntegerField(verbose_name="出生孕周(周)", blank=True, null=True)
    # 血型信息
    blood_type = models.CharField(verbose_name="血型", max_length=5, blank=True)
    # 过敏史记录，重要健康信息
    allergies = models.TextField(verbose_name="过敏史", blank=True)
    # 宝宝头像，按年月分类存
    avatar = models.ImageField(verbose_name="头像", upload_to="baby/avatars", default="default.jpg", blank=True,
                               null=True)
    # 其他备注信息
    notes = models.TextField(verbose_name="备注信息", null=True, blank=True)
    # 记录创建时间，用于排序和查询
    created_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now, db_index=True)
    # 自动记录最后更新时间
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    # 软删除标记，避免直接删除数据
    is_deleted = models.BooleanField(default=False)

    # 多对多关系，通过BabyParent中间表关联用户
    parents = models.ManyToManyField(User, through="main.BabyParent", related_name="babies")

    class Meta:
        """模型元数据配置"""
        verbose_name = "宝宝档案"
        verbose_name_plural = "宝宝档案"
        # 默认按创建时间倒序排列
        ordering = ["-created_at"]
        # 数据库索引优化
        indexes = [
            models.Index(fields=['birthday']),  # 按生日查询
            models.Index(fields=['created_at', 'is_deleted']),  # 按创建时间和删除状态查询
        ]

    @property
    def age_in_days(self):
        """计算宝宝当前天数年龄"""
        if self.birthday:
            return (timezone.now().date() - self.birthday).days
        return None

    @property
    def age_in_months(self):
        """计算宝宝当前月龄"""
        if self.birthday:
            today = timezone.now().date()
            return (today.year - self.birthday.year) * 12 + (today.month - self.birthday.month)
        return None

    def clean(self):
        """数据验证方法，确保数据的合理性"""
        # 验证出生日期不能在未来
        if self.birthday and self.birthday > timezone.now().date():
            raise ValidationError({"birthday": "出生日期不能在未来"})

        # 验证出生体重合理性（20kg为合理上限）
        if self.birth_weight and self.birth_weight > 20:
            raise ValidationError({"birth_weight": "出生体重数据异常"})

    # 后续开发可以考虑将数据库进行分页，减轻数据库的存储大小的压力
    # def baby_avatar_path(instance, filename):
    #     # 生成唯一路径：avatar/宝宝ID/年月/文件名
    #     return f'avatar/{instance.id}/{timezone.now().strftime("%Y/%m")}/{filename}'
    # avatar = models.ImageField(upload_to=baby_avatar_path, default="avatar/default.jpg")