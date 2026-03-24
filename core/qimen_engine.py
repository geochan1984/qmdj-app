"""
奇門遁甲計算引擎
實現地方真太陽時計算、起局、九宮格生成
"""
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


# ============================================================
# 城市經緯度數據（用於地方真太陽時計算）
# ============================================================
CITY_DATA = {
    '香港': {'lon': 114.1694, 'lat': 22.3193, 'tz': 8},
    '台北': {'lon': 121.5654, 'lat': 25.0330, 'tz': 8},
    '北京': {'lon': 116.4074, 'lat': 39.9042, 'tz': 8},
    '上海': {'lon': 121.4737, 'lat': 31.2304, 'tz': 8},
    '廣州': {'lon': 113.2644, 'lat': 23.1291, 'tz': 8},
    '深圳': {'lon': 114.0579, 'lat': 22.5431, 'tz': 8},
    '成都': {'lon': 104.0665, 'lat': 30.5728, 'tz': 8},
    '武漢': {'lon': 114.3054, 'lat': 30.5928, 'tz': 8},
    '西安': {'lon': 108.9402, 'lat': 34.3416, 'tz': 8},
    '澳門': {'lon': 113.5439, 'lat': 22.1987, 'tz': 8},
    '新加坡': {'lon': 103.8198, 'lat': 1.3521, 'tz': 8},
    '吉隆坡': {'lon': 101.6869, 'lat': 3.1390, 'tz': 8},
    '東京': {'lon': 139.6917, 'lat': 35.6895, 'tz': 9},
    '首爾': {'lon': 126.9780, 'lat': 37.5665, 'tz': 9},
    '曼谷': {'lon': 100.5018, 'lat': 13.7563, 'tz': 7},
}


def equation_of_time(day_of_year: int) -> float:
    """計算時差（均時差），單位：分鐘"""
    B = 360 / 365 * (day_of_year - 81)
    B_rad = math.radians(B)
    eot = 9.87 * math.sin(2 * B_rad) - 7.53 * math.cos(B_rad) - 1.5 * math.sin(B_rad)
    return eot


def get_solar_time(dt: datetime, city: str) -> datetime:
    """計算地方真太陽時"""
    if city not in CITY_DATA:
        return dt
    city_info = CITY_DATA[city]
    lon = city_info['lon']
    tz = city_info['tz']
    day_of_year = dt.timetuple().tm_yday
    eot = equation_of_time(day_of_year)
    lon_correction = (lon - tz * 15) * 4  # 每度4分鐘
    total_correction = lon_correction + eot
    solar_dt = dt + timedelta(minutes=total_correction)
    return solar_dt


# ============================================================
# 干支系統
# ============================================================
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

JIUGONG_NAMES = {
    1: '坎', 2: '坤', 3: '震', 4: '巽',
    5: '中', 6: '乾', 7: '兌', 8: '艮', 9: '離'
}

# 九宮洛書方位（宮號 -> 位置描述）
JIUGONG_POSITIONS = {
    4: '東南', 9: '正南', 2: '西南',
    3: '正東', 5: '中央', 7: '正西',
    8: '東北', 1: '正北', 6: '西北'
}

# 八門
BAMEN = ['休', '生', '傷', '杜', '景', '死', '驚', '開']

# 九星
JIUXING = ['天蓬', '天芮', '天沖', '天輔', '天禽', '天心', '天柱', '天任', '天英']

# 八神
BASHEN = ['值符', '螣蛇', '太陰', '六合', '白虎', '玄武', '九地', '九天']

# 五行
WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水',
    '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
    '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金',
    '戌': '土', '亥': '水',
}

# 宮位五行
GONG_WUXING = {
    1: '水', 2: '土', 3: '木', 4: '木',
    5: '土', 6: '金', 7: '金', 8: '土', 9: '火'
}


def get_ganzhi_year(year: int) -> str:
    """獲取年干支"""
    tg_idx = (year - 4) % 10
    dz_idx = (year - 4) % 12
    return TIANGAN[tg_idx] + DIZHI[dz_idx]


def get_ganzhi_month(year: int, month: int) -> str:
    """獲取月干支（簡化版）"""
    month_dz = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
    year_tg_idx = (year - 4) % 10
    month_tg_base = (year_tg_idx % 5) * 2
    tg_idx = (month_tg_base + month - 1) % 10
    dz = month_dz[month - 1]
    return TIANGAN[tg_idx] + dz


def get_ganzhi_day(year: int, month: int, day: int) -> str:
    """獲取日干支"""
    import datetime as dt_module
    base = dt_module.date(1900, 1, 1)
    target = dt_module.date(year, month, day)
    days = (target - base).days
    tg_idx = (days + 0) % 10
    dz_idx = (days + 0) % 12
    return TIANGAN[tg_idx] + DIZHI[dz_idx]


