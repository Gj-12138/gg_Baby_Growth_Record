import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from main.forms import ArticleForm, RecordForm, VaccineForm, VaccineRecordForm, EventForm
from main.models import Articles, Category, Collect, ArticleComments, Like, Record, Photo, Vaccine, VaccineRecord, \
    Event, Tag
from users.models import User, Baby


# Create your views here.
def index(request):
    return render(request,'main/index.html')



"""
社区-文章
"""

class ArticleListView(ListView):
    # model = Articles
    context_object_name = 'articles'
    template_name = 'main/article_list.html'
    paginate_by = 9

    def get_queryset(self):
        category_id = self.request.GET.get('category',"all")
        # search_query = self.request.GET.get('query', '').strip()

        queryset = Articles.objects.filter()
        # queryset = Articles.objects.filter(state=Articles.APPROVED)

        if category_id and category_id != 'all' and category_id.isdigit():
            cat = get_object_or_404(Category,id=category_id)
            queryset = queryset.filter(categorys=cat)


        # if search_query:
        #     queryset = queryset.filter(
        #         Q(title__icontains=search_query) |  # 标题包含关键词
        #         Q(content__icontains=search_query) |  # 内容包含关键词
        #         Q(author__username__icontains=search_query)  # 作者名包含关键词
        #     )

        # 富文本搜索修：先剥离HTML标签，再匹配纯文本
        # if search_query:
        #     # 用extra()执行SQL函数，在数据库层面剥离HTML标签
        #     # 注：不同数据库函数略有差异，以下适配MySQL；若用PostgreSQL，将REGEXP_REPLACE换成regexp_replace
        #     queryset = queryset.extra(
        #         where=[
        #             # 标题搜索
        #             "main_articles.title LIKE %s",
        #             # 富文本content搜索：先剥离HTML标签，再匹配关键词
        #             "REGEXP_REPLACE(main_articles.content, '<[^>]+>', '', 1) LIKE %s",
        #             # # 3. 作者名搜索：必须加外键关联条件，否则会出现表数据笛卡尔积（无意义匹配）
        #             # "main_articles.author_id = users_user.id AND users_user.username LIKE %s"
        #         ],
        #         params=[
        #             f'%{search_query}%',  # 标题匹配
        #             f'%{search_query}%',  # 剥离标签后的content匹配
        #             # f'%{search_query}%'  # 作者名匹配
        #         ],
        #         # tables=['users_user']  # 关联用户表
        #     )

        return queryset.order_by('-created_articles')



    def get_context_data(self, **kwargs):
        # 传递额外参数到模板：当前分类、搜索关键词、所有分类（用于筛选栏）
        context = super().get_context_data(**kwargs)
        # 当前分类ID（用于模板高亮选中分类）
        context['category'] = self.request.GET.get('category', 'all')
        context['tag'] = self.request.GET.get('tag', 'all')
        # 当前搜索关键词（用于模板回显搜索框、显示搜索结果提示）
        context['query'] = self.request.GET.get('query', '').strip()
        # 所有分类（用于模板渲染分类筛选栏）
        context['all_categories'] = Category.objects.all()
        context['all_tags'] = Tag.objects.all()
        return context

@method_decorator(login_required(login_url="users:login"), name="dispatch")
class ArticleManageView(ListView):
    model = Articles

    context_object_name = 'articles'
    template_name = 'main/article_manage.html'
    paginate_by = 9

    def get_queryset(self):
        queryset = Articles.objects.filter(author=self.request.user)
        return queryset

class ArticleDetailView(DetailView):
    queryset = Articles.objects.all()
    context_object_name = 'article'
    template_name = 'main/article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_article = self.get_object()

        context["content"] = ArticleComments.objects.filter(
            article=current_article,
            is_deleted = False
        ).order_by("-create_time")

        context["content_count"] = context["content"].count()
        # 传递CSRF令牌（Ajax提交评论需要，也可在模板中直接用{ % csrf_token %}）
        context['csrf_token'] = self.request.META.get('CSRF_COOKIE', '')

        return context


