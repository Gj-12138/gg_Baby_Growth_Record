from ckeditor.widgets import CKEditorWidget
from django import forms
from django.utils import timezone
from django.views.generic import UpdateView

from main.models import Articles, Record, Vaccine, VaccineRecord, Event, Photo


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Articles
        fields = ['title', 'content','tags','categorys']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'content': CKEditorWidget(attrs={'class':'form-control'}),
        }
class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['baby', 'title', 'content', 'category', 'record_date', 'voice']
        widgets = {
            # 优化字段渲染：日期选择器、富文本编辑器等
            'record_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'  # 适配 HTML5 日期格式
            ),
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': '请详细描述宝宝的成长情况...'}
            ),
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '如“宝宝第一次独立坐稳”'}
            ),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'baby': forms.Select(attrs={'class': 'form-select'}),
            'voice': forms.FileInput(
                attrs={'class': 'form-control', 'accept': 'audio/*'}  # 仅允许音频文件
            )
        }
        labels = {
            'baby': '宝宝',
            'title': '记录标题',
            'content': '详细内容',
            'category': '记录分类',
            'record_date': '记录日期',
            'voice': '语音补充（可选）'
        }


class VaccineForm(forms.ModelForm):
    class Meta:
        model = Vaccine
        fields = ['name', 'code', 'category', 'shot_age_days_start', 'shot_age_days_end',
                  'dose', 'interval_days', 'description', 'contraindication', 'side_effects']
        widgets = {
            # 文本输入框
            'name': forms.TextInput(attrs={
                'class': 'form-control',  # 样式类
                'placeholder': '请输入疫苗名称（如：乙肝疫苗）'  # 占位提示
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入疫苗编码（如：HBV）'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入疫苗类别（如：一类疫苗）'
            }),

            # 数字输入框
            'shot_age_days_start': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,  # 最小值限制
                'placeholder': '起始日龄（天）'
            }),
            'shot_age_days_end': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '截止日龄（天，可选）'
            }),
            'dose': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,  # 剂次至少为1
                'placeholder': '接种剂次'
            }),
            'interval_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '与上一剂的间隔天数'
            }),

            # 多行文本框（设置rows属性）
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,  # 行数
                'placeholder': '请输入疫苗说明'
            }),
            'contraindication': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入接种禁忌症'
            }),
            'side_effects': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入可能的不良反应'
            }),
        }

class VaccineRecordForm(forms.ModelForm):
    class Meta:
        model = VaccineRecord
        fields =  ['baby', 'vaccine', 'shot_date', 'batch_number',
                   'hospital', 'doctor', 'reaction', 'next_shot_date',]


        widgets = {
            # 日期字段使用日期选择器
            'shot_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': '选择接种日期'
                }
            ),
            'next_shot_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': '选择下次接种日期（可选）'
                }
            ),
            # 文本输入字段样式
            'batch_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例如：20230501'
                }
            ),
            'hospital': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '填写接种医院或社区卫生服务中心'
                }
            ),
            'doctor': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '填写接种医生姓名（可选）'
                }
            ),
            # 多行文本框
            'reaction': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': '记录接种后是否有发热、红肿等不良反应（可选）'
                }
            ),
            # 下拉选择框样式
            'baby': forms.Select(attrs={'class': 'form-select'}),
            'vaccine': forms.Select(attrs={'class': 'form-select'}),
        }
        # 字段标签
        labels = {
            'baby': '宝宝',
            'vaccine': '疫苗名称',
            'shot_date': '接种日期',
            'batch_number': '疫苗批号',
            'hospital': '接种地点',
            'doctor': '接种医生',
            'reaction': '接种后反应',
            'next_shot_date': '下次接种日期',
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [ 'type', 'title', 'happen_date','description','photos',]

    def __init__(self, *args, **kwargs):
        self.baby = kwargs.pop('baby', None)
        super().__init__(*args, **kwargs)

        # # 如果提供了宝宝信息，可以过滤照片或其他相关数据
        # if self.baby:
        #     # 例如：只显示属于该宝宝的照片
        #     self.fields['photos'].queryset = Photo.objects.filter(baby=self.baby)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.baby:
            instance.baby = self.baby
        if commit:
            instance.save()
            self.save_m2m()
        return instance




