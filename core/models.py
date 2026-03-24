from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Case(models.Model):
    """問事案例模型"""
    GENDER_CHOICES = [('M', '男'), ('F', '女'), ('', '不詳')]
    CATEGORY_CHOICES = [
        ('career', '事業'),
        ('wealth', '財運'),
        ('relationship', '感情'),
        ('health', '健康'),
        ('other', '其他'),
    ]
    FEEDBACK_CHOICES = [
        ('accurate', '準確'),
        ('partial', '部分準確'),
        ('inaccurate', '不準確'),
        ('pending', '待驗證'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases',
                             verbose_name="所屬用戶", null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="案例標題")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='career', verbose_name="類別")

    # 求測人信息
    name = models.CharField(max_length=50, blank=True, verbose_name="姓名")
    age = models.IntegerField(null=True, blank=True, verbose_name="年齡")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="性別")

    # 事業類專用字段（依據 QMDJ_Structure_Guide）
    sub_type = models.CharField(max_length=50, blank=True, verbose_name="細分場景")
    requester_type = models.CharField(max_length=20, blank=True, verbose_name="求測人類型")
    has_supervisor = models.BooleanField(null=True, blank=True, verbose_name="是否有直接上司")
    has_competitor = models.BooleanField(null=True, blank=True, verbose_name="是否有競爭對手")
    has_investment = models.BooleanField(null=True, blank=True, verbose_name="是否有資金投入")

    # 時間與地點
    manual_time = models.DateTimeField(null=True, blank=True, verbose_name="問事時間（起心動念）")
    city = models.CharField(max_length=50, blank=True, verbose_name="城市")
    solar_time_used = models.DateTimeField(null=True, blank=True, verbose_name="實際使用太陽時")

    # 問題與分析
    question = models.TextField(blank=True, verbose_name="問事問題")
    question_data = models.JSONField(default=dict, verbose_name="問題數據")
    chart_data = models.JSONField(default=dict, verbose_name="盤面數據")
    ai_analysis = models.TextField(blank=True, verbose_name="AI 分析")

    # 反饋
    feedback_required = models.BooleanField(default=False, verbose_name="需要反饋")
    feedback_submitted = models.BooleanField(default=False, verbose_name="已提交反饋")
    feedback_result = models.CharField(max_length=20, choices=FEEDBACK_CHOICES, blank=True, verbose_name="反饋結果")
    feedback_comment = models.TextField(blank=True, verbose_name="反饋說明")
    feedback_time = models.DateTimeField(null=True, blank=True, verbose_name="反饋時間")

    # 歷史案例字段
    is_historical = models.BooleanField(default=False, verbose_name="是否歷史案例")
    source = models.CharField(max_length=200, blank=True, verbose_name="資料來源")
    ganzhi = models.CharField(max_length=100, blank=True, verbose_name="干支八字")
    key_config = models.TextField(blank=True, verbose_name="關鍵格局")
    expert_judgment = models.TextField(blank=True, verbose_name="大師斷語")
    real_feedback = models.TextField(blank=True, verbose_name="事後反饋")

    created_at = models.DateTimeField(default=timezone.now, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "問事案例"
        verbose_name_plural = "問事案例"

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"


class VIPUser(models.Model):
    """VIP 用戶模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='vip_profile', verbose_name="用戶")
    vip_number = models.CharField(max_length=10, unique=True, verbose_name="VIP 編號")
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp 號碼")
    is_verified = models.BooleanField(default=False, verbose_name="已驗證")
    verification_code = models.CharField(max_length=6, blank=True, verbose_name="驗證碼")
    code_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="驗證碼過期時間")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="驗證時間")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="創建時間")

    class Meta:
        verbose_name = "VIP 用戶"
        verbose_name_plural = "VIP 用戶"

    def __str__(self):
        return f"VIP-{self.vip_number} ({self.user.username})"

    def can_create_case(self):
        """檢查 VIP 用戶是否可以創建新案例"""
        if not self.is_verified:
            return False, "請先完成 WhatsApp 驗證"
        pending = self.user.cases.filter(feedback_required=True, feedback_submitted=False)
        if pending.exists():
            case = pending.first()
            return False, f"請先完成案例「{case.title}」的反饋，才能創建新問事"
        return True, ""

    @property
    def total_cases(self):
        return self.user.cases.filter(is_historical=False).count()

    @property
    def pending_feedback(self):
        return self.user.cases.filter(feedback_required=True, feedback_submitted=False).count()
