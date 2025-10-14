import uuid

from ckeditor.fields import RichTextField
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

# from django.contrib.auth import get_user_model
from users.models import Baby, User


# User = get_user_model()

# Create your models here.


class BabyParent(models.Model):
    """家长与宝宝关系表 - 管理宝宝与家长之间的多对多关系，支持多种角色"""
    # 家庭成员角色定义
    ROLE_CHOICES = (
        ("father", "爸爸"),
        ("mother", "妈妈"),
        ("grandpa", "爷爷"),
        ("grandma", "奶奶"),
        ("paternal_aunt", "外婆"),
        ("maternal_aunt", "外公"),
        ("other", "其他")
    )
    # UUID主键，提高安全性
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 家长角色，定义与宝宝的关系
    role = models.CharField(verbose_name="身份", max_length=20, choices=ROLE_CHOICES, default="other")
    # 标记是否为主要监护人，用于权限控制
    is_primary = models.BooleanField(verbose_name="是否主要监护人", default=False)
    # 关系建立时间
    created_at = models.DateTimeField(verbose_name="绑定时间", default=timezone.now)
    # 最后更新时间
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    # 外键关联宝宝
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name="parent_links")
    # 外键关联用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="baby_links")

    class Meta:
        # 唯一约束，避免重复关系
        unique_together = [("baby", "user")]
        verbose_name = "家长关系"
        verbose_name_plural = "家长关系"

    def __str__(self):
        return f"{self.get_role_display()} - {self.baby} - {self.user.username}"


class Record(models.Model):
    """成长记录 - 记录宝宝的日常成长信息，支持文字和语音两种形式"""
    # 记录分类，便于分类查看
    RECORD_CATEGORY = (
        ("daily", "日常记录"),
        ("health", "健康记录"),
        ("development", "发育记录"),
        ("feeding", "喂养记录"),
        ("sleep", "睡眠记录"),
        ("other", "其他")
    )
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 关联宝宝
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name="records")
    # 记录创建者
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 记录标题，可选
    title = models.CharField(verbose_name="标题", max_length=100, blank=True)
    # 记录主要内容
    content = models.TextField("内容")
    # 记录分类
    category = models.CharField(verbose_name="分类", max_length=20, choices=RECORD_CATEGORY, default="daily")
    # 记录类型：文字或语音
    record_type = models.CharField(verbose_name="类型", max_length=20,
                                   choices=(("text", "文字"), ("voice", "语音")),
                                   default="text")
    # 语音文件存储路径
    voice = models.FileField(verbose_name="语音文件", upload_to="voice/%Y/%m", blank=True, null=True)
    # 语音时长，单位为秒
    voice_duration = models.PositiveIntegerField(verbose_name="语音时长(秒)", default=0)
    # 记录发生的日期
    record_date = models.DateField(verbose_name="记录日期", default=timezone.now, db_index=True)
    # 记录创建时间
    created_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    # 最后更新时间
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        # 默认按记录日期和创建时间倒序排列
        ordering = ["-record_date", "-created_at"]
        verbose_name = "成长记录"
        verbose_name_plural = "成长记录"
        # 数据库索引优化
        indexes = [
            models.Index(fields=['baby', 'record_date']),  # 按宝宝和日期查询
            models.Index(fields=['category', 'record_date']),  # 按分类和日期查询
        ]

    def __str__(self):
        return f"{self.baby}的{self.get_category_display()}: {self.title or self.content[:20]}"


class Photo(models.Model):
    """照片/视频 - 管理宝宝的媒体文件，支持照片和视频两种类型"""
    # 媒体类型定义
    MEDIA_TYPE = (
        ("photo", "照片"),
        ("video", "视频")
    )
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 关联宝宝
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name="photos")
    # 媒体文件存储路径
    file = models.FileField(verbose_name="文件", upload_to="media/%Y/%m")
    # 媒体类型：照片或视频
    media_type = models.CharField(verbose_name="媒体类型", max_length=10, choices=MEDIA_TYPE, default="photo")
    # 缩略图路径，用于快速预览
    thumbnail = models.ImageField(verbose_name="缩略图", upload_to="media/thumb/%Y/%m", blank=True, null=True)
    # 媒体描述
    description = models.CharField(verbose_name="描述", max_length=200, blank=True)
    # 拍摄地点
    location = models.CharField(verbose_name="拍摄地点", max_length=200, blank=True)
    # 拍摄时间
    shot_at = models.DateTimeField(verbose_name="拍摄时间", blank=True, null=True)
    # 上传者
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="uploaded_media")
    # 上传时间
    uploaded_at = models.DateTimeField(verbose_name="上传时间", default=timezone.now)

    class Meta:
        # 默认按拍摄时间和上传时间倒序排列
        ordering = ["-shot_at", "-uploaded_at"]
        verbose_name = "照片/视频"
        verbose_name_plural = "照片/视频"

    def __str__(self):
        return f"{self.get_media_type_display()}: {self.description or '未命名'}"


