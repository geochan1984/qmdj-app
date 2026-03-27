'''
奇門遁甲計算引擎
實現地方真太陽時計算、起局、九宮格生成
'''
import math
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import qimen_ju_name_zhirun, gangzhi
from typing import Dict, Any, Optional

# ============================================================
# 核心定義
# ============================================================
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
QIMEN_LUOYI = ['戊', '己', '庚', '辛', '壬', '癸', '丁', '丙', '乙']
JIUGONG_NAMES = {1: '坎', 2: '坤', 3: '震', 4: '巽', 5: '中', 6: '乾', 7: '兌', 8: '艮', 9: '離'}
LUOSHU_SEQ = [1, 2, 3, 4, 6, 7, 8, 9]
GONG_TO_IDX = {g: i for i, g in enumerate(LUOSHU_SEQ)}
BAMEN_GONG = {1: '休門', 2: '死門', 3: '傷門', 4: '杜門', 6: '開門', 7: '驚門', 8: '生門', 9: '景門'}
JIUXING_GONG = {1: '天蓬', 2: '天芮', 3: '天沖', 4: '天輔', 5: '天禽', 6: '天心', 7: '天柱', 8: '天任', 9: '天英'}
BASHEN = ['值符', '螣蛇', '太陰', '六合', '白虎', '玄武', '九地', '九天']
CITY_DATA = {
    '香港': {'lon': 114.1694, 'lat': 22.3193, 'tz': 8},
    '台北': {'lon': 121.5654, 'lat': 25.0330, 'tz': 8},
    '北京': {'lon': 116.4074, 'lat': 39.9042, 'tz': 8},
    '上海': {'lon': 121.4737, 'lat': 31.2304, 'tz': 8},
    '廣州': {'lon': 113.2644, 'lat': 23.1291, 'tz': 8},
}

# ============================================================
# 時間 & 干支 & 節氣 & 局數 計算
# ============================================================
def equation_of_time(day_of_year: int) -> float:
    B = 360 / 365 * (day_of_year - 81)
    B_rad = math.radians(B)
    return 9.87 * math.sin(2 * B_rad) - 7.53 * math.cos(B_rad) - 1.5 * math.sin(B_rad)

def get_solar_time(dt: datetime, city: str) -> datetime:
    if city not in CITY_DATA:
        return dt
    city_info = CITY_DATA[city]
    lon, tz = city_info['lon'], city_info['tz']
    day_of_year = dt.timetuple().tm_yday
    eot = equation_of_time(day_of_year)
    lon_correction = (lon - tz * 15) * 4
    return dt + timedelta(minutes=lon_correction + eot)

_SOLAR_TERMS_START = [(1, 6), (2, 4), (3, 6), (4, 5), (5, 6), (6, 6), (7, 7), (8, 7), (9, 8), (10, 8), (11, 7), (12, 7)]
_MONTH_DZ_LIST = ['丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子']

def get_ganzhi_year(year: int, month: int, day: int) -> str:
    lichun_m, lichun_d = _SOLAR_TERMS_START[1]
    gz_year = year - 1 if (month < lichun_m) or (month == lichun_m and day < lichun_d) else year
    tg_idx = (gz_year - 4) % 10
    dz_idx = (gz_year - 4) % 12
    return TIANGAN[tg_idx] + DIZHI[dz_idx]

def _get_solar_month_index(month: int, day: int) -> int:
    for i in range(11, -1, -1):
        sm, sd = _SOLAR_TERMS_START[i]
        if (month > sm) or (month == sm and day >= sd):
            return i
    return 11

def get_ganzhi_month(year: int, month: int, day: int) -> str:
    lichun_m, lichun_d = _SOLAR_TERMS_START[1]
    gz_year = year - 1 if (month < lichun_m) or (month == lichun_m and day < lichun_d) else year
    year_tg_idx = (gz_year - 4) % 10
    month_tg_base = ((year_tg_idx % 5) * 2 + 2) % 10
    solar_month_idx = _get_solar_month_index(month, day)
    tg_offset = (solar_month_idx - 1) % 12
    tg_idx = (month_tg_base + tg_offset) % 10
    return TIANGAN[tg_idx] + _MONTH_DZ_LIST[solar_month_idx]

def get_ganzhi_day(year: int, month: int, day: int, hour: int, minute: int) -> str:
    return gangzhi(year, month, day, hour, minute)[2]

