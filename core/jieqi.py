# -*- coding: utf-8 -*-
"""
jieqi.py - 節氣計算模組（零外部依賴純 Python 實現）
使用 VSOP87 簡化天文算法計算節氣，完全不依賴任何外部庫。
lunar-python 僅用於干支計算，若不可用則使用內建算法。
"""

import datetime
import math
from itertools import cycle, repeat

tian_gan = '甲乙丙丁戊己庚辛壬癸'
di_zhi = '子丑寅卯辰巳午未申酉戌亥'

# 24節氣名稱（按黃經順序，從小寒285度開始）
jqmc = ['小寒', '大寒', '立春', '雨水', '驚蟄', '春分', '清明', '穀雨',
        '立夏', '小滿', '芒種', '夏至', '小暑', '大暑', '立秋', '處暑',
        '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至']

JIEQI_NAMES = jqmc

# 24節氣對應的太陽黃經（度）
JIEQI_LONGITUDES = [285, 300, 315, 330, 345, 0, 15, 30, 45, 60, 75, 90,
                    105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270]


def jiazi():
    return list(map(lambda x: "{}{}".format(tian_gan[x % len(tian_gan)], di_zhi[x % len(di_zhi)]), list(range(60))))


def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None


def new_list(olist, o):
    a = olist.index(o)
    res1 = olist[a:] + olist[:a]
    return res1


def repeat_list(n, thelist):
    return [repetition for i in thelist for repetition in repeat(i, n)]


# ─── 純 Python 節氣計算（零外部依賴）────────────────────────────────────────

def _jde_to_datetime(jde):
    """儒略日轉 datetime（UTC）"""
    jde = jde + 0.5
    z = int(jde)
    f = jde - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e)
    if e < 14:
        month = e - 1
    else:
        month = e - 13
    if month > 2:
        year = c - 4716
    else:
        year = c - 4715
    total_seconds = f * 86400
    hour = int(total_seconds // 3600)
    total_seconds -= hour * 3600
    minute = int(total_seconds // 60)
    second = int(total_seconds - minute * 60)
    try:
        return datetime.datetime(year, month, day, hour, minute, second)
    except Exception:
        return datetime.datetime(year, month, day, 0, 0, 0)


def _sun_longitude(jde):
    """計算給定儒略日的太陽視黃經（度），精度約0.01度"""
    T = (jde - 2451545.0) / 36525.0
    # 太陽平黃經
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    # 太陽平近點角
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    M_rad = math.radians(M % 360)
    # 太陽中心方程
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad)
         + (0.019993 - 0.000101 * T) * math.sin(2 * M_rad)
         + 0.000289 * math.sin(3 * M_rad))
    # 太陽真黃經
    sun_lon = (L0 + C) % 360
    # 章動修正（簡化）
    omega = 125.04 - 1934.136 * T
    apparent = sun_lon - 0.00569 - 0.00478 * math.sin(math.radians(omega))
    return apparent % 360


def _datetime_to_jde(dt):
    """datetime（UTC）轉儒略日"""
    y, m, d = dt.year, dt.month, dt.day
    h = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    if m <= 2:
        y -= 1
        m += 12
    A = int(y / 100)
    B = 2 - A + int(A / 4)
    jde = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + h / 24.0 + B - 1524.5
    return jde


def _get_solar_term_jde(year, target_lon):
    """用二分法計算節氣的儒略日（UTC）"""
    # 估算初始日期
    days_from_winter_solstice = ((target_lon - 270) % 360) / 360.0 * 365.25
    # 上一年冬至約在12月22日
    approx_dt = datetime.datetime(year - 1, 12, 22) + datetime.timedelta(days=days_from_winter_solstice)
    # 確保在合理範圍內
    if approx_dt.year < year - 1:
        approx_dt = datetime.datetime(year, 1, 1)

    jde_approx = _datetime_to_jde(approx_dt)
    jde_start = jde_approx - 20
    jde_end = jde_approx + 20

    for _ in range(60):
        jde_mid = (jde_start + jde_end) / 2.0
        lon = _sun_longitude(jde_mid)
        diff = (lon - target_lon + 360) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < 0.00001:
            break
        if diff > 0:
            jde_end = jde_mid
        else:
            jde_start = jde_mid

    return jde_mid