class Measurement(models.Model):
    """身高体重头围记录 - 记录宝宝的身体发育指标"""
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 关联宝宝
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name="measurements")
    # 身高，单位厘米，必须为正数
    height = models.DecimalField(verbose_name="身高(cm)", max_digits=5, decimal_places=1,
                                 validators=[MinValueValidator(0)])
    # 体重，单位千克，必须为正数
    weight = models.DecimalField(verbose_name="体重(kg)", max_digits=5, decimal_places=2,
                                 validators=[MinValueValidator(0)])
    # 头围，单位厘米，可选
    head_circumference = models.DecimalField(verbose_name="头围(cm)", max_digits=5, decimal_places=1,
                                             blank=True, null=True)
    # 胸围，单位厘米，可选
    chest_circumference = models.DecimalField(verbose_name="胸围(cm)", max_digits=5, decimal_places=1,
                                              blank=True, null=True)
    # 测量日期
    measure_date = models.DateField(verbose_name="测量日期", default=timezone.now, db_index=True)
    # 测量者
    measured_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # 测量备注
    notes = models.CharField(verbose_name="备注", max_length=200, blank=True)
    # 记录创建时间
    created_at = models.DateTimeField(verbose_name="录入时间", default=timezone.now)
    # 最后更新时间
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        # 默认按测量日期倒序排列
        ordering = ["-measure_date"]
        # 唯一约束，同一天只保留最新一次测量记录
        unique_together = [("baby", "measure_date")]
        verbose_name = "身高体重记录"
        verbose_name_plural = "身高体重记录"

    def __str__(self):
        return f"{self.baby}的测量记录: {self.measure_date}"


class Vaccine(models.Model):
    """疫苗字典 - 存储国家免疫规划的疫苗标准信息"""
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 疫苗名称
    name = models.CharField(verbose_name="疫苗名称", max_length=100)
    # 疫苗编码，唯一标识
    code = models.CharField(verbose_name="编码", max_length=30, unique=True)
    # 疫苗类别：一类疫苗、二类疫苗等
    category = models.CharField(verbose_name="疫苗类别", max_length=50, blank=True,
                                help_text="如:一类疫苗、二类疫苗")
    # 推荐接种起始日龄
    shot_age_days_start = models.PositiveSmallIntegerField(verbose_name="推荐接种起始日龄", default=0)
    # 推荐接种截止日龄
    shot_age_days_end = models.PositiveSmallIntegerField(verbose_name="推荐接种截止日龄", blank=True, null=True)
    # 接种剂次
    dose = models.PositiveSmallIntegerField(verbose_name="剂次", default=1)
    # 与上一剂的间隔天数
    interval_days = models.PositiveSmallIntegerField(verbose_name="间隔天数", default=0,
                                                     help_text="与上一剂的间隔天数")
    # 疫苗说明
    description = models.TextField(verbose_name="说明", blank=True)
    # 禁忌症
    contraindication = models.TextField(verbose_name="禁忌症", blank=True)
    # 不良反应
    side_effects = models.TextField(verbose_name="不良反应", blank=True)

    def __str__(self):
        return f"{self.name}({self.dose}剂)"

    class Meta:
        # 默认按接种起始日龄、名称和剂次排序
        ordering = ["shot_age_days_start", "name", "dose"]
        verbose_name = "疫苗"
        verbose_name_plural = "疫苗"
        # 唯一约束，避免重复疫苗剂次
        unique_together = [("name", "dose")]


class VaccineRecord(models.Model):
    """宝宝实际接种记录 - 记录宝宝的实际疫苗接种情况"""
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 关联宝宝
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name="vaccine_records")
    # 关联疫苗字典
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    # 实际接种日期
    shot_date = models.DateField("接种日期")
    # 疫苗批号
    batch_number = models.CharField(verbose_name="疫苗批号", max_length=50, blank=True)
    # 接种医院或机构
    hospital = models.CharField(verbose_name="接种点", max_length=150, blank=True)
    # 接种医生
    doctor = models.CharField(verbose_name="接种医生", max_length=50, blank=True)
    # 接种后不良反应
    reaction = models.TextField(verbose_name="不良反应", blank=True)
    # 下次接种日期
    next_shot_date = models.DateField(verbose_name="下次接种日期", blank=True, null=True)
    # 记录创建者
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # 记录创建时间
    created_at = models.DateTimeField(verbose_name="录入时间", default=timezone.now)
    # 最后更新时间
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        # 默认按接种日期正序排列
        ordering = ["shot_date"]
        verbose_name = "接种记录"
        verbose_name_plural = "接种记录"

    def __str__(self):
        return f"{self.baby}接种{self.vaccine.name}: {self.shot_date}"