def get_shichen(hour: int) -> str:
    """獲取時辰"""
    shichen_map = {
        23: '子', 0: '子', 1: '丑', 2: '丑', 3: '寅', 4: '寅',
        5: '卯', 6: '卯', 7: '辰', 8: '辰', 9: '巳', 10: '巳',
        11: '午', 12: '午', 13: '未', 14: '未', 15: '申', 16: '申',
        17: '酉', 18: '酉', 19: '戌', 20: '戌', 21: '亥', 22: '亥'
    }
    return shichen_map.get(hour, '子')


def get_shigan(year: int, month: int, day: int, hour: int) -> str:
    """獲取時干"""
    day_gz = get_ganzhi_day(year, month, day)
    day_tg = day_gz[0]
    day_tg_idx = TIANGAN.index(day_tg)
    shichen_order = {
        '子': 0, '丑': 1, '寅': 2, '卯': 3, '辰': 4, '巳': 5,
        '午': 6, '未': 7, '申': 8, '酉': 9, '戌': 10, '亥': 11
    }
    shichen = get_shichen(hour)
    sc_idx = shichen_order[shichen]
    tg_base = (day_tg_idx % 5) * 2
    time_tg_idx = (tg_base + sc_idx) % 10
    return TIANGAN[time_tg_idx] + shichen


# ============================================================
# 奇門遁甲起局
# ============================================================

def get_ju_number(year: int, month: int, day: int, hour: int) -> Dict:
    """
    計算局數（簡化版陰陽遁）
    返回：局數(1-9)、陰遁/陽遁、值符宮位等
    """
    # 根據月份判斷陰陽遁
    # 冬至後為陽遁（11-4月），夏至後為陰遁（5-10月）
    if month in [11, 12, 1, 2, 3, 4]:
        ju_type = '陽遁'
    else:
        ju_type = '陰遁'

    # 簡化局數計算（基於日時干支）
    day_gz = get_ganzhi_day(year, month, day)
    day_tg_idx = TIANGAN.index(day_gz[0])
    shichen = get_shichen(hour)
    shichen_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    sc_idx = shichen_order.index(shichen)

    # 計算局數 1-9
    ju_num = ((day_tg_idx * 2 + sc_idx) % 9) + 1

    return {
        'ju_type': ju_type,
        'ju_number': ju_num,
    }


def generate_jiugong_chart(dt: datetime, city: str = '香港', use_solar_time: bool = True) -> Dict:
    """
    生成九宮格盤面數據
    """
    # 使用地方真太陽時
    if use_solar_time and city in CITY_DATA:
        solar_dt = get_solar_time(dt, city)
    else:
        solar_dt = dt

    year = solar_dt.year
    month = solar_dt.month
    day = solar_dt.day
    hour = solar_dt.hour

    # 干支
    year_gz = get_ganzhi_year(year)
    month_gz = get_ganzhi_month(year, month)
    day_gz = get_ganzhi_day(year, month, day)
    time_gz = get_shigan(year, month, day, hour)
    shichen = get_shichen(hour)

    # 局數
    ju_info = get_ju_number(year, month, day, hour)
    ju_type = ju_info['ju_type']
    ju_num = ju_info['ju_number']

    # 生成九宮格（每宮包含：門、星、神、天干）
    # 值符宮位（根據局數）
    zhifu_gong = ju_num  # 簡化：值符在局數對應宮位

    # 八門排布（從值符宮順時針/逆時針）
    # 洛書九宮順序：1坎、2坤、3震、4巽、5中、6乾、7兌、8艮、9離
    luoshu_order = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # 陽遁順布，陰遁逆布
    if ju_type == '陽遁':
        rotation_order = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    else:
        rotation_order = [9, 8, 7, 6, 5, 4, 3, 2, 1]

    # 計算各宮的門、星、神
    palaces = {}
    for i, gong in enumerate(luoshu_order):
        # 計算偏移
        offset = (gong - zhifu_gong) % 9
        if ju_type == '陰遁':
            offset = (zhifu_gong - gong) % 9

        # 八門（跳過5中宮）
        men_idx = offset % 8
        xing_idx = offset % 9
        shen_idx = offset % 8

        palaces[gong] = {
            'gong': gong,
            'gong_name': JIUGONG_NAMES[gong],
            'position': JIUGONG_POSITIONS[gong],
            'men': BAMEN[men_idx],
            'xing': JIUXING[xing_idx],
            'shen': BASHEN[shen_idx],
            'wuxing': GONG_WUXING[gong],
            'is_zhifu': gong == zhifu_gong,
        }

    # 特殊格局檢測
    special_configs = detect_special_configs(palaces, ju_type, ju_num)

    # 日干落宮
    day_tg = day_gz[0]
    day_tg_gong = get_tiangan_gong(day_tg, ju_num, ju_type)

    # 時干落宮
    time_tg = time_gz[0]
    time_tg_gong = get_tiangan_gong(time_tg, ju_num, ju_type)

    return {
        'year_gz': year_gz,
        'month_gz': month_gz,
        'day_gz': day_gz,
        'time_gz': time_gz,
        'shichen': shichen,
        'ju_type': ju_type,
        'ju_number': ju_num,
        'zhifu_gong': zhifu_gong,
        'palaces': palaces,
        'special_configs': special_configs,
        'day_tg': day_tg,
        'day_tg_gong': day_tg_gong,
        'time_tg': time_tg,
        'time_tg_gong': time_tg_gong,
        'solar_time': solar_dt.strftime('%Y-%m-%d %H:%M'),
        'original_time': dt.strftime('%Y-%m-%d %H:%M'),
        'city': city,
    }