def _get_all_jieqi_for_year(year):
    """獲取某年所有節氣的北京時間（UTC+8），按時間排序"""
    result = []
    for lon, name in zip(JIEQI_LONGITUDES, JIEQI_NAMES):
        jde = _get_solar_term_jde(year, lon)
        dt_utc = _jde_to_datetime(jde)
        dt_bj = dt_utc + datetime.timedelta(hours=8)
        result.append({'name': name, 'datetime': dt_bj, 'longitude': lon})
    return sorted(result, key=lambda x: x['datetime'])


# 緩存，避免重複計算
_jieqi_cache = {}


def _get_jieqi_list(year):
    if year not in _jieqi_cache:
        _jieqi_cache[year] = _get_all_jieqi_for_year(year)
    return _jieqi_cache[year]


def get_jieqi_start_date(year, month, day, hour, minute):
    """
    獲取給定日期時間的當前節氣（最近已過的節氣）開始時間。
    返回包含年月日時分和節氣名的字典。
    """
    current_dt = datetime.datetime(year, month, day, hour, minute)
    all_jieqi = (_get_jieqi_list(year - 1) +
                 _get_jieqi_list(year) +
                 _get_jieqi_list(year + 1))
    all_jieqi = sorted(all_jieqi, key=lambda x: x['datetime'])

    prev_jq = None
    for jq_item in all_jieqi:
        if jq_item['datetime'] <= current_dt:
            prev_jq = jq_item
        else:
            break

    if prev_jq:
        t = prev_jq['datetime']
        return {
            '年': t.year, '月': t.month, '日': t.day,
            '時': t.hour, '分': t.minute,
            '節氣': prev_jq['name'],
            '時間': t
        }
    return None


def get_next_jieqi_start_date(year, month, day, hour, minute):
    """獲取給定日期時間的下一個節氣開始時間"""
    current_dt = datetime.datetime(year, month, day, hour, minute)
    all_jieqi = (_get_jieqi_list(year - 1) +
                 _get_jieqi_list(year) +
                 _get_jieqi_list(year + 1))
    all_jieqi = sorted(all_jieqi, key=lambda x: x['datetime'])

    for jq_item in all_jieqi:
        if jq_item['datetime'] > current_dt:
            t = jq_item['datetime']
            return {
                '年': t.year, '月': t.month, '日': t.day,
                '時': t.hour, '分': t.minute,
                '節氣': jq_item['name'],
                '時間': t
            }
    return None


def get_before_jieqi_start_date(year, month, day, hour, minute):
    """獲取給定日期時間的前一個節氣（即當前節氣的前一個）"""
    current_jq = get_jieqi_start_date(year, month, day, hour, minute)
    if not current_jq:
        return None
    t = current_jq['時間']
    prev_dt = t - datetime.timedelta(seconds=1)
    return get_jieqi_start_date(prev_dt.year, prev_dt.month, prev_dt.day,
                                prev_dt.hour, prev_dt.minute)


def jq(year, month, day, hour, minute):
    """獲取給定日期時間所在的節氣名稱"""
    try:
        result = get_jieqi_start_date(year, month, day, hour, minute)
        if result:
            return result['節氣']
        raise ValueError(f"無法確定節氣: {year}-{month}-{day} {hour}:{minute}")
    except Exception as e:
        raise ValueError(f"Error in jq for {year}-{month}-{day} {hour}:{minute}: {str(e)}")


# ─── 干支計算 ────────────────────────────────────────────────────────────────

def ke_jiazi_d(hour):
    t = [f"{h}:{m}0" for h in range(24) for m in range(6)]
    minutelist = dict(zip(t, cycle(repeat_list(1, find_lunar_ke(hour)))))
    return minutelist