class MilestoneType(models.Model):
    """里程碑事件类型 - 定义宝宝发育里程碑的分类"""
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 里程碑类型名称
    name = models.CharField(verbose_name="类型名称", max_length=50, unique=True)
    # 类型描述
    description = models.TextField(verbose_name="描述", blank=True)

    class Meta:
        verbose_name = "里程碑类型"
        verbose_name_plural = "里程碑类型"
        # 默认按名称排序
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(models.Model):
    """里程碑事件 - 记录宝宝的重要发育里程碑，如第一次翻身、第一次走路等"""
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 关联宝宝
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name="events")
    # 关联里程碑类型
    type = models.ForeignKey(MilestoneType, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="events")
    # 事件标题
    title = models.CharField(verbose_name="事件标题", max_length=100)
    # 事件发生日期
    happen_date = models.DateField(verbose_name="发生日期", db_index=True)
    # 事件详细描述
    description = models.TextField(verbose_name="详细描述", blank=True)
    # 关联的照片，多对多关系
    photos = models.ManyToManyField(Photo, blank=True, related_name="events")
    # 事件记录者
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # 记录创建时间
    created_at = models.DateTimeField(verbose_name="记录时间", default=timezone.now)
    # 最后更新时间
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        # 默认按发生日期倒序排列
        ordering = ["-happen_date"]
        verbose_name = "里程碑事件"
        verbose_name_plural = "里程碑事件"

    def __str__(self):
        return f"{self.baby}: {self.title}({self.happen_date})"


class MedicationRecord(models.Model):
    """用药记录 - 记录宝宝的用药情况"""
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 关联宝宝
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name="medication_records")
    # 疾病或症状
    disease = models.CharField(verbose_name="病症", max_length=100, blank=True)
    # 药物名称
    medicine_name = models.CharField(verbose_name="药物名称", max_length=100)
    # 用药剂量
    dosage = models.CharField(verbose_name="剂量", max_length=50)
    # 用药频次
    frequency = models.CharField(verbose_name="频次", max_length=50, blank=True, help_text="如:每日3次")
    # 用药时间
    administration_time = models.DateTimeField("用药时间")
    # 给药途径
    route = models.CharField(verbose_name="给药途径", max_length=50, blank=True, help_text="如:口服、外用")
    # 医嘱
    doctor_advice = models.TextField(verbose_name="医嘱", blank=True)
    # 备注信息
    notes = models.TextField(verbose_name="备注", blank=True)
    # 记录创建者
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # 记录创建时间
    created_at = models.DateTimeField(verbose_name="记录时间", default=timezone.now)

    class Meta:
        # 默认按用药时间倒序排列
        ordering = ["-administration_time"]
        verbose_name = "用药记录"
        verbose_name_plural = "用药记录"

    def __str__(self):
        return f"{self.baby}服用{self.medicine_name}: {self.administration_time.strftime('%Y-%m-%d %H:%M')}"


class CheckupRecord(models.Model):
    """体检记录 - 记录宝宝的体检信息"""
    # UUID主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 关联宝宝
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name="checkup_records")
    # 体检日期
    checkup_date = models.DateField("体检日期")
    # 体检机构
    institution = models.CharField(verbose_name="体检机构", max_length=150)
    # 体检医生
    doctor = models.CharField(verbose_name="医生", max_length=50, blank=True)
    # 体检总结
    summary = models.TextField(verbose_name="体检总结", blank=True)
    # 详细体检数据，使用JSON格式存储灵活的数据结构
    details = models.JSONField(verbose_name="详细数据", blank=True, null=True)
    # 医生建议
    suggestions = models.TextField(verbose_name="医生建议", blank=True)
    # 下次体检日期
    next_checkup_date = models.DateField(verbose_name="下次体检日期", blank=True, null=True)
    # 记录创建者
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # 记录创建时间
    created_at = models.DateTimeField(verbose_name="录入时间", default=timezone.now)
    # 最后更新时间
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        # 默认按体检日期倒序排列
        ordering = ["-checkup_date"]
        verbose_name = "体检记录"
        verbose_name_plural = "体检记录"

    def __str__(self):
        return f"{self.baby}的体检记录: {self.checkup_date} @ {self.institution}"