# 评论
# 登录才能提交评论：用login_required装饰器
@login_required(login_url="users:login")
# 只接受POST请求：用require_POST装饰器
@require_POST
def add_comment(request, article_id):
    try:
        # 1. 获取请求数据（Ajax传递的评论内容）
        comment_content = request.POST.get('content', '').strip()

        # 2. 验证数据
        if not comment_content:
            return JsonResponse({'status': 'error', 'msg': '评论内容不能为空！'})
        if len(comment_content) > 500:  # 对应评论模型的content字段max_length=500
            return JsonResponse({'status': 'error', 'msg': '评论内容不能超过500字！'})

        # 3. 获取关联的文章（不存在则返回404）
        article = Articles.objects.get(id=article_id, state=Articles.APPROVED)  # 只允许对审核通过的文章评论
        user = User.objects.get(id=request.POST.get('user', ''))

        # 4. 创建评论（关联当前登录用户、文章）
        # ArticleComments.objects.create(
        #     user=request.user,
        #     article=article,
        #     content=comment_content
        #     # like_count默认0，is_deleted默认False，无需手动传
        # )
        try:

            parent =  ArticleComments.objects.get(id = request.POST.get("parent"))
            instance =  ArticleComments.objects.create(
                            user=request.user,
                            article=article,
                            content=comment_content,
                            parent =parent,
                            # like_count默认0，is_deleted默认False，无需手动传
                        )
        except ArticleComments.DoesNotExist:
            instance = ArticleComments.objects.create(
                user=request.user,
                article=article,
                content=comment_content
                # like_count默认0，is_deleted默认False，无需手动传
            )
        # 5. 返回成功响应
        new_comment_count = ArticleComments.objects.filter(article=article, is_deleted=False).count()

        return JsonResponse({
            'status': 'success',
            'msg': '评论提交成功！',
            'comment_count': new_comment_count, # 给前端更新“评论总数”显示
            'data': {  # ← 这一整块就是 res.data
                "username": user.username ,
                "avatar":user.avatar.url,
                'content': instance.content,
                'created': instance.create_time.strftime('%Y-%m-%d %H:%M'),
                'id': instance.id,
            }
        })

    # 异常处理：文章不存在、数据库错误等
    except Articles.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': '关联的文章不存在或未通过审核！'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': f'评论提交失败：{str(e)}'})

def delete_comment(request,article_id):
    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        c = ArticleComments.objects.filter(id=comment_id,article = article_id).first()
        if c:
            c.delete()
            return JsonResponse({
                "code": 0,
                "msg": "删除成功",
            })
        else:
            return JsonResponse({
                "code": -1005,
                "msg": "禁止删除",
            })

@method_decorator(login_required(login_url="users:login"), name="dispatch")
class ArticleCreateView(CreateView):
    """
        创建文章
    """
    model = Articles
    context_object_name = 'articles'
    template_name = 'main/article_form.html'
    form_class = ArticleForm
    success_url = reverse_lazy('main:article_manage')
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

@method_decorator(login_required(login_url="users:login"), name="dispatch")
class ArticleUpdateView(UpdateView):
    model = Articles
    context_object_name = 'articles'
    template_name = 'main/article_form.html'
    form_class = ArticleForm
    success_url = reverse_lazy('main:article_manage')

@method_decorator(login_required(login_url="users:login"), name="dispatch")
class ArticleDeleteView(DeleteView):
    model = Articles
    context_object_name = 'articles'
    template_name = 'main/article_confirm_delete.html'
    success_url = reverse_lazy('main:article_manage')

@login_required(login_url="users:login")
def collect_articles(request):
    a_id = request.POST.get('article')
    u_id = request.POST.get('user')
    user = get_object_or_404(User, id=u_id)
    articles = get_object_or_404(Articles, id=a_id)
    collect = Collect.objects.filter(article=articles, user=user).first()
    if collect is None:
        Collect.objects.create(article=articles, user=user)
        return JsonResponse({'code': 200,'msg':'收藏成功','status':1})
    else:
        collect.delete()
        return JsonResponse({'code': 200, 'msg': '取消收藏成功', 'status': 1})

@login_required(login_url="users:login")
def like_articles(request):
    a_id = request.POST.get('article')
    u_id = request.POST.get('user')
    user = get_object_or_404(User, id=u_id)
    article = get_object_or_404(Articles, id=a_id)

    like = Like.objects.filter(article=article, user=user).first()

    if like is None:
        Like.objects.create(article=article, user=user)
        like_count = Like.objects.filter(article=article).count()
        return JsonResponse({"code": 200, "status": 1, "msg":"点赞成功","like_count":like_count})
    else:
        like.delete()
        like_count = Like.objects.filter(article=article).count()
        return JsonResponse({"code":200,"status":1,"msg":"取消点赞成功","like_count":like_count})


