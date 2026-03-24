#!/usr/bin/env python3
"""
批量導入奇門遁甲歷史案例 CSV 到數據庫
"""
import os
import sys
import django

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qmdj_project.settings')
sys.path.insert(0, '/home/ubuntu/qmdj_project')
django.setup()

import csv
from core.models import Case

CSV_FILE = '/home/ubuntu/upload/qmdj_business_cases_v1.csv'

def import_cases():
    count = 0
    errors = 0

    with open(CSV_FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # 解析起局時間
                time_str = row.get('起局時間', '').strip()
                manual_time = None
                if time_str:
                    from django.utils.dateparse import parse_datetime
                    manual_time = parse_datetime(time_str.replace(' ', 'T') if 'T' not in time_str else time_str)

                case = Case.objects.create(
                    title=row.get('求測類型', '未知').strip(),
                    category='career',
                    name=row.get('求測人背景', '').strip(),
                    question=row.get('斷語紀錄', '').strip(),
                    manual_time=manual_time,
                    ganzhi=row.get('干支八字', '').strip(),
                    key_config=row.get('關鍵局項', '').strip(),
                    expert_judgment=row.get('斷語紀錄', '').strip(),
                    real_feedback=row.get('事後反饋', '').strip(),
                    source=row.get('資料來源', '').strip(),
                    is_historical=True,
                    ai_analysis='',
                    chart_data={},
                    question_data={'question': row.get('斷語紀錄', ''), 'category': 'career'},
                )
                count += 1
                print(f"  ✅ 導入：{case.title}")
            except Exception as e:
                errors += 1
                print(f"  ❌ 錯誤：{row.get('求測類型', '?')} - {e}")

    print(f"\n完成！成功導入 {count} 個案例，失敗 {errors} 個。")

if __name__ == '__main__':
    print("開始導入歷史案例...")
    import_cases()
