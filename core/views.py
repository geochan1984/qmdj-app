from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
import json
import random
import string
from datetime import datetime

from .models import Case, VIPUser
from .forms import RegisterForm, CaseCreationForm, FeedbackForm
from .qimen_engine import generate_jiugong_chart, get_ai_analysis, CITY_DATA


def index(request):
    if request.user.is_authenticated:
        return redirect('case_list')
    historical_cases = Case.objects.filter(is_historical=True).order_by('-created_at')[:6]
    return render(request, 'core/index.html', {'historical_cases': historical_cases})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('case_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email', '')
            password = form.cleaned_data['password']
            if User.objects.filter(username=username).exists():
                messages.error(request, "用戶名已存在")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user)
                messages.success(request, f"歡迎，{username}！")
                return redirect('case_list')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('case_list')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'case_list')
            return redirect(next_url)
        else:
            messages.error(request, "用戶名或密碼錯誤")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='/login/')
def case_list_view(request):
    user_cases = Case.objects.filter(user=request.user, is_historical=False).order_by('-created_at')
    historical_cases = Case.objects.filter(is_historical=True).order_by('-created_at')

    search_q = request.GET.get('q', '')
    if search_q:
        historical_cases = historical_cases.filter(
            Q(title__icontains=search_q) |
            Q(expert_judgment__icontains=search_q) |
            Q(key_config__icontains=search_q) |
            Q(real_feedback__icontains=search_q)
        )

    category_filter = request.GET.get('category', '')
    if category_filter:
        historical_cases = historical_cases.filter(category=category_filter)

    vip_user = None
    try:
        vip_user = request.user.vip_profile
    except VIPUser.DoesNotExist:
        pass

    context = {
        'user_cases': user_cases,
        'historical_cases': historical_cases,
        'vip_user': vip_user,
        'search_q': search_q,
        'category_filter': category_filter,
    }
    return render(request, 'core/case_list.html', context)


@login_required(login_url='/login/')
def create_case_view(request):
    # VIP 權限檢查
    try:
        vip_user = request.user.vip_profile
        can_create, reason = vip_user.can_create_case()
        if not can_create:
            messages.error(request, reason)
            return redirect('case_list')
    except (VIPUser.DoesNotExist, AttributeError):
        pass

    if request.method == 'POST':
        form = CaseCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            title = cd['title']
            category = cd['category']
            question = cd['question']
            name = cd.get('name', '')
            age = cd.get('age')
            gender = cd.get('gender', '')
            city = cd.get('city', '香港')
            sub_type = cd.get('sub_type', '')
            requester_type = cd.get('requester_type', 'self')
            has_supervisor = cd.get('has_supervisor')
            has_competitor = cd.get('has_competitor')
            has_investment = cd.get('has_investment')

            manual_time = cd.get('manual_time')
            if manual_time:
                if hasattr(manual_time, 'replace'):
                    qipan_time = manual_time.replace(tzinfo=None) if manual_time.tzinfo else manual_time
                else:
                    qipan_time = manual_time
            else:
                qipan_time = datetime.now()
                manual_time = qipan_time

            chart_data = generate_jiugong_chart(dt=qipan_time, city=city, use_solar_time=True)

            question_data = {
                'question': question,
                'category': category,
                'sub_type': sub_type,
            }

            is_vip = False
            try:
                _ = request.user.vip_profile
                is_vip = True
            except (VIPUser.DoesNotExist, AttributeError):
                pass

            # 立即建立案例，ai_analysis 標記為分析中
            case = Case.objects.create(
                user=request.user,
                title=title,
                category=category,
                name=name,
                age=age,
                gender=gender,
                city=city,
                manual_time=manual_time,
                question=question,
                question_data=question_data,
                chart_data=chart_data,
                sub_type=sub_type,
                requester_type=requester_type,
                has_supervisor=has_supervisor,
                has_competitor=has_competitor,
                has_investment=has_investment,
                feedback_required=is_vip,
                ai_analysis='__ANALYZING__',
            )

            # 立即跳轉到案例詳情頁，AI 分析在背景執行
            import threading
            def run_ai_analysis(case_id, q_data, c_data):
                try:
                    result = get_ai_analysis(q_data, c_data)
                    Case.objects.filter(id=case_id).update(ai_analysis=result)
                except Exception as e:
                    Case.objects.filter(id=case_id).update(
                        ai_analysis=f'AI 分析暫時不可用（{str(e)[:60]}）'
                    )
            t = threading.Thread(target=run_ai_analysis,
                                 args=(case.id, question_data, chart_data),
                                 daemon=True)
            t.start()

            messages.success(request, "問事案例已建立，AI 分析進行中…")
            return redirect('case_detail', case_id=case.id)
    else:
        form = CaseCreationForm()

    return render(request, 'core/create_case.html', {
        'form': form,
        'cities': list(CITY_DATA.keys()),
    })