# Record成长记录
class RecordListView(ListView):
    model = Record
    context_object_name = 'records'
    template_name = "main/record_list.html"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user).order_by('-created_at')

class RecordDetailView(DetailView):
    model = Record
    context_object_name = 'record'
    template_name = "main/record_detail.html"

class RecordCreateView(LoginRequiredMixin, CreateView):
    model = Record
    form_class = RecordForm
    template_name = 'main/record_form.html'
    success_url = reverse_lazy('main:record_list')  # 非AJAX请求的默认跳转

    def get_object(self, queryset=None):
        record = super().get_object(queryset)
        # 校验：只有记录的创建者才能查看
        if record.author != self.request.user:
            raise PermissionDenied("你没有权限查看这条记录")  # 拒绝访问
        return record


    def get_form(self, form_class=None):
        """过滤仅显示当前用户关联的宝宝"""
        form = super().get_form(form_class)
        # 通过Baby与User的多对多关系（Baby.parents）过滤
        form.fields['baby'].queryset = Baby.objects.filter(
            parents=self.request.user,
            is_deleted=False  # 排除已删除的宝宝（若有此需求）
        )
        return form

    def form_valid(self, form):
        """处理表单验证通过：创建记录+同步关联图片"""
        # 1. 保存记录基本信息（关联作者）
        form.instance.author = self.request.user
        record = form.save()  # 保存记录，获取完整对象

        # 2. 处理多图片上传（从请求中获取图片文件）
        self._handle_photos(record)

        # 3. 根据请求类型返回不同响应（AJAX/普通请求）
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX请求：返回JSON结果
            return JsonResponse({
                'status': 'success',
                'msg': '记录创建成功',
                'record_id': str(record.id)
            })
        else:
            # 普通表单提交：使用默认跳转
            return super().form_valid(form)

    def form_invalid(self, form):
        """处理表单验证失败：返回错误信息"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX请求：返回JSON格式错误
            errors = {field: err[0] for field, err in form.errors.items()}
            return JsonResponse({
                'status': 'error',
                'msg': '表单填写有误',
                'errors': errors
            }, status=400)
        else:
            # 普通请求：使用默认错误处理
            return super().form_invalid(form)

    def _handle_photos(self, record):
        """内部方法：处理图片上传并关联到记录"""
        photo_files = self.request.FILES.getlist('photos')  # 获取所有上传的图片
        for file in photo_files:
            # 验证文件大小（单张不超过5MB）
            if file.size > 5 * 1024 * 1024:
                continue  # 跳过超大文件

            # 验证文件格式（仅允许图片）
            ext = os.path.splitext(file.name)[-1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                continue  # 跳过非图片文件

            # 创建图片记录并关联到当前记录
            Photo.objects.create(
                baby=record.baby,  # 与记录关联同一宝宝
                record=record,  # 关联当前创建的记录
                file=file,
                media_type='photo',
                uploaded_by=self.request.user
            )

# 上传照片（关联已有记录）- 函数视图（支持 AJAX 异步上传多张）
@login_required
def upload_photos(request):
    if request.method == 'POST' and request.FILES.getlist('photos'):
        record_id = request.POST.get('record_id')
        # 验证记录是否存在，且属于当前用户
        try:
            record = Record.objects.get(
                id=record_id,
                author=request.user
            )
        except Record.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': '记录不存在或无权限'}, status=403)

        # 批量处理多张照片
        photo_count = 0
        for photo_file in request.FILES.getlist('photos'):
            # 自动判断媒体类型（照片/视频）
            file_ext = os.path.splitext(photo_file.name)[-1].lower()
            media_type = 'photo' if file_ext in ['jpg', 'jpeg', 'png', 'gif'] else 'video'

            # 创建照片记录
            Photo.objects.create(
                baby=record.baby,
                record=record,
                file=photo_file,
                media_type=media_type,
                uploaded_by=request.user,
                # 若前端传递拍摄时间，可在此处接收（如 request.POST.get('shot_at')）
                # shot_at=request.POST.get('shot_at') if request.POST.get('shot_at') else None
            )
            photo_count += 1

        return JsonResponse({
            'status': 'success',
            'msg': f'成功上传 {photo_count} 张媒体文件',
            'photo_count': record.related_photos.count()  # 记录当前关联的总照片数
        })

    # 非 POST 请求或无文件，返回错误
    return JsonResponse({'status': 'error', 'msg': '请提交有效的照片文件'}, status=400)

class VaccineListView(ListView):
    model= Vaccine
    context_object_name = 'vaccines'
    template_name = "main/vaccines_list.html"
    paginate_by = 9

class VaccineDetailView(DetailView):
    model = Vaccine
    context_object_name = 'vaccine'
    template_name = "main/vaccines_form.html"


# 接种记录
class VaccineRecordListView(ListView):
    model = VaccineRecord
    context_object_name = 'vaccine_records'
    template_name = "main/vaccine_record_list.html"
    paginate_by = 9

    def get_queryset(self):
        """只查询当前用户的接种记录"""
        queryset = VaccineRecord.objects.filter(created_by=self.request.user)

        # 支持筛选（按宝宝和疫苗）
        baby_id = self.request.GET.get('baby')
        vaccine_id = self.request.GET.get('vaccine')
        if baby_id:
            queryset = queryset.filter(baby_id=baby_id)
        if vaccine_id:
            queryset = queryset.filter(vaccine_id=vaccine_id)
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['babies'] = Baby.objects.filter(parents=self.request.user, is_deleted=False)
        context['vaccines'] = Vaccine.objects.all()
        return context



class VaccineRecordDetailView(DetailView):
    model = VaccineRecord
    context_object_name = 'vaccine_record'
    template_name = "main/vaccine_record_detail.html"


class VaccineRecordDeleteView(DeleteView):
    model = VaccineRecord
    context_object_name = 'vaccine_record'
    success_url = reverse_lazy('main:vaccine_record_list')

class VaccineRecordCreateView(CreateView):
    model = VaccineRecord
    context_object_name = 'vaccine_record'
    template_name = "main/vaccine_record_from.html"
    form_class = VaccineRecordForm
    success_url = reverse_lazy('main:vaccine_record_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

# 里程碑事件
class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = "main/event_list.html"
    paginate_by = 9
    def get_queryset(self):

        # 筛选所有事件，按发生日期倒序
        return Event.objects.filter(baby__parents=self.request.user).order_by('-happen_date')

    def get_context_data(self,** kwargs):
        context = super().get_context_data(**kwargs)
        context['babies'] = Baby.objects.filter(parents=self.request.user)  # 传递宝宝信息到模板
        return context


class EventDetailView(LoginRequiredMixin,DetailView):
    model = Event
    context_object_name = 'event'
    template_name = "main/event_detail.html"
    def get_queryset(self):
        # 仅允许查看当前用户关联宝宝的事件
        return Event.objects.filter(
            baby__parent_links__user=self.request.user
        ).select_related('baby', 'type', 'created_by').prefetch_related('photos')

class EventDeleteView(LoginRequiredMixin,DeleteView):
    model = Event
    context_object_name = 'event'

class EventCreateView(LoginRequiredMixin,CreateView):
    model = Event
    context_object_name = 'event'
    template_name = "main/event_form.html"
    form_class = EventForm


    def get_form_kwargs(self):
        # 向表单传递宝宝ID，用于过滤照片
        kwargs = super().get_form_kwargs()
        self.baby = get_object_or_404(
            Baby,
            id=self.kwargs['baby_id'],
            parent_links__user=self.request.user
        )
        kwargs['baby'] = self.baby
        return kwargs

    def form_valid(self, form):
        # 关联事件到宝宝和创建者
        form.instance.baby = self.baby
        form.instance.created_by = self.request.user
        messages.success(self.request, "里程碑事件创建成功！")
        return super().form_valid(form)

    def get_success_url(self):
        # 跳转回该宝宝的事件列表
        return reverse_lazy('main:event_list')  # 或者根据您的URL配置调整

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['baby'] = self.baby
        context['title'] = f"为 {self.baby.name} 添加里程碑事件"
        context['is_new'] = True
        return context


class EventUpdateView(LoginRequiredMixin,UpdateView):
    model = Event
    context_object_name = 'event'
    template_name = "main/event_form.html"
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 在编辑时也需要传递 baby 给表单，用于过滤照片
        kwargs['baby'] = self.object.baby
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 从事件对象中获取宝宝信息
        context['baby'] = self.object.baby
        context['is_new'] = False
        context['title'] = f"编辑 {self.object.baby.name} 的里程碑事件"
        return context

    def form_valid(self, form):
        # 编辑时不需要设置 baby，因为已经关联了
        messages.success(self.request, "里程碑事件更新成功！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('main:event_list')