def get_tiangan_gong(tg: str, ju_num: int, ju_type: str) -> int:
    """獲取天干落宮（簡化版）"""
    tg_idx = TIANGAN.index(tg) if tg in TIANGAN else 0
    if ju_type == '陽遁':
        gong = ((tg_idx + ju_num - 1) % 9) + 1
    else:
        gong = ((ju_num - tg_idx - 1) % 9) + 1
    if gong == 0:
        gong = 9
    return gong


def detect_special_configs(palaces: Dict, ju_type: str, ju_num: int) -> list:
    """檢測特殊格局"""
    configs = []

    # 伏吟：值符宮位與局數相同（簡化判斷）
    if ju_num in [1, 5, 9]:
        configs.append({
            'name': '伏吟',
            'description': '主停滯不前，事情不了了之',
            'severity': 'warning'
        })

    # 反吟：局數與宮位相對（簡化）
    if ju_num in [2, 8] or ju_num in [3, 7] or ju_num in [4, 6]:
        configs.append({
            'name': '反吟',
            'description': '主反覆波折，難以持久',
            'severity': 'danger'
        })

    # 空亡檢測（示例）
    if ju_num in [6, 7]:
        configs.append({
            'name': '空亡',
            'description': '主計畫落空，名存實亡',
            'severity': 'danger'
        })

    return configs


def get_ai_analysis(question_data: Dict, chart_data: Dict, knowledge_context: str = '') -> str:
    """
    調用 AI 分析奇門遁甲盤面
    """
    try:
        from openai import OpenAI
        import os

        client = OpenAI()

        # 構建盤面描述
        palaces = chart_data.get('palaces', {})
        palace_desc = []
        for gong_num in [4, 9, 2, 3, 5, 7, 8, 1, 6]:
            if str(gong_num) in palaces or gong_num in palaces:
                p = palaces.get(gong_num) or palaces.get(str(gong_num), {})
                palace_desc.append(
                    f"{p.get('position', '')}（{p.get('gong_name', '')}宮）：{p.get('men', '')}門 {p.get('xing', '')} {p.get('shen', '')}"
                )

        special = chart_data.get('special_configs', [])
        special_desc = '、'.join([s['name'] for s in special]) if special else '無特殊格局'

        question = question_data.get('question', '') if isinstance(question_data, dict) else str(question_data)
        category = question_data.get('category', '事業') if isinstance(question_data, dict) else '事業'

        prompt = f"""你是一位精通奇門遁甲的命理師，請根據以下盤面信息進行專業分析。

【問事問題】{question}
【問事類別】{category}

【盤面信息】
- 年月日時干支：{chart_data.get('year_gz', '')}年 {chart_data.get('month_gz', '')}月 {chart_data.get('day_gz', '')}日 {chart_data.get('time_gz', '')}時
- 局型：{chart_data.get('ju_type', '')} {chart_data.get('ju_number', '')}局
- 特殊格局：{special_desc}
- 日干：{chart_data.get('day_tg', '')}（落{chart_data.get('day_tg_gong', '')}宮）
- 時干：{chart_data.get('time_tg', '')}（落{chart_data.get('time_tg_gong', '')}宮）

【九宮格局】
{chr(10).join(palace_desc)}

{f'【參考案例】{knowledge_context}' if knowledge_context else ''}

請提供：
1. **盤面解讀**：分析關鍵宮位、門、星、神的組合含義
2. **核心判斷**：針對問題給出明確的吉凶判斷
3. **時間預測**：預測事情發展的時間節點
4. **建議行動**：給出具體可行的建議

請用繁體中文回答，語言專業但易懂，約300-400字。"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"AI 分析暫時不可用（{str(e)[:50]}）。請根據盤面數據自行分析。"
