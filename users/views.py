from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.base import ContentFile
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from Dome01.settings import KEY_EMAIL
from users.froms import BabyAddForm, RegisterForm, LoginForm, UserCenterForm, PasswordChangeForm, UserCenterChangeForm
from users.models import Baby, User
from utils.encryption_decryption import encryption, decryption

from django.contrib.auth import login as lgi ,logout as lgo

# Create your views here.
class BabyListView(ListView):
    model = Baby
    context_object_name = 'baby'
    template_name = 'users/baby.html'
    paginate_by = 5

class BabyInfoDetailView(DetailView):
    queryset = Baby.objects.all()


class BabyCreateView(CreateView):
    model = Baby
    form_class = BabyAddForm
    success_url = reverse_lazy('users:baby')

class BabyUpdateView(UpdateView):
    model = Baby
    form_class = BabyAddForm
    success_url = reverse_lazy('users:baby')
    template_name_suffix = "_update"

class BabyDeleteView(DeleteView):
    model = Baby
    success_url = reverse_lazy('users:baby')



signer = TimestampSigner()

mesg="桀桀桀,看不见就对了，桀桀桀！！！如果看不到HTML内容，请复制链接手动激活：http://127.0.0.1:8000/user/active/"

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            # user.is_staff = True
            # user.is_superuser = True
            user.save()
            user_id = encryption(str(user.id),KEY_EMAIL)
            signed = signer.sign(f"{user_id}")
            active_url = f"http://{get_current_site(request).domain}{reverse('users:active',args=(signed,))}"
            user.email_user(subject="学习测试" ,message=mesg,html_message= f'''
                                <h3>Hi {user.username}，欢迎注册</h3>
                                <p>请点击下方链接激活账号：</p>
                                <a href='{active_url}'> 是兄弟就电我</a>
                                '''
                            )


            return redirect( reverse('users:login' ))
        else:
            return render(request,"users/register.html",{"register_form":form})
    else:
        form =  RegisterForm()
        return render(request,"users/register.html",{'register_form':form})


def login(request):
    if request.method == "POST":
        lf = LoginForm(request.POST)
        if lf.is_valid():
            user = User.objects.filter(username=lf.cleaned_data['username']).first() or User.objects.filter(email=lf.cleaned_data['username']).first()
            if user and user.is_active:
                if user.check_password(lf.cleaned_data['password']):
                    lgi(request,user)
                    next_url = request.GET.get("next")
                    if next_url:
                        return redirect(next_url)
                    else:

                        return redirect( reverse('main:index' ))
                else:
                    lf.add_error("password","密码错误")
                    return render(request,"users/login.html",{"login_form":lf})
            else:
                lf.add_error("username","账号不存在or账号已被封禁")
                return render(request,"users/login.html",{"login_form":lf})
        else:

            return render(request,"users/login.html",{"login_form":lf})
    else:
        lf = LoginForm()
        return render(request,"users/login.html",{"login_form":lf})

def logout(request):
    lgo(request)
    return redirect(reverse('main:index'))

@login_required(login_url="users:login")
def passwordchange(request):
    if request.method == "POST":
        ucf = PasswordChangeForm(request.POST, user=request.user)
        if ucf.is_valid():
            ucf.save()
            lgo(request)
            return redirect( reverse('user:login' ))
        else:
            return render(request,"users/passwordchange.html",{"form":ucf})
    else:
        ucf = PasswordChangeForm(user=request.user)
        return render(request,"users/passwordchange.html" ,{"form":ucf})

@login_required(login_url="users:login")
def usercenterchange(request):
    if request.method == "POST":
        ucf = UserCenterChangeForm(request.POST, files=request.FILES, initial={"username":request.POST['username'],"headerimg":request.user.avatar})

        if ucf.is_valid():
            request.user.username = ucf.cleaned_data['username']
            request.user.avatar="user/avatars/"+ucf.cleaned_data['headerimg']
            request.user.save()

            return redirect( reverse('main:index' ))
        else:
            return render(request, "users/usercenterchange.html", {"form":ucf})
    else:
        ucf = UserCenterChangeForm( initial={"username":request.user.username,"headerimg":request.user.avatar})
        return render(request, "users/usercenterchange.html", {"form":ucf})

@login_required(login_url="users:login")
def usercenter(request):
    form = UserCenterForm(initial={"username":request.user.username})
    return render(request,"users/usercenter.html",{"form":form})

def active(request,id):
    try:
        designered = signer.unsign(id, max_age=60 * 6)
        user_id = decryption(designered,KEY_EMAIL)
        user = User.objects.filter(id=user_id).first()
        if user:
            user.is_active = True
            user.save()
            return redirect(reverse('users:login'))
        else:
            return render(request, "users/login.html")
    except SignatureExpired:
        return HttpResponse("已过期")
    except BadSignature:
        return HttpResponse("激活链接无效")

@method_decorator(login_required(login_url="users:login"), name="dispatch")
class UserManagement(ListView):
    model = User
    template_name = "users/admin.html"
    context_object_name = "users"
    paginate_by = 10





