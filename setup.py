#!/usr/bin/env python3
"""
初始化腳本：創建管理員帳號和測試 VIP 用戶
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qmdj_project.settings')
sys.path.insert(0, '/home/ubuntu/qmdj_project')
django.setup()

from django.contrib.auth.models import User
from core.models import VIPUser
from django.utils import timezone

# 創建管理員
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@qmdj.test', 'admin123')
    print("✅ 管理員帳號創建：admin / admin123")
else:
    admin = User.objects.get(username='admin')
    print("ℹ️ 管理員帳號已存在")

# 創建測試用戶
if not User.objects.filter(username='test').exists():
    test_user = User.objects.create_user('test', 'test@qmdj.test', 'test123')
    print("✅ 測試帳號創建：test / test123")
else:
    test_user = User.objects.get(username='test')
    print("ℹ️ 測試帳號已存在")

# 創建測試 VIP 用戶
if not VIPUser.objects.filter(user=test_user).exists():
    vip = VIPUser.objects.create(
        user=test_user,
        vip_number='001',
        whatsapp_number='+852 9999 8888',
        is_verified=True,
        verification_code='123456',
        verified_at=timezone.now(),
        code_expires_at=timezone.now() + timezone.timedelta(hours=24),
    )
    print(f"✅ 測試 VIP 用戶創建：VIP-001 (test / test123)")
else:
    print("ℹ️ 測試 VIP 用戶已存在")

print("\n🎉 初始化完成！")
print("   管理員：admin / admin123")
print("   測試VIP：test / test123 (VIP-001，已驗證)")