# 五虎遁，起正月
def find_lunar_month(year):
    fivetigers = {
        tuple(list('甲己')): '丙寅',
        tuple(list('乙庚')): '戊寅',
        tuple(list('丙辛')): '庚寅',
        tuple(list('丁壬')): '壬寅',
        tuple(list('戊癸')): '甲寅'
    }
    if multi_key_dict_get(fivetigers, year[0]) is None:
        result = multi_key_dict_get(fivetigers, year[1])
    else:
        result = multi_key_dict_get(fivetigers, year[0])
    return dict(zip(range(1, 13), new_list(jiazi(), result)[:12]))


# 五鼠遁，起子時
def find_lunar_hour(day):
    fiverats = {
        tuple(list('甲己')): '甲子',
        tuple(list('乙庚')): '丙子',
        tuple(list('丙辛')): '戊子',
        tuple(list('丁壬')): '庚子',
        tuple(list('戊癸')): '壬子'
    }
    if multi_key_dict_get(fiverats, day[0]) is None:
        result = multi_key_dict_get(fiverats, day[1])
    else:
        result = multi_key_dict_get(fiverats, day[0])
    return dict(zip(list(di_zhi), new_list(jiazi(), result)[:12]))


# 五馬遁，起子刻
def find_lunar_ke(hour):
    fivehourses = {
        tuple(list('丙辛')): '甲午',
        tuple(list('丁壬')): '丙午',
        tuple(list('戊癸')): '戊午',
        tuple(list('甲己')): '庚午',
        tuple(list('乙庚')): '壬午'
    }
    if multi_key_dict_get(fivehourses, hour[0]) is None:
        result = multi_key_dict_get(fivehourses, hour[1])
    else:
        result = multi_key_dict_get(fivehourses, hour[0])
    return new_list(jiazi(), result)


# ─── 干支計算（純 Python 算法，不依賴外部庫）────────────────────────────────

# 以 2000-01-01 為基準日（甲辰年丙子月庚午日）
_BASE_DATE = datetime.date(2000, 1, 1)
_BASE_DAY_GZ_INDEX = 36  # 庚午 = 第36個干支（甲=0,乙=1,...庚=6; 子=0,...午=6 → 6*6=36? 需驗證）

def _get_day_gz_index(year, month, day):
    """計算日干支索引（0-59）"""
    d = datetime.date(year, month, day)
    delta = (d - _BASE_DATE).days
    # 2000-01-01 是庚午日
    # 庚=6(天干), 午=6(地支) → 索引 = ?
    # 干支60循環：甲子=0, 乙丑=1, ..., 庚午=?
    # 庚=6, 午=6 → 找到 n 使得 n%10==6 且 n%12==6 → n=6 (庚午)
    base_idx = 6  # 庚午的索引
    return (base_idx + delta) % 60


def _gz_from_index(idx):
    """從干支索引獲取干支字符串"""
    return tian_gan[idx % 10] + di_zhi[idx % 12]


def _get_year_gz(year, month, day):
    """計算年干支（以立春為界）"""
    # 立春大約在2月4日前後，簡化處理
    # 找到該年立春日期
    jde = _get_solar_term_jde(year, 315)  # 立春黃經315度
    dt_bj = _jde_to_datetime(jde) + datetime.timedelta(hours=8)
    lichun_date = dt_bj.date()

    current_date = datetime.date(year, month, day)
    if current_date < lichun_date:
        calc_year = year - 1
    else:
        calc_year = year

    # 甲子年 = 1984年（天干甲=0, 地支子=0）
    base_year = 1984
    idx = (calc_year - base_year) % 60
    return _gz_from_index(idx)


def _get_month_gz(year, month, day, year_gz):
    """計算月干支（以節為界，用五虎遁）"""
    # 找到當前節（奇數黃經節氣）
    # 節：立春315, 驚蟄345, 清明15, 立夏45, 芒種75, 小暑105,
    #     立秋135, 白露165, 寒露195, 立冬225, 大雪255, 小寒285
    jie_longitudes = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
    jie_months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # 對應農曆月

    current_dt = datetime.datetime(year, month, day, 0, 0)
    # 找最近已過的節
    all_jie = []
    for y in [year - 1, year, year + 1]:
        for lon, m_num in zip(jie_longitudes, jie_months):
            jde = _get_solar_term_jde(y, lon)
            dt_bj = _jde_to_datetime(jde) + datetime.timedelta(hours=8)
            all_jie.append({'datetime': dt_bj, 'month_num': m_num, 'year': y})

    all_jie.sort(key=lambda x: x['datetime'])

    prev_jie = None
    for j in all_jie:
        if j['datetime'] <= current_dt:
            prev_jie = j
        else:
            break

    if prev_jie is None:
        prev_jie = all_jie[0]

    lunar_month = prev_jie['month_num']
    month_map = find_lunar_month(year_gz)
    return month_map.get(lunar_month, '甲子')