class Tag(models.Model):
    """  标签  """
    tag = models.CharField(verbose_name="标签名",max_length=15, unique=True)

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

class Category(models.Model):
    """分类"""
    classification = models.CharField(verbose_name="分类名",max_length=50,unique=True)
    classification_parent = models.ForeignKey(verbose_name="父类名",to="Category",null=True,blank=True,on_delete=models.CASCADE)

    def children(self):
        return Category.objects.filter(classification_parent=self)


    def __str__(self):
        return self.classification

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"

class Articles(models.Model):
    """宝宝成长的分享 || 养育经验"""
    REJECTED = -1
    PENDING = 0
    APPROVED = 1
    STATE_CHOICES = (
        (REJECTED, "拒绝"),
        (PENDING, "未审核"),
        (APPROVED, "通过"),
    )

    # state = models.IntegerField(
    #     verbose_name='审核状态',
    #     choices=STATE_CHOICES,
    #     default=PENDING,   # 默认未审核
    # )
    title =  models.CharField(verbose_name="标题",max_length=128)

    content = RichTextField(verbose_name='文章分享' )
    # 记录创建时间
    created_articles = models.DateTimeField(verbose_name="发表时间", default=timezone.now)
    # 最后更新时间
    updated_articles = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    # 作者
    author = models.ForeignKey(verbose_name='作者', to=User, on_delete=models.CASCADE, null=True)
    # 审核状态
    state = models.IntegerField(verbose_name='审核状态',choices=STATE_CHOICES,default=PENDING)
    # 关联关系
    categorys = models.ManyToManyField(verbose_name="所属分类", to=Category)

    tags = models.ManyToManyField(verbose_name="所有标签", to=Tag)


    def get_absolute_url(self):
        return reverse('main:article_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_articles"]
        verbose_name = "社区分享"
        verbose_name_plural = "社区分享"

class Collect(models.Model):
    user = models.ForeignKey(verbose_name="用户",to=User, on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name="文章",to=Articles, on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.article.title}"

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "收藏夹"
        verbose_name_plural = "收藏夹"
        unique_together = ("user", "article")

class Like(models.Model):
    user = models.ForeignKey(verbose_name="用户",to=User,on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name="文章",to=Articles,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}点赞了{self.article.title}"

    class Meta:
        verbose_name = "点赞"
        verbose_name_plural = "点赞"
        unique_together = ("user", "article")




# article_comment



class ArticleComments(models.Model):
    """文章评论模型"""
    #  用户外键：适配自定义用户模型，增加related_name便于反向查询
    user = models.ForeignKey(
        verbose_name="评论用户",
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_comments"  # 反向查询：用户.article_comments.all() 获取该用户所有评论
    )

    # 文章外键：增加related_name，便于通过文章查所有评论
    article = models.ForeignKey(
        verbose_name="关联文章",
        to=Articles,
        on_delete=models.CASCADE,
        related_name="comments"  # 反向查询：文章.comments.all() 获取该文章所有评论
    )

    #  评论内容
    content = models.TextField(
        verbose_name="评论内容",
        max_length=500,
        null=False,
        blank=False
    )

    # 时间字段
    create_time = models.DateTimeField(
        verbose_name="评论时间",
        auto_now_add=True,
        db_index=True
    )


    # 支持评论点赞、
    like_count = models.PositiveIntegerField(
        verbose_name="点赞数",
        default=0,  # 默认0赞，无需手动初始化
        db_index=True  # 优化“按点赞数排序”查询效率
    )
    # 软删除
    is_deleted = models.BooleanField(
        verbose_name="是否软删除",
        default=False,
        db_index=True  # 优化“筛选未删除评论”效率（如 queryset.filter(is_deleted=False)）
    )

    def __str__(self):
        # 显示评论摘要，增加评论ID便于定位
        content_summary = self.content[:20] + "..." if len(self.content) > 20 else self.content
        return f"[{self.id}] {self.user.username} 评《{self.article.title}》：{content_summary}"

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "文章评论"
        verbose_name_plural = "文章评论"
        indexes = [
            # 复合索引：优化“按文章+时间”查询（高频场景：查某文章的所有评论并按时间排序）
            models.Index(fields=["article", "-create_time"]),
            # 复合索引：优化“按用户+时间”查询（高频场景：查某用户的所有评论并按时间排序）
            models.Index(fields=["user", "-create_time"]),
        ]