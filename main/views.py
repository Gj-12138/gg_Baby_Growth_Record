from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from main.forms import ArticleForm
from main.models import Articles, Category, Collect, ArticleComments, Link
from users.models import User


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
    paginate_by = 1

    def get_queryset(self):
        category_id = self.request.GET.get('category',"all")
        search_query = self.request.GET.get('query', '').strip()

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

        # 2. 富文本搜索修：先剥离HTML标签，再匹配纯文本
        if search_query:
            # 用extra()执行SQL函数，在数据库层面剥离HTML标签
            # 注：不同数据库函数略有差异，以下适配MySQL；若用PostgreSQL，将REGEXP_REPLACE换成regexp_replace
            queryset = queryset.extra(
                where=[
                    # 标题搜索
                    "main_articles.title LIKE %s",
                    # 富文本content搜索：先剥离HTML标签，再匹配关键词
                    "REGEXP_REPLACE(main_articles.content, '<[^>]+>', '', 1) LIKE %s",
                    # # 3. 作者名搜索：必须加外键关联条件，否则会出现表数据笛卡尔积（无意义匹配）
                    # "main_articles.author_id = users_user.id AND users_user.username LIKE %s"
                ],
                params=[
                    f'%{search_query}%',  # 标题匹配
                    f'%{search_query}%',  # 剥离标签后的content匹配
                    # f'%{search_query}%'  # 作者名匹配
                ],
                # tables=['users_user']  # 关联用户表
            )

        return queryset.order_by('-created_articles')



    def get_context_data(self, **kwargs):
        # 传递额外参数到模板：当前分类、搜索关键词、所有分类（用于筛选栏）
        context = super().get_context_data(**kwargs)
        # 当前分类ID（用于模板高亮选中分类）
        context['category'] = self.request.GET.get('category', 'all')
        # 当前搜索关键词（用于模板回显搜索框、显示搜索结果提示）
        context['query'] = self.request.GET.get('query', '').strip()
        # 所有分类（用于模板渲染分类筛选栏）
        context['all_categories'] = Category.objects.all()
        return context



@method_decorator(login_required(login_url="users:login"), name="dispatch")
class ArticleManageView(ListView):
    model = Articles

    context_object_name = 'articles'
    template_name = 'main/article_manage.html'
    paginate_by = 10

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

        # 4. 创建评论（关联当前登录用户、文章）
        ArticleComments.objects.create(
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
            'comment_count': new_comment_count  # 给前端更新“评论总数”显示
        })




    # 异常处理：文章不存在、数据库错误等
    except Articles.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': '关联的文章不存在或未通过审核！'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': f'评论提交失败：{str(e)}'})


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

def like_articles(request):
    a_id = request.POST.get('article')
    u_id = request.POST.get('user')
    user = get_object_or_404(User, id=u_id)
    article = get_object_or_404(Articles, id=a_id)
    link = Link.objects.filter(article=article, user=user).first()

    if link is None:
        Link.objects.create(article=article, user=user)
        link_count = Link.objects.filter(article=article).count()
        return JsonResponse({"code": 200, "status": 1, "msg":"点赞成功","link_count":link_count})
    else:
        link.delete()
        link_count = Link.objects.filter(article=article).count()
        return JsonResponse({"code":200,"status":1,"msg":"点赞成功","link_count":link_count})