def get_shichen(hour: int) -> str:
    return DIZHI[(hour + 1) // 2 % 12]

def get_shigan(year: int, month: int, day: int, hour: int, minute: int) -> str:
    day_gz = get_ganzhi_day(year, month, day, hour, minute)
    day_tg_idx = TIANGAN.index(day_gz[0])
    shichen = get_shichen(hour)
    sc_idx = DIZHI.index(shichen)
    tg_base = (day_tg_idx % 5) * 2
    time_tg_idx = (tg_base + sc_idx) % 10
    return TIANGAN[time_tg_idx] + shichen

def get_ju_number(year: int, month: int, day: int, hour: int, minute: int) -> Dict:
    ju_string = qimen_ju_name_zhirun(year, month, day, hour, minute)
    ju_type = ju_string[0:2]
    chinese_to_int = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    ju_number = chinese_to_int[ju_string[2]]
    return {'ju_type': ju_type, 'ju_number': ju_number}

# ============================================================
# 奇門遁甲核心算法 (Corrected)
# ============================================================
def get_dipan(ju_num: int, ju_type: str) -> Dict[int, str]:
    cnumber_map = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九'}
    gua_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    cnumber = ['一', '二', '三', '四', '五', '六', '七', '八', '九']

    ju_num_char = cnumber_map[ju_num]

    if ju_type == '陽遁':
        tian_gan_sequence = ['戊', '己', '庚', '辛', '壬', '癸', '丁', '丙', '乙']
        start_index = cnumber.index(ju_num_char)
        ordered_cnumber = cnumber[start_index:] + cnumber[:start_index]
    else: # 陰遁
        tian_gan_sequence = ['戊', '乙', '丙', '丁', '癸', '壬', '辛', '庚', '己']
        start_index = cnumber.index(ju_num_char)
        ordered_cnumber = cnumber[start_index::-1] + cnumber[:start_index:-1]

    palace_numbers = [gua_map[c] for c in ordered_cnumber]
    dipan = dict(zip(palace_numbers, tian_gan_sequence))
    return dipan

def get_tianpan(dipan: Dict[int, str], tianpeng_gong: int) -> Dict[int, str]:
    tianpan = {}
    T = GONG_TO_IDX[tianpeng_gong]
    diff_map = {}
    diff_map[LUOSHU_SEQ[T % 8]] = 8
    diff_map[LUOSHU_SEQ[(T + 1) % 8]] = 8
    diff_map[LUOSHU_SEQ[(T - 1 + 8) % 8]] = 3
    diff_map[LUOSHU_SEQ[(T + 2) % 8]] = 3
    diff_map[LUOSHU_SEQ[(T + 3) % 8]] = 6
    diff_map[LUOSHU_SEQ[(T + 6) % 8]] = 6
    diff_map[LUOSHU_SEQ[(T + 4) % 8]] = 1
    diff_map[LUOSHU_SEQ[(T + 5) % 8]] = 1
    for gong in LUOSHU_SEQ:
        di_tg = dipan.get(gong, '')
        if not di_tg: continue
        di_idx = QIMEN_LUOYI.index(di_tg)
        diff = diff_map.get(gong, 0)
        tian_idx = (di_idx + diff) % 9
        tianpan[gong] = QIMEN_LUOYI[tian_idx]
    return tianpan

def get_jiuxing_pan(ju_num: int) -> Dict[int, str]:
    if ju_num == 1: return JIUXING_GONG
    if ju_num == 9: return {1: '天輔', 2: '天蓬', 3: '天芮', 4: '天柱', 5: '天禽', 6: '天沖', 7: '天任', 8: '天英', 9: '天心'}
    return JIUXING_GONG

def get_bashen_pan(tianpeng_gong: int, ju_type: str) -> Dict[int, str]:
    bashen_pan = {}
    palace_order = [1, 8, 3, 4, 9, 2, 7, 6] # 坎, 艮, 震, 巽, 離, 坤, 兌, 乾

    start_idx = palace_order.index(tianpeng_gong)

    if ju_type == '陽遁':
        ordered_palaces = palace_order[start_idx:] + palace_order[:start_idx]
        seq = ['值符', '螣蛇', '太陰', '六合', '勾陳', '朱雀', '九地', '九天']
    else: # 陰遁
        ordered_palaces = [palace_order[start_idx]] + palace_order[:start_idx][::-1] + palace_order[start_idx+1:][::-1]
        seq = ['值符', '螣蛇', '太陰', '六合', '白虎', '玄武', '九地', '九天']

    for i, shen in enumerate(seq):
        gong = ordered_palaces[i]
        bashen_pan[gong] = shen
    return bashen_pan
    return bashen_pan

def generate_jiugong_chart(dt: datetime, city: str = '香港', use_solar_time: bool = True) -> Dict:
    solar_dt = get_solar_time(dt, city) if use_solar_time else dt
    year, month, day, hour, minute = solar_dt.year, solar_dt.month, solar_dt.day, solar_dt.hour, solar_dt.minute
    year_gz = get_ganzhi_year(year, month, day)
    month_gz = get_ganzhi_month(year, month, day)
    day_gz = get_ganzhi_day(year, month, day, hour, minute)
    time_gz = get_shigan(year, month, day, hour, minute)
    ju_info = get_ju_number(year, month, day, hour, minute)
    ju_num, ju_type = ju_info['ju_number'], ju_info['ju_type']
    dipan = get_dipan(ju_num, ju_type)
    time_tg = time_gz[0]
    tianpeng_gong = -1
    for gong, tg in dipan.items():
        if tg == time_tg:
            tianpeng_gong = gong
            break
    if tianpeng_gong == 5: tianpeng_gong = 2
    if tianpeng_gong == -1: tianpeng_gong = ju_num # Fallback
    tianpan = get_tianpan(dipan, tianpeng_gong)
    jiuxing_pan = get_jiuxing_pan(ju_num)
    bashen_pan = get_bashen_pan(tianpeng_gong, ju_type)
    bamen_pan = BAMEN_GONG
    # 計算日干落宮、時干落宮
    day_tg = day_gz[0]
    day_tg_gong = None
    for gong, tg in dipan.items():
        if tg == day_tg:
            day_tg_gong = gong
            break
    if day_tg_gong == 5: day_tg_gong = 2
    time_tg_gong = tianpeng_gong  # 時干落宮即天蓬宮

    palaces = {}
    GONG_POSITION = {4: '西北', 9: '正北', 2: '東北', 3: '正西', 5: '中央', 7: '正東', 8: '西南', 1: '正南', 6: '東南'}
    for gong in range(1, 10):
        palaces[gong] = {
            'gong': gong,
            'gong_name': JIUGONG_NAMES[gong],
            'position': GONG_POSITION.get(gong, ''),
            'dipan_tg': dipan.get(gong, ''),
            'tianpan_tg': tianpan.get(gong, ''),
            'men': bamen_pan.get(gong, ''),
            'xing': jiuxing_pan.get(gong, ''),
            'shen': bashen_pan.get(gong, ''),
        }
    return {
        'ju_type': ju_type, 'ju_number': ju_num, 'palaces': palaces,
        'year_gz': year_gz, 'month_gz': month_gz, 'day_gz': day_gz, 'time_gz': time_gz,
        'day_tg': day_tg, 'day_tg_gong': day_tg_gong,
        'time_tg': time_tg, 'time_tg_gong': time_tg_gong,
        'solar_time': solar_dt.strftime('%Y-%m-%d %H:%M'), 'original_time': dt.strftime('%Y-%m-%d %H:%M'),
        'city': city, 'tianpeng_gong': tianpeng_gong,
        'special_configs': [],
    }


def get_ai_analysis(question_data: Dict, chart_data: Dict, knowledge_context: str = '') -> str:
    """調用 AI 分析奇門遁甲盤面"""
    try:
        from openai import OpenAI
        client = OpenAI()
        palaces = chart_data.get('palaces', {})
        palace_desc = []
        for gong_num in [4, 9, 2, 3, 5, 7, 8, 1, 6]:
            p = palaces.get(gong_num) or palaces.get(str(gong_num), {})
            if p:
                palace_desc.append(
                    f"{p.get('gong_name', '')}宮（{p.get('position', '')}）："
                    f"地盤{p.get('dipan_tg', '')} 天盤{p.get('tianpan_tg', '')} "
                    f"{p.get('men', '')} {p.get('xing', '')} {p.get('shen', '')}"
                )
        special = chart_data.get('special_configs', [])
        special_desc = '、'.join([s['name'] for s in special]) if special else '無特殊格局'
        question = question_data.get('question', '') if isinstance(question_data, dict) else str(question_data)
        category = question_data.get('category', '事業') if isinstance(question_data, dict) else '事業'
        day_tg = chart_data.get('day_tg', chart_data.get('day_gz', '')[:1])
        day_tg_gong = chart_data.get('day_tg_gong', '')
        time_tg = chart_data.get('time_tg', chart_data.get('time_gz', '')[:1])
        time_tg_gong = chart_data.get('time_tg_gong', '')
        gong_names = {1: '坎', 2: '坤', 3: '震', 4: '巽', 5: '中', 6: '乾', 7: '兌', 8: '艮', 9: '離'}
        day_tg_gong_name = gong_names.get(day_tg_gong, str(day_tg_gong))
        time_tg_gong_name = gong_names.get(time_tg_gong, str(time_tg_gong))
        prompt = f"""你是一位精通奇門遁甲的命理師，請根據以下盤面信息進行專業分析。
【問事問題】{question}
【問事類別】{category}
【盤面信息】
- 年月日時干支：{chart_data.get('year_gz', '')}年 {chart_data.get('month_gz', '')}月 {chart_data.get('day_gz', '')}日 {chart_data.get('time_gz', '')}時
- 局型：{chart_data.get('ju_type', '')}{chart_data.get('ju_number', '')}局
- 特殊格局：{special_desc}
- 日干：{day_tg}（落{day_tg_gong_name}宮）
- 時干：{time_tg}（落{time_tg_gong_name}宮）
【九宮格局】
{chr(10).join(palace_desc)}
{f'【參考案例】{knowledge_context}' if knowledge_context else ''}
請提供：
1. **盤面解讀**：分析關鍵宮位、門、星、神的組合含義
2. **核心判斷**：針對問題給出明確的吉凶判斷
3. **時間預測**：預測事情發展的時間節點
4. **建議行動**：給出具體可行的建議
5. **人物關係**：分析相關人物的角色與影響
請用繁體中文回答，語言專業但易懂，約400-500字。"""
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 分析暫時不可用（{str(e)[:50]}）。請根據盤面數據自行分析。"
