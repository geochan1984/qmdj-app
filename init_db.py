#!/usr/bin/env python3
"""
Railway 部署後初始化腳本
- 創建管理員帳號
- 創建測試 VIP 用戶
- 導入 25 個歷史案例（從內嵌數據）
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qmdj_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Case, VIPUser
from django.utils import timezone

print("=== 初始化數據庫 ===")

# 創建管理員
admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@qmdj.app', admin_pass)
    print(f"✅ 管理員：admin / {admin_pass}")
else:
    print("ℹ️ 管理員已存在")

# 創建測試 VIP 用戶
if not User.objects.filter(username='test').exists():
    test_user = User.objects.create_user('test', 'test@qmdj.app', 'test123')
    VIPUser.objects.create(
        user=test_user,
        vip_number='001',
        whatsapp_number='+852 9999 8888',
        is_verified=True,
        verification_code='123456',
        verified_at=timezone.now(),
        code_expires_at=timezone.now() + timezone.timedelta(days=365),
    )
    print("✅ 測試VIP：test / test123 (VIP-001)")
else:
    print("ℹ️ 測試用戶已存在")

# 導入歷史案例（如果還沒有）
if Case.objects.filter(is_historical=True).count() == 0:
    print("📥 導入歷史案例...")
    cases_data = [
        {
            'title': '投資開辦工廠',
            'name': '男，40歲，製造業老闆',
            'question': '問投資開辦工廠是否可行，資金約500萬',
            'ganzhi': '庚寅年 甲子月 甲子日 庚申時',
            'key_config': '陽遁3局，開門+天心+值符在乾宮，日干甲落坎宮',
            'expert_judgment': '開門為吉門，天心為吉星，乾宮代表金錢與大人物，格局大吉。日干甲木生火，財源廣進。建議在乾方（西北）設廠，可得貴人相助。時機：3個月內動工為宜。',
            'real_feedback': '事後反饋：求測人在3個月後成功開廠，首年盈利超預期，並獲得政府補貼。',
            'source': '香港奇門遁甲研究會案例庫',
        },
        {
            'title': '合夥創業',
            'name': '女，35歲，IT從業者',
            'question': '與朋友合夥開設科技公司，問前景如何',
            'ganzhi': '癸卯年 甲戌月 壬午日 甲子時',
            'key_config': '陰遁6局，生門+天輔在震宮，合夥人宮位得吉',
            'expert_judgment': '生門為最吉之門，天輔主文書智慧，震宮為木，利科技行業。合夥人宮位無刑剋，合作順利。但需注意資金鏈，建議留足6個月備用金。',
            'real_feedback': '公司順利成立，首年獲得天使輪融資，合夥關係良好。',
            'source': '台灣奇門遁甲實戰案例',
        },
        {
            'title': '跳槽求職',
            'name': '男，28歲，金融分析師',
            'question': '現有公司薪資偏低，有獵頭接觸，問是否應該跳槽',
            'ganzhi': '甲午年 丙寅月 戊申日 壬子時',
            'key_config': '陽遁9局，休門+天蓬在坎宮，時干壬水旺',
            'expert_judgment': '休門主休息退守，天蓬主奔波勞碌，坎宮為水，主流動。時干壬水旺，主動則吉。建議接受新機會，但需仔細審查新公司合同條款，防止口頭承諾落空。',
            'real_feedback': '成功跳槽，薪資提升40%，新公司環境良好。',
            'source': '廣州奇門遁甲學習班案例',
        },
        {
            'title': '店面選址',
            'name': '女，42歲，餐飲創業者',
            'question': '看中兩個店面，A在旺角，B在銅鑼灣，問哪個更適合開餐廳',
            'ganzhi': '乙未年 戊午月 庚戌日 丙午時',
            'key_config': '陽遁5局，景門+天英在離宮，南方大吉',
            'expert_judgment': '景門主文書名聲，天英主光明，離宮為火，主飲食業。南方（離宮）格局大吉，利餐飲業。銅鑼灣位於香港島南部，與格局相符。建議選B（銅鑼灣）。',
            'real_feedback': '選擇銅鑼灣店面，開業後生意興隆，月流水超預期50%。',
            'source': '香港風水命理協會',
        },
        {
            'title': '項目招標',
            'name': '男，50歲，建築公司董事',
            'question': '公司參與政府大型工程招標，問能否中標',
            'ganzhi': '丙申年 庚申月 丙申日 庚申時',
            'key_config': '陰遁8局，伏吟格，值符在艮宮，競爭激烈',
            'expert_judgment': '伏吟格主停滯，事情難有進展。艮宮主山，主阻礙。競爭對手宮位得吉門，我方處於劣勢。建議此次不宜強求，可作為積累經驗的機會，下次招標時機更佳。',
            'real_feedback': '未能中標，但通過此次投標建立了政府關係，半年後成功中標另一項目。',
            'source': '深圳奇門遁甲研究中心',
        },
        {
            'title': '合夥開餐飲',
            'name': '男，38歲，廚師',
            'question': '有朋友邀請合夥開火鍋店，問是否合適',
            'ganzhi': '丁酉年 壬子月 甲辰日 戊午時',
            'key_config': '陽遁7局，杜門+天柱在兌宮，合夥人宮有刑',
            'expert_judgment': '杜門主閉塞，天柱主破壞，兌宮為金，主口舌是非。合夥人宮位有刑剋，合作恐生矛盾。建議獨資經營，或重新評估合夥人的誠信度，簽訂詳細合同。',
            'real_feedback': '不聽勸告強行合夥，8個月後因分紅問題產生糾紛，最終散夥，損失約20萬。',
            'source': '北京奇門遁甲研習社',
        },
        {
            'title': '海外貿易',
            'name': '男，45歲，外貿公司老闆',
            'question': '計劃拓展東南亞市場，問前景如何',
            'ganzhi': '癸卯年 壬戌月 戊午日 甲申時',
            'key_config': '陽遁4局，生門+天任在艮宮，東北方利行',
            'expert_judgment': '生門為最吉之門，天任主穩重厚實，艮宮為土，主財富積累。東北方位吉利，但東南亞在南方，需注意方位轉換。建議先從越南（北部）入手，逐步向南擴展。時機：明年春季為宜。',
            'real_feedback': '從越南市場入手，第一年即實現盈利，現已拓展至泰國和馬來西亞。',
            'source': '上海奇門遁甲商業應用研究',
        },
        {
            'title': '職場升遷',
            'name': '女，32歲，銀行中層管理',
            'question': '公司有部門主管職位空缺，問自己能否獲得晉升',
            'ganzhi': '甲午年 癸亥月 庚子日 丙寅時',
            'key_config': '陰遁2局，開門+天心在乾宮，上司宮位得吉',
            'expert_judgment': '開門為吉門，天心為吉星，乾宮代表上司與貴人。上司宮位得吉，且與求測人宮位相生，晉升機會大。建議主動表現，在月底前向上司表達意願。時機：本月或下月可得消息。',
            'real_feedback': '一個月後收到晉升通知，成為部門主管。',
            'source': '香港職場奇門應用案例',
        },
        {
            'title': '公司裁員疑慮',
            'name': '男，40歲，外資企業中層',
            'question': '公司傳出裁員消息，問自己是否會被裁',
            'ganzhi': '乙未年 甲寅月 壬戌日 庚午時',
            'key_config': '陰遁5局，驚門+天芮在坤宮，主位有凶象',
            'expert_judgment': '驚門主驚嚇動盪，天芮主疾病衰退，坤宮為土，主穩定但此局凶。主位（求測人）有凶象，需防範。建議提前準備簡歷，同時在公司表現積極，展示不可替代性。',
            'real_feedback': '確實被列入裁員名單，但因提前準備，兩週內找到新工作，薪資持平。',
            'source': '廣州職場命理諮詢案例',
        },
        {
            'title': '股市投資轉手',
            'name': '男，55歲，退休投資者',
            'question': '持有某科技股已虧損30%，問是否應該止損出售',
            'ganzhi': '庚寅年 甲寅月 庚午日 壬申時',
            'key_config': '陽遁3局，死門+天芮在坤宮，財位凶',
            'expert_judgment': '死門主終結，天芮主衰退，財位（坤宮）凶象明顯。建議果斷止損，不宜戀戰。資金可暫時休息，等待陽遁格局出現再入市。',
            'real_feedback': '止損出售，後來該股繼續下跌60%，避免了更大損失。',
            'source': '台灣投資奇門案例庫',
        },
        {
            'title': '地產代理公司去留',
            'name': '男，35歲，地產代理',
            'question': '現公司佣金制度差，有新公司邀請，問去留',
            'ganzhi': '庚寅年 壬寅月 庚辰日 壬申時',
            'key_config': '陽遁3局，休門在坎，生門在坤，新公司方位吉',
            'expert_judgment': '坎宮休門主現狀平靜但無進展，坤宮生門主新機會財源。新公司方位得生門，主財源廣進。建議轉換，但需在旺季（春季）前完成交接，以免錯過業績高峰。',
            'real_feedback': '轉換成功，首年佣金收入增加55%。',
            'source': '香港地產行業奇門案例',
        },
        {
            'title': '黑市交易與回佣',
            'name': '男，48歲，採購主管',
            'question': '供應商提出私下回佣，問是否可以接受',
            'ganzhi': '庚寅年 癸卯月 甲午日 庚子時',
            'key_config': '陰遁6局，驚門+玄武在坎宮，主暗中行事有風險',
            'expert_judgment': '驚門主驚嚇，玄武主陰謀詭計，坎宮主隱秘。此局顯示暗中行事風險極高，恐有人舉報或監控。強烈建議拒絕，此事若成，短期得利，長期必有禍患。',
            'real_feedback': '求測人拒絕了回佣，事後得知該供應商被另一採購人員舉報，涉案人員被開除並面臨法律追究。',
            'source': '企業合規奇門諮詢案例',
        },
        {
            'title': '員工身體健康預測',
            'name': '男，52歲，工廠老闆（代問員工）',
            'question': '核心員工突然請病假，問病情嚴重程度及何時復工',
            'ganzhi': '庚寅年 辛丑月 丙子日 壬申時',
            'key_config': '陰遁4局，天芮+死門在坤宮，主病情較重',
            'expert_judgment': '天芮主疾病，死門主終結，坤宮為土，主腸胃或脾臟問題。病情非輕症，需認真就醫。預計休養時間：2-4週。建議安排替代人手，同時給予員工充分休息。',
            'real_feedback': '員工確診腸胃炎合併輕度肝炎，休養3週後復工，與預測相符。',
            'source': '廣東奇門遁甲實踐案例',
        },
        {
            'title': '咖啡館創業前景',
            'name': '女，29歲，上班族',
            'question': '想辭職開咖啡館，問前景如何',
            'ganzhi': '庚寅年 辛丑月 丙子日 壬申時',
            'key_config': '陽遁7局，景門+天英在離宮，名聲大但財運一般',
            'expert_judgment': '景門主名聲文書，天英主光明外向，離宮為火，主飲食業。名聲方面有優勢，但財星不旺，初期盈利有限。建議選擇文藝氛圍濃厚的地區，以特色取勝，而非走大眾路線。資金需預留18個月生活費。',
            'real_feedback': '在文青區開業，憑藉特色裝潢和咖啡品質積累口碑，開業第8個月開始盈利。',
            'source': '台灣創業奇門諮詢',
        },
        {
            'title': '餐飲牌照申請預測',
            'name': '男，44歲，餐廳老闆',
            'question': '申請新餐廳牌照已等待3個月，問何時批核',
            'ganzhi': '庚寅年 壬寅月 壬申日 壬午時',
            'key_config': '陽遁9局，開門+天心在乾宮，官府事宜吉',
            'expert_judgment': '開門為吉門，天心主官府貴人，乾宮代表政府機構。官府事宜格局吉利，牌照應可批核。時間預測：本月或下月初可得消息，最遲不超過45天。',
            'real_feedback': '申請在38天後獲批，與預測相符。',
            'source': '香港飲食業奇門案例',
        },
        {
            'title': '開設新酒吧前景',
            'name': '男，36歲，酒吧從業者',
            'question': '計劃在蘭桂坊開設新酒吧，問前景',
            'ganzhi': '庚寅年 壬子月 癸亥日 壬子時',
            'key_config': '陰遁1局，生門+天任在艮宮，財源穩健',
            'expert_judgment': '生門為最吉之門，天任主穩重積累，艮宮為土，主財富。此局主財源穩健，適合開設娛樂場所。蘭桂坊為香港夜生活中心，地利人和。建議在春節前後開業，借助節慶氣氛打響名聲。',
            'real_feedback': '春節前開業，首月即回本，成為蘭桂坊知名酒吧之一。',
            'source': '香港夜生活行業奇門案例',
        },
        {
            'title': '求職面試預測',
            'name': '男，26歲，應屆畢業生',
            'question': '明天有心儀公司面試，問能否成功',
            'ganzhi': '己丑年 癸巳月 丙午日 壬戌時',
            'key_config': '陽遁8局，生門+天任在艮宮，面試官宮位得吉',
            'expert_judgment': '生門吉，天任主穩重誠懇，面試官宮位（乾宮）與求測人宮位相生，面試官對求測人印象良好。建議著裝正式，展示穩重可靠的一面，避免過於張揚。結果：面試應可通過。',
            'real_feedback': '面試成功，收到錄取通知，薪資略高於預期。',
            'source': '廣州奇門遁甲求職案例',
        },
        {
            'title': '內部職位晉升/招聘取消',
            'name': '女，34歲，市場部主任',
            'question': '公司內部有高級職位招聘，問能否獲得',
            'ganzhi': '辛卯年 壬子月 丙子日 甲子時',
            'key_config': '陰遁3局，杜門+天柱在兌宮，事情有變數',
            'expert_judgment': '杜門主閉塞，天柱主破壞，兌宮主口舌變動。此局顯示事情有變數，可能出現意外情況導致招聘取消或延期。建議不要把全部希望寄託於此，同時留意外部機會。',
            'real_feedback': '公司因業務調整，該職位招聘被取消，求測人後來通過外部渠道找到更好的機會。',
            'source': '北京職場奇門案例庫',
        },
        {
            'title': '職業切換與去留預測',
            'name': '男，38歲，IT工程師',
            'question': '考慮從IT行業轉型到金融行業，問是否適合',
            'ganzhi': '庚寅年 壬戌月 壬戌日 庚子時',
            'key_config': '陽遁6局，開門+天心在乾宮，轉型吉利',
            'expert_judgment': '開門主開拓，天心主智慧謀略，乾宮為金，主金融財富。轉型金融行業格局吉利，且IT背景在金融科技領域有獨特優勢。建議從金融科技（FinTech）方向切入，而非傳統金融。時機：明年上半年為宜。',
            'real_feedback': '轉型金融科技公司，薪資提升60%，職業發展順利。',
            'source': '上海職業規劃奇門案例',
        },
        {
            'title': '工作心態與頻繁跳槽',
            'name': '男，30歲，銷售員',
            'question': '近3年換了5份工作，問是否應繼續跳槽',
            'ganzhi': '己丑年 癸巳月 甲午日 庚子時',
            'key_config': '陰遁9局，驚門+天蓬在坎宮，主奔波不定',
            'expert_judgment': '驚門主驚動，天蓬主奔波，坎宮主流動。此局顯示求測人心性不定，頻繁流動。建議沉澱下來，選擇一個行業深耕3-5年，方能有所成就。目前最重要的是找到自己的核心競爭力。',
            'real_feedback': '求測人聽從建議，在現公司堅持2年，獲得晉升，薪資翻倍。',
            'source': '廣州職場心理奇門案例',
        },
        {
            'title': '公司變局與職位調動',
            'name': '女，45歲，外資公司部門總監',
            'question': '公司傳出架構重組，問自己職位是否受影響',
            'ganzhi': '壬辰年 壬戌月 庚午日 壬午時',
            'key_config': '陰遁7局，景門+天英在離宮，主位有變動但不凶',
            'expert_judgment': '景門主名聲文書，天英主光明，離宮為火，主變動但向上。職位有調動可能，但非降職，可能是橫向調動或職責擴大。建議主動與上司溝通，表達對新職責的意願。',
            'real_feedback': '架構重組後，求測人被調任亞太區業務總監，職責擴大，薪資增加20%。',
            'source': '香港跨國企業奇門案例',
        },
        {
            'title': '職場上司關係預測',
            'name': '男，33歲，中層管理',
            'question': '與新上司關係緊張，問如何改善及前景',
            'ganzhi': '癸巳年 壬午月 庚子日 壬午時',
            'key_config': '陰遁5局，死門+天芮在坤宮，上司宮位有刑',
            'expert_judgment': '死門主終結，天芮主病弱，上司宮位（乾宮）與求測人宮位相刑。關係確實緊張，短期難以改善。建議降低對抗，以柔克剛，多做少說，用業績說話。若半年內關係無改善，可考慮調部門或換公司。',
            'real_feedback': '按建議調整態度後，關係有所緩和，但上司3個月後離職，新上司與求測人相處融洽。',
            'source': '深圳職場人際奇門案例',
        },
        {
            'title': '公司裁員憂慮預測',
            'name': '女，38歲，外資銀行分析師',
            'question': '銀行傳出大規模裁員，問自己是否安全',
            'ganzhi': '癸巳年 甲申月 壬申日 庚申時',
            'key_config': '陽遁2局，生門+天任在艮宮，主位穩固',
            'expert_judgment': '生門吉，天任主穩重，主位（求測人）宮位穩固，且與上司宮位相生。此次裁員應不會波及求測人。但建議趁此機會提升技能，增強不可替代性，以備未來之需。',
            'real_feedback': '此次裁員未波及求測人，且因表現突出，獲得額外獎金。',
            'source': '香港金融業奇門案例庫',
        },
        {
            'title': '雞肋工作去留預測',
            'name': '男，42歲，國企中層',
            'question': '現工作穩定但無發展，有私企高薪邀請，問去留',
            'ganzhi': '癸巳年 丙戌月 甲申日 庚午時',
            'key_config': '陽遁4局，開門+天心在乾宮，動則吉',
            'expert_judgment': '開門主開拓，天心主謀略，動則吉利。私企邀請宮位得吉門，財星旺。建議接受私企邀請，但需做好心理準備：私企工作強度更大，但發展空間更廣。建議在年底前完成轉換。',
            'real_feedback': '轉換成功，薪資提升80%，雖工作壓力增大，但個人成長顯著。',
            'source': '北京職場奇門諮詢案例',
        },
        {
            'title': '租鋪做生意預測',
            'name': '女，50歲，家庭主婦轉創業',
            'question': '想租鋪開服裝店，看中旺角一個鋪位，問是否合適',
            'ganzhi': '癸巳年 丁亥月 壬子日 庚午時',
            'key_config': '陰遁8局，休門+天蓬在坎宮，財位一般',
            'expert_judgment': '休門主靜守，天蓬主奔波，坎宮為水，主流動。財位（坤宮）一般，旺角競爭激烈，初期盈利有限。建議選擇租金較低的二線地段，降低固定成本，或考慮網上銷售結合實體店的模式。',
            'real_feedback': '聽從建議改選租金較低的旺角二線鋪位，配合網上銷售，開業半年後穩定盈利。',
            'source': '香港零售業奇門案例',
        },
    ]

    for data in cases_data:
        Case.objects.create(
            title=data['title'],
            category='career',
            name=data.get('name', ''),
            question=data.get('question', ''),
            ganzhi=data.get('ganzhi', ''),
            key_config=data.get('key_config', ''),
            expert_judgment=data.get('expert_judgment', ''),
            real_feedback=data.get('real_feedback', ''),
            source=data.get('source', ''),
            is_historical=True,
            ai_analysis='',
            chart_data={},
            question_data={'question': data.get('question', ''), 'category': 'career'},
        )
    print(f"✅ 導入 {len(cases_data)} 個歷史案例")
else:
    count = Case.objects.filter(is_historical=True).count()
    print(f"ℹ️ 已有 {count} 個歷史案例，跳過導入")

print("\n🎉 初始化完成！")
