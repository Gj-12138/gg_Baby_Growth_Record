from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.hashers import check_password

from main.models import BabyParent
from users.models import Baby, User


class BabyAddForm(forms.ModelForm):
    # 家长角色选择（默认妈妈）
    parent_role = forms.ChoiceField(
        choices=BabyParent.ROLE_CHOICES,
        label="家长身份",
        initial="mother",  # 默认妈妈
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Baby
        fields = [
            'avatar',
            'name',
            'nickname',
            'gender',
            'birthday',
            'birth_weight',
            'birth_height',
            'gestational_age',
            'blood_type',
            'allergies',
            'notes',
            'parent_role',
        ]
        widgets = {
            'avatar': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*',
                }
            ),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '宝宝正式姓名'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '宝宝小名'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birthday': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
            'birth_weight': forms.NumberInput(
                attrs={'class': 'form-control', 'step': 0.01, 'placeholder': 'kg'}
            ),
            'birth_height': forms.NumberInput(
                attrs={'class': 'form-control', 'step': 0.1, 'placeholder': 'cm'}
            ),
            'gestational_age': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': '孕周'}
            ),
            'blood_type': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '如 A+、O-' }
            ),
            'allergies': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': '可空；多种过敏请用逗号分隔'}
            ),
            'notes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': '任意备注'}
            ),
        }





class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email','password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                "placeholder": "用户名",
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                "placeholder": "电子邮箱",
                "block": False,
                'required': 'required',
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                "placeholder": "用户密码",
                'required': 'required',
            }),

        }
        labels = {
            'username': "账号",
            'password': "密码",
            'email':"电子邮箱"
        }
        required = {
            'username': True,
            'password': True,
            'email': True,
        }


    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "确认密码",
    }))
    # 验证码
    captcha = CaptchaField(label="验证码")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("账号已存在")
        return username
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("该邮箱已注册！！！")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 6:
            raise forms.ValidationError("密码短")
        return password
    def clean_password2(self):
        password2 = self.cleaned_data['password2']
        password = self.cleaned_data['password']
        if password2 != password:
            raise forms.ValidationError("确认密码错误")


class LoginForm(forms.Form):
    username = forms.CharField(
        label='账号',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists() and not  User.objects.filter(email=username).exists():
            raise forms.ValidationError("账号不存在！！！")
        return username

class PasswordChangeForm(forms.Form):
    """
    修改密码
    """
    old_password = forms.CharField(
        label='旧密码',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   "placeholder": "旧密码",
                   "id":"old_password"
                   }
        )
    )
    new_password = forms.CharField(
        label='新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control' ,"placeholder": "新密码","id":"new_password",})
    )
    new_password2 = forms.CharField(
        label='确认新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder": "新密码确认","id":"new_password2",})
    )

    def __init__(self, *args, **kwargs):
        """
        必须要把当前登录用户传进来，才能校验旧密码
        """
        self.user = kwargs.pop('user')  # 视图里传进来
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old = self.cleaned_data.get('old_password')
        if not check_password(old, self.user.password):
            raise forms.ValidationError('旧密码输入错误')
        return old

    def clean_new_password(self):
        pwd = self.cleaned_data.get('new_password')
        if pwd and len(pwd) < 6:
            raise forms.ValidationError('新密码至少 6 位')
        return pwd

    def clean(self):
        cleaned = super().clean()
        pwd1 = cleaned.get('new_password')
        pwd2 = cleaned.get('new_password2')
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error('new_password2', '两次新密码不一致')
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save(update_fields=['password'])
        return self.user


class UserCenterChangeForm(forms.Form):
    username = forms.CharField( max_length = 100,label ='用户名',widget=forms.TextInput(attrs={'class': 'form-control'}))
    headerimg = forms.CharField(label="头像",widget=forms.FileInput(attrs={'class': 'form-control'}))


class UserCenterForm(forms.Form):
    username = forms.CharField( max_length = 100,label ='用户名',widget=forms.TextInput(attrs={'class': 'form-control'}))
    headerimg = forms.CharField(label="头像",widget=forms.FileInput(attrs={'class': 'form-control'}))



class UserManagementForm(forms.ModelForm):
    header = forms.ImageField(
        label="头像",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"})
    )
    class Meta:
        model = User
        fields = ["username", "email", "header", "is_active", "date_joined", "last_login"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "date_joined": forms.DateTimeInput(
                attrs={"class": "form-control", "readonly": "readonly"}
            ),
            "last_login": forms.DateTimeInput(
                attrs={"class": "form-control", "readonly": "readonly"}
            ),
        }