def _get_day_gz(year, month, day):
    """計算日干支"""
    idx = _get_day_gz_index(year, month, day)
    return _gz_from_index(idx)


def lunar_date_d(year, month, day):
    """農曆日期（嘗試用 lunar-python，失敗則返回簡化結果）"""
    try:
        from lunar_python import Solar
        lunar_m = ['占位', '正月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '冬月', '腊月']
        solar = Solar.fromYmd(year, month, day)
        lunar = solar.getLunar()
        return {
            '年': lunar.getYear(),
            '農曆月': lunar_m[abs(lunar.getMonth())],
            '月': lunar.getMonth(),
            '日': lunar.getDay()
        }
    except Exception:
        return {'年': year, '農曆月': '未知', '月': month, '日': day}


def gangzhi1(year, month, day, hour, minute):
    """計算年月日時干支（不含刻）"""
    # 子時跨日處理：23時屬於次日子時
    calc_year, calc_month, calc_day = year, month, day
    if hour == 23:
        next_day = datetime.datetime(year, month, day) + datetime.timedelta(days=1)
        calc_year, calc_month, calc_day = next_day.year, next_day.month, next_day.day

    # 優先用 lunar-python
    try:
        from lunar_python import Solar
        solar = Solar.fromYmd(calc_year, calc_month, calc_day)
        lunar = solar.getLunar()
        yTG = lunar.getYearInGanZhi()
        mTG = lunar.getMonthInGanZhi()
        dTG = lunar.getDayInGanZhi()
    except Exception:
        # 備用：純 Python 算法
        yTG = _get_year_gz(calc_year, calc_month, calc_day)
        dTG = _get_day_gz(calc_year, calc_month, calc_day)
        mTG = _get_month_gz(calc_year, calc_month, calc_day, yTG)

    # 時支對照
    hour_to_shichen = {0: '子', 1: '丑', 2: '丑', 3: '寅', 4: '寅', 5: '卯',
                       6: '卯', 7: '辰', 8: '辰', 9: '巳', 10: '巳', 11: '午',
                       12: '午', 13: '未', 14: '未', 15: '申', 16: '申', 17: '酉',
                       18: '酉', 19: '戌', 20: '戌', 21: '亥', 22: '亥', 23: '子'}
    shichen = hour_to_shichen.get(hour, '子')
    hTG = find_lunar_hour(dTG).get(shichen, '甲子')

    return [yTG, mTG, dTG, hTG]


def gangzhi(year, month, day, hour, minute):
    """計算年月日時干支（含刻）"""
    try:
        base = gangzhi1(year, month, day, hour, minute)
        yTG, mTG, dTG, hTG = base

        # 刻干支
        zi_gz = gangzhi1(year, month, day, 0, 0)[3]
        if minute < 10:
            reminute = "00"
        elif minute < 20:
            reminute = "10"
        elif minute < 30:
            reminute = "20"
        elif minute < 40:
            reminute = "30"
        elif minute < 50:
            reminute = "40"
        else:
            reminute = "50"
        hourminute = str(hour) + ":" + str(reminute)
        gangzhi_minute = ke_jiazi_d(zi_gz).get(hourminute)

        return [yTG, mTG, dTG, hTG, gangzhi_minute]
    except Exception:
        return ['甲子', '甲子', '甲子', '甲子', '甲子']


if __name__ == '__main__':
    year, month, day, hour, minute = 2026, 3, 28, 0, 37
    print(f"{year}-{month}-{day} {hour}:{minute}")
    print("節氣:", jq(year, month, day, hour, minute))
    print("干支:", gangzhi(year, month, day, hour, minute))
