from django import forms
from django.contrib.auth.models import User
from .models import Case


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="密碼")
    password2 = forms.CharField(widget=forms.PasswordInput, label="確認密碼")

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {'username': '用戶名', 'email': '電郵'}

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("兩次密碼不一致")
        return cleaned_data


CITY_CHOICES = [
    ('香港', '香港'),
    ('台北', '台北'),
    ('北京', '北京'),
    ('上海', '上海'),
    ('廣州', '廣州'),
    ('深圳', '深圳'),
    ('成都', '成都'),
    ('武漢', '武漢'),
    ('西安', '西安'),
    ('澳門', '澳門'),
    ('新加坡', '新加坡'),
    ('吉隆坡', '吉隆坡'),
    ('東京', '東京'),
    ('首爾', '首爾'),
    ('曼谷', '曼谷'),
]

CATEGORY_CHOICES = [
    ('career', '事業'),
    ('wealth', '財運'),
    ('relationship', '感情'),
    ('health', '健康'),
    ('other', '其他'),
]

CAREER_SUBTYPE_CHOICES = [
    ('', '--- 請選擇 ---'),
    ('job_search', '求職面試'),
    ('job_change', '跳槽轉職'),
    ('promotion', '升遷晉升'),
    ('layoff', '裁員憂慮'),
    ('startup', '創業開業'),
    ('partnership', '合夥合作'),
    ('investment', '投資項目'),
    ('shop_rental', '租鋪選址'),
    ('bidding', '項目招標'),
    ('stay_or_leave', '去留問題'),
    ('other', '其他'),
]

REQUESTER_TYPE_CHOICES = [
    ('self', '本人問'),
    ('proxy', '代他人問'),
]


class CaseCreationForm(forms.Form):
    # 基本信息
    title = forms.CharField(max_length=200, label="案例標題", help_text="簡短描述問事主題")
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label="問事類別", initial='career')
    question = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="問事問題",
                               help_text="詳細描述你的問題")

    # 求測人信息
    name = forms.CharField(max_length=50, label="姓名", required=False)
    age = forms.IntegerField(min_value=1, max_value=120, label="年齡", required=False)
    gender = forms.ChoiceField(choices=[('', '不詳'), ('M', '男'), ('F', '女')],
                               label="性別", required=False)

    # 時間與地點
    manual_time = forms.DateTimeField(
        label="起心動念時間",
        help_text="請輸入第一次產生這個念頭的時間（格式：2026-01-13 14:30）",
        input_formats=['%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M'],
        required=False
    )
    city = forms.ChoiceField(choices=CITY_CHOICES, label="所在城市", initial='香港')

    # 事業類專用字段
    sub_type = forms.ChoiceField(choices=CAREER_SUBTYPE_CHOICES, label="細分場景", required=False)
    requester_type = forms.ChoiceField(choices=REQUESTER_TYPE_CHOICES, label="求測人類型",
                                       initial='self', required=False)
    has_supervisor = forms.NullBooleanField(
        label="是否有直接上司",
        widget=forms.Select(choices=[('', '不適用'), ('True', '有'), ('False', '沒有')]),
        required=False
    )
    has_competitor = forms.NullBooleanField(
        label="是否有競爭對手",
        widget=forms.Select(choices=[('', '不適用'), ('True', '有'), ('False', '沒有')]),
        required=False
    )
    has_investment = forms.NullBooleanField(
        label="是否有資金投入",
        widget=forms.Select(choices=[('', '不適用'), ('True', '有'), ('False', '沒有')]),
        required=False
    )


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['feedback_result', 'feedback_comment']
        labels = {
            'feedback_result': '驗證結果',
            'feedback_comment': '詳細說明（事後實際發生了什麼？）',
        }
        widgets = {
            'feedback_comment': forms.Textarea(attrs={'rows': 4}),
        }