@login_required(login_url='/login/')
def case_detail_view(request, case_id):
    case = get_object_or_404(Case, id=case_id)

    if not case.is_historical and case.user != request.user:
        messages.error(request, "無權限查看此案例")
        return redirect('case_list')

    feedback_form = None
    if not case.is_historical and case.user == request.user:
        if request.method == 'POST':
            feedback_form = FeedbackForm(request.POST, instance=case)
            if feedback_form.is_valid():
                case = feedback_form.save(commit=False)
                case.feedback_submitted = True
                case.feedback_time = timezone.now()
                case.save()
                messages.success(request, "反饋已提交！感謝您的驗證。")
                return redirect('case_detail', case_id=case.id)
        else:
            if not case.feedback_submitted:
                feedback_form = FeedbackForm(instance=case)

    chart_data = case.chart_data or {}
    palaces = chart_data.get('palaces', {})
    palaces_int = {}
    for k, v in palaces.items():
        palaces_int[int(k)] = v

    grid_order = [4, 9, 2, 3, 5, 7, 8, 1, 6]

    context = {
        'case': case,
        'chart_data': chart_data,
        'palaces': palaces_int,
        'grid_order': grid_order,
        'feedback_form': feedback_form,
        'special_configs': chart_data.get('special_configs', []),
    }
    return render(request, 'core/case_detail.html', context)


def vip_register_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        _ = request.user.vip_profile
        return redirect('vip_dashboard')
    except VIPUser.DoesNotExist:
        pass

    if request.method == 'POST':
        whatsapp = request.POST.get('whatsapp_number', '').strip()
        if not whatsapp:
            messages.error(request, "請輸入 WhatsApp 號碼")
        else:
            existing_count = VIPUser.objects.count()
            if existing_count >= 100:
                messages.error(request, "VIP 名額已滿（最多100位）")
            else:
                vip_num = str(existing_count + 1).zfill(3)
                code = ''.join(random.choices(string.digits, k=6))
                expires = timezone.now() + timezone.timedelta(minutes=30)
                vip = VIPUser.objects.create(
                    user=request.user,
                    vip_number=vip_num,
                    whatsapp_number=whatsapp,
                    verification_code=code,
                    code_expires_at=expires,
                )
                messages.success(request, f"申請成功！測試驗證碼：{code}（正式版將發送至 WhatsApp）")
                return redirect('vip_verify')

    return render(request, 'core/vip_register.html')


def vip_verify_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        vip = request.user.vip_profile
    except VIPUser.DoesNotExist:
        return redirect('vip_register')

    if vip.is_verified:
        return redirect('vip_dashboard')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if code == vip.verification_code:
            if timezone.now() <= vip.code_expires_at:
                vip.is_verified = True
                vip.verified_at = timezone.now()
                vip.save()
                messages.success(request, f"驗證成功！歡迎，VIP-{vip.vip_number}！")
                return redirect('vip_dashboard')
            else:
                messages.error(request, "驗證碼已過期，請重新申請")
        else:
            messages.error(request, "驗證碼錯誤，請重試")

    return render(request, 'core/vip_verify.html', {'vip': vip})


@login_required(login_url='/login/')
def vip_dashboard_view(request):
    try:
        vip = request.user.vip_profile
    except VIPUser.DoesNotExist:
        return redirect('vip_register')

    user_cases = Case.objects.filter(user=request.user, is_historical=False).order_by('-created_at')
    pending_cases = user_cases.filter(feedback_required=True, feedback_submitted=False)
    can_create, reason = vip.can_create_case()

    context = {
        'vip': vip,
        'user_cases': user_cases,
        'pending_cases': pending_cases,
        'total_cases': user_cases.count(),
        'pending_count': pending_cases.count(),
        'can_create': can_create,
        'cannot_create_reason': reason,
    }
    return render(request, 'core/vip_dashboard.html', context)


@login_required(login_url='/login/')
def ai_analysis_status_view(request, case_id):
    """API: 返回案例 AI 分析狀態（前端輪詢用）"""
    case = get_object_or_404(Case, id=case_id)
    if not case.is_historical and case.user != request.user:
        return JsonResponse({'status': 'error', 'message': '無權限'}, status=403)

    analyzing = case.ai_analysis == '__ANALYZING__'
    return JsonResponse({
        'status': 'analyzing' if analyzing else 'done',
        'content': '' if analyzing else case.ai_analysis,
    })


@login_required(login_url='/login/')
def import_cases_view(request):
    if not request.user.is_staff:
        messages.error(request, "需要管理員權限")
        return redirect('case_list')

    if request.method == 'POST' and request.FILES.get('csv_file'):
        import csv
        import io
        csv_file = request.FILES['csv_file']
        decoded = csv_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded))
        count = 0
        for row in reader:
            try:
                Case.objects.create(
                    title=row.get('求測類型', '未知'),
                    category='career',
                    name=row.get('求測人背景', ''),
                    question=row.get('斷語紀錄', ''),
                    ganzhi=row.get('干支八字', ''),
                    key_config=row.get('關鍵局項', ''),
                    expert_judgment=row.get('斷語紀錄', ''),
                    real_feedback=row.get('事後反饋', ''),
                    source=row.get('資料來源', ''),
                    is_historical=True,
                    ai_analysis='',
                    chart_data={},
                    question_data={},
                )
                count += 1
            except Exception:
                continue
        messages.success(request, f"成功導入 {count} 個歷史案例")
        return redirect('case_list')

    return render(request, 'core/import_cases.html')
