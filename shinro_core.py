"""
終章：3Dプリンター×産業用ロボットで拓く進路探究 ─ データと部品

出どころ：単元案「終章：3Dプリンター×産業用ロボットで拓く進路探究【最新版】」（14コマ＋校外1日）

ねらい（高いところから見た位置づけ）
  終章「これからの科学と人間生活」は、(2)で学んだ内容を踏まえて生徒が課題を設定する単元。
  課題は生徒が決め、教員はテーマ例と職業の事例で「選べる幅」を用意する。
  どのテーマも「変えるもの1つ・そろえるもの・測るもの」が決まる形 ＝ 読解カードの③をそのまま問いにしたもの。

データの種類
  - 導入目標・18分野・事例：単元案が引用する公開資料（2026年時点）。**授業で使う前に最新の資料で確かめる**
  - 特別教育の制度：教員向けの要点。時間数や18歳未満の扱いは、実施前に条文と労働基準監督署で確定する（未確定事項）

Streamlit に依存しない。`python shinro_core.py` で自己チェック。
"""
from __future__ import annotations

import datetime as dt

TARGET_YEAR = 2040
TARGET_UNITS = "1,000万台規模"

# 導入目標の18分野（単元案の表より）
FIELDS_18 = (
    "製造業（多品種少量）", "造船", "物流", "建設・土木", "建築", "インフラ保守", "小売", "宿泊", "飲食・食品製造",
    "医療", "介護", "警備", "農業", "林業", "廃棄物処理", "災害対応", "警察活動", "防衛",
)

LEAD_QUESTION = f"{TARGET_UNITS}が入る{TARGET_YEAR}年、あなたは何歳で、ロボットの“どちら側”にいるか？"
EASY_WORDS = "ロボットは理系だけの話ではない。導入を決める人、安全ルールを作る人、お客さんに説明する人も必要になる。"


def age_in(target_year: int, this_year: int, age_now: int) -> int:
    return age_now + (target_year - this_year)


# 終章の進め方（全体14コマ＋校外1日）：(順, 段階, コマ数, 内容)
FLOW: list[tuple[int, str, str, str]] = [
    (1, "導入実習", "6コマ", "3Dプリンターとロボットに実際に触れ、「問いの種」を集める"),
    (2, "課題設定", "2コマ", "テーマ例と職業の事例から出発し、問い・仮説シート（矢印図・予想グラフ付き）を作る"),
    (3, "研究", "4コマ＋校外1日", "校内実験、または三原西部の圃場・ハウスでの試験"),
    (4, "まとめと発表", "2コマ", "結果を読解カード4項目で整理し、「この科学はどの仕事につながるか」まで発表する"),
]

# 導入実習（6コマ）：(コマ, テーマ, 活動, 対応する(2)の内容, 情報Ⅰ連携, 問いの種の例)
INTRO: list[tuple[int, str, str, str, str, str]] = [
    (1, "3Dプリンターは何をしているか", "実機観察。「溶かす→積む→冷やす」を熱の言葉で説明", "光や熱の科学", "3Dデータ＝座標の列", "なぜ角が反るのか"),
    (2, "材料の科学", "PLA（植物由来）とABSの比較、再利用と分別", "物質の科学", "材料データ表の作成", "失敗作は再利用できるか"),
    (3, "設計して印刷する", "無料CADでFW用の小物を設計（播種間隔ゲージ、温度センサーのケース）", "物質の科学", "モデル化、寸法＝数値の設計", "どの形が一番丈夫か"),
    (4, "ロボットと安全", "労働災害の事例、「隔離・停止・教育」、リスクアセスメント", "これからの科学と人間生活", "リスク＝起こりやすさ×被害", "人とロボットはどこまで近づけるか"),
    (5, "教示＝プログラミング", "小型教育用アーム（定格出力80W以下）で「つかむ→運ぶ→置く」を教示", "光や熱の科学（センサー）", "順次・反復・分岐、DNCL", "教示点を減らすと速くなるか"),
    (6, "AIロボットと人間の仕事", "草刈りの実証事例を読む：なぜ人ではなくロボットか／何がまだ人の仕事か", "宇宙や地球の科学（斜面・気象）", "生成AI・基盤モデルの光と影", "日本の急斜面はどれくらいあるか"),
]

AREAS = ("光や熱の科学", "物質の科学", "生命の科学", "宇宙や地球の科学", "社会・情報との統合")

# 課題研究テーマ例（17テーマ）
#   no, 領域, 問い, 変えるもの, そろえるもの, 測るもの（単位）, 情報Ⅰ連携, 難易度(1〜3), 文系に入りやすいか, つながる職業
THEMES: list[dict] = [
    dict(no=1, area=AREAS[0], q="ノズル温度を上げると、造形物の反りは減るか", change="ノズル温度", control="形状・材料・室温",
         measure="角の浮き（mm）", joho="散布図・相関", level=1, bun=False, jobs="生産技術、品質管理"),
    dict(no=2, area=AREAS[0], q="距離センサーは、物の色や材質で誤検出するか", change="対象物の色・材質", control="距離・角度・照明",
         measure="計測値と実際の差（cm）", joho="計測の誤差、条件分岐", level=2, bun=False, jobs="ロボットSIer、自動運転開発"),
    dict(no=3, area=AREAS[0], q="3Dプリントした通風型ケースで、ハウス内の気温の測り方は変わるか", change="ケースの有無・形",
         control="設置場所・高さ・時刻", measure="気温（℃）の差", joho="時系列グラフ", level=2, bun=False, jobs="スマート農業、気象観測"),
    dict(no=4, area=AREAS[1], q="充填率を上げると、強さはどこまで上がるか（材料量とのつり合い）", change="充填率",
         control="形状・温度・材料ロット", measure="壊れるまでのおもり（g）、材料（g）、時間（分）", joho="散布図、費用対効果", level=1, bun=False,
         jobs="設計者、生産管理"),
    dict(no=5, area=AREAS[1], q="屋外に置いたPLAとPETG、どちらが劣化しにくいか", change="材料", control="形状・設置場所・期間",
         measure="強さ・色の変化", joho="表の作成、比較", level=2, bun=False, jobs="材料開発、農業資材"),
    dict(no=6, area=AREAS[1], q="失敗作を再生したフィラメントで、強さは落ちるか", change="新品か再生品か", control="形状・温度・充填率",
         measure="壊れるまでのおもり（g）", joho="平均とばらつき", level=2, bun=False, jobs="リサイクル、廃棄物処理"),
    dict(no=7, area=AREAS[1], q="植物由来のPLAは、畑の土の中で数か月で変化するか", change="埋めるか否か", control="形状・期間",
         measure="質量の減少（g）", joho="「言えないこと」の記述", level=2, bun=False, jobs="環境コンサル、農業"),
    dict(no=8, area=AREAS[2], q="3Dプリントした播種ゲージで株間をそろえると、麦の生育のばらつきは減るか", change="ゲージの有無",
         control="品種・播種日・圃場の列", measure="草丈（cm）の標準偏差", joho="箱ひげ図", level=2, bun=False, jobs="農業法人、スマート農業"),
    dict(no=9, area=AREAS[2], q="ロボットハンドのつかむ強さと、やわらかい作物の傷みの関係", change="つかむ強さ・指の形",
         control="作物の種類・大きさ", measure="傷の数・落下回数", joho="分岐を含む手順", level=3, bun=False, jobs="収穫ロボット、食品工場"),
    dict(no=10, area=AREAS[2], q="握る力が弱い人向けの自助具（スプーンの柄）を設計すると、どの太さが持ちやすいか", change="柄の太さ・形",
         control="長さ・重さ", measure="持ちやすさの評価（5段階）", joho="アンケートの集計", level=2, bun=True, jobs="介護、作業療法士、福祉用具"),
    dict(no=11, area=AREAS[3], q="斜面の角度を上げると、車輪型と脚型の模型ロボットはどこで転ぶか", change="斜面の角度・移動方式",
         control="重さ・表面の材質", measure="転倒する角度（度）", joho="シミュレーションとの比較", level=3, bun=False, jobs="建設・林業、インフラ保守"),
    dict(no=12, area=AREAS[3], q="地域の標高データで地形模型を3Dプリントすると、地図より土砂災害の危険箇所を見つけやすいか",
         change="模型か地図か", control="対象地域・問題文", measure="正答率（%）・回答時間（秒）", joho="公開データの利用", level=2, bun=True,
         jobs="防災・自治体、測量"),
    dict(no=13, area=AREAS[4], q="教示点の数を減らすと、動作時間と置く位置の正確さはどう変わるか", change="教示点の数", control="速度・対象物",
         measure="時間（秒）・位置のずれ（mm）", joho="アルゴリズム、DNCL", level=2, bun=False, jobs="ロボットSIer、生産技術"),
    dict(no=14, area=AREAS[4], q="圃場の作業を時間計測すると、ロボットに任せるべき工程はどこか", change="工程（播種・草刈り・運搬など）",
         control="作業者・面積", measure="時間（分）・危険度・費用", joho="表計算、意思決定", level=1, bun=True, jobs="農業経営、導入コンサル"),
    dict(no=15, area=AREAS[4], q="広島県で人手不足が大きいのは18分野のうちどこか", change="分野", control="統計の年・指標",
         measure="有効求人倍率など（公開統計）", joho="データの活用（第4問型）", level=1, bun=True, jobs="行政、政策、人事"),
    dict(no=16, area=AREAS[4], q="生成AIが作ったロボットの安全手順書に、人が点検してどれだけ誤りが見つかるか", change="点検の有無・チェックリスト",
         control="作業内容・生成条件", measure="誤りの件数", joho="生成AIの特性、情報モラル", level=2, bun=True, jobs="品質保証、安全管理"),
    dict(no=17, area=AREAS[4], q="ネットにつながるロボットに、どんな情報セキュリティ対策が必要か（守る側の調査）", change="接続の方式",
         control="対象機種", measure="対策の有無（チェック表）", joho="情報セキュリティ", level=2, bun=True, jobs="サイバーセキュリティ"),
]
FW_DIRECT = (3, 8, 14)   # 2年FW（三原西部の圃場）と直結するテーマ

# テーマごとの注意（実施前に必ず読む）
THEME_NOTES = {
    7: "「変化が見えなかった」結果になりやすい。そのとき「何か月なら言えるか」を書ければ成功として評価する。",
    10: "試す人は生徒自身に限る（握る力を弱める手袋で再現）。高齢者や患者に試してもらう場合は、施設の許可と同意を先に取る。",
    12: "人を対象にする研究。参加は任意とし、名前を記録しない。",
    16: "人を対象にする研究。参加は任意とし、名前を記録しない。",
    17: "調べるだけで、攻撃の再現はしない。実機を使う場合は、学校のICT担当の許可を取る。",
}


def filter_themes(areas: list[str] | None = None, max_level: int = 3, bun_only: bool = False,
                  fw_only: bool = False) -> list[dict]:
    out = []
    for t in THEMES:
        if areas and t["area"] not in areas:
            continue
        if t["level"] > max_level or (bun_only and not t["bun"]) or (fw_only and t["no"] not in FW_DIRECT):
            continue
        out.append(t)
    return out


def stars(level: int) -> str:
    return "★" * level


# ロボットとの6つの関わり方：(立ち位置, 仕事の例, 文系にも開かれた入口, 関係する学び, 対応テーマ)
ROLES: list[tuple[str, str, str, str, tuple[int, ...]]] = [
    ("使う", "工場・物流・農業のオペレーター", "産業用ロボット特別教育", "安全・手順", (8, 9)),
    ("つくる", "ロボットメーカー、3D設計", "情報系・工学系への進学", "数学・物理・情報Ⅰ", (1, 4, 5, 6)),
    ("つなぐ", "ロボットSIer（現場に合わせて組み込む）", "営業・提案・プロジェクト管理", "課題を言葉にする力", (2, 13)),
    ("直す", "保守・点検（検査等の特別教育）", "現場経験から上る道", "安全・論理", (3, 11)),
    ("決める", "導入判断、自治体・農協、政策", "商学・経済・法学", "費用対効果、資料読解", (12, 14, 15)),
    ("守る", "安全基準、サイバーセキュリティ", "法学・情報", "情報Ⅰ（セキュリティ）", (10, 16, 17)),
]


def role_of(theme_no: int) -> str | None:
    return next((r[0] for r in ROLES if theme_no in r[4]), None)


# 進路ワーク（1枚）
CAREER_ITEMS = ("① 今いちばん困っていること", "② ロボットで解決できること", "③ 人に残る仕事", "④ 自分がなれる立ち位置")


def career_sheet(field: str, role: str, rows: dict[str, str], weak: list[str]) -> str:
    """進路ワークをテキストにする（ダウンロード用。サーバーには残さない）。根拠の弱い項目には「言えない」の印"""
    lines = ["進路ワーク：2040年、ロボットのどちら側にいるか", f"選んだ分野：{field}", f"立ち位置：{role}", ""]
    for item in CAREER_ITEMS:
        mark = "　［言えない＝根拠が弱い］" if item in weak else ""
        lines.append(f"{item}：{rows.get(item) or '（未記入）'}{mark}")
    lines += ["", "※ 根拠の弱い主張には「言えない」の印を付け、次に何を調べれば言えるようになるかを書く。"]
    return "\n".join(lines)


# 導入第4コマ：リスク＝起こりやすさ×被害（情報Ⅰ連携）
LIKELIHOOD = {1: "ほとんど起きない", 2: "ときどき起きる", 3: "よく起きる"}
SEVERITY = {1: "かすり傷", 2: "通院するけが", 3: "重いけが・後遺症"}
RISK_ACTIONS = ("隔離（人とロボットを離す・囲う）", "停止（止めてから近づく・非常停止）", "教育（手順を学んでから扱う）")


def risk(likelihood: int, severity: int) -> tuple[int, str]:
    """リスクの点数と判定。3×3 の表（説明用の区分）"""
    if likelihood not in LIKELIHOOD or severity not in SEVERITY:
        raise ValueError("1〜3 で入力")
    s = likelihood * severity
    return s, ("高い：このままでは作業しない。対策してから" if s >= 6 else "中くらい：対策を決めて、守れているか確かめる"
               if s >= 3 else "低い：手順どおりに作業する")


# 職業につながる科学の事例：(事例, 何をしているか, 使われている科学, 関わる仕事, 対応テーマ)
CASES: list[tuple[str, str, str, str, tuple[int, ...]]] = [
    ("四足歩行ロボットによる急斜面の草刈り実証（長野県の実証事業）",
     "四足歩行ロボットに3Dプリントしたアームと刈刃を付け、急斜面の草刈りを実証。目的は転落・熱中症のリスクを減らすこと",
     "重心と転倒、材料の強さ、自律移動", "農林業・インフラ保守、ロボット開発、自治体の実証事業担当", (4, 11, 14)),
    ("四足歩行ロボットによる除草剤の自律散布（大学発ベンチャーとメーカー）", "太陽光パネル周辺などに除草剤を自律散布",
     "センサーと空間認識、AI", "フィジカルAI開発、設備の保守", (2, 16)),
    ("ロボットSIerによる高校での特別授業", "工科高校で、生徒が溶接ロボットの遠隔操作を体験。特別教育修了証を交付する研修も実施",
     "教示（プログラム）、遠隔操作、熱", "ロボットSIer、溶接オペレーター", (13,)),
    ("メーカーによる工業高校への産業用ロボット寄贈", "マイスター・ハイスクール事業で産業用ロボットを寄贈し、社員が授業も支援",
     "制御ロジック、軌道制御", "ロボットメーカーの技術者・営業", ()),
    ("工科高校のロボティクスコース", "コース卒業者に「産業用ロボット安全特別教育（教示）」修了証を発行", "安全の科学、法令", "ロボットを扱う製造業全般", ()),
]

# 産業用ロボット特別教育の活用（3段階）：(段階, 対象, 内容, 修了証)
TRAINING: list[tuple[str, str, str, str]] = [
    ("① 全員", "全生徒", "導入第4・5コマで、特別教育の学科内容に準拠した安全・法令学習", "なし（「準拠」と明示し、資格と誤解させない）"),
    ("② 希望者", "製造・物流・農業・SIerを進路に考える生徒", "外部機関で正式受講（長期休業中）", "あり"),
    ("③ 進路接続", "受講者", "修了証と終章の研究報告書を、進路書類・面接の具体的なエピソードにする", "―"),
]
TRAINING_NOTES = (
    "校内実習は、定格出力80W以下の教育用アームに限る（80W以下でもリスクアセスメントは必要）",
    "正式な修了証は、規程どおりの科目・時間を満たした場合のみ。時間数は実施前に規程の条文で確定する",
    "18歳未満の生徒が教示等の業務に当たるかは、条文と労働基準監督署で確認する（未確定事項）",
)

SAFETY = (
    "3Dプリンター：ノズル・ヒーターのやけど、加熱した樹脂の臭い・微粒子 → 換気し、稼働中はその場を離れない",
    "造形しないもの：銃器とその部品、刃物、危険物の容器。生徒の3Dデータは造形前に教員が確認する",
    "ロボット：校内は80W以下の教育用アームに限る。可動範囲の表示、非常停止の確認、2人1組を守る",
    "事例との線引き：刈刃のような危険な部品の取り付けは扱わない。「なぜ危険か」「なぜ人を斜面から外したいのか」を考えるところまで",
    "校外実習：圃場では人力・低速の補助具のみ。熱中症・転落対策は通常のFWの基準に従う",
    "人を対象にする研究（No.10・12・16）：参加は任意とし、名前を記録しない。校外の人には先に同意を取る",
)

FIRST_STEP = "テーマNo.4（充填率と強さ）を1コマで試し、理科基礎の対照実験や情報Ⅰ第4問の散布図と同じ考え方で解けるかを確かめる。"


# ─────────────────────────────────────────────
# 学びの実例：作成者が受講中の「Physical AI講座 2026」（基礎編 → 応用編1 → 応用編2）
#   大人も同じ問い（2040年、ロボットのどちら側にいるか）に、学びながら答えを探している、という実例。
#   載せるのは日程表の見出し（題と日付）だけ。講義の中身（スライド・動画・課題）は載せない。
#   「立ち位置」「高校での入口」は作成者の見立て（講座の公式な分類ではない）。
# ─────────────────────────────────────────────
COURSE_NAME = "Physical AI講座 2026"
COURSE_YEAR = 2026
#   編: (ひとことで, 高校の言葉で言うと)
COURSE_PARTS: dict[str, tuple[str, str]] = {
    "基礎編": ("ロボットがどう学ぶか（全7回＋最終課題）", "AIが手本やごほうびから上達するしくみ"),
    "応用編1": ("学んだAIを現場で動かし続けるしくみ（全6回）", "つくった後の、運用・通信・共同開発"),
    "応用編2": ("ロボットの体を数式で表す（第5回まで確認）", "座標・運動・力 ─ 物理基礎と数学の出番"),
}
#   (編, 回, (月, 日), 題, 立ち位置, 高校での入口)
LECTURES: list[tuple[str, int, tuple[int, int], str, tuple[str, ...], str]] = [
    ("基礎編", 1, (6, 25), "Physical AIの概要", ("決める",), "導入第6コマ：AIロボットと人間の仕事"),
    ("基礎編", 2, (7, 2), "Physical AIの活用", ("決める", "つなぐ"), "18分野・職業の事例を読解カードで読む"),
    ("基礎編", 3, (7, 9), "Physical AIの学習（模倣学習）", ("つくる",), "導入第5コマ：教示（手本を見せて覚えさせる）"),
    ("基礎編", 4, (7, 16), "Physical AIの学習（強化学習）", ("つくる",), "予想 → ずれ（δ）で直す。『次の一手』の探索と活用"),
    ("基礎編", 5, (7, 23), "スケーリングとアーキテクチャ", ("つくる",), "情報Ⅰ：モデル化、データの量と計算"),
    ("基礎編", 6, (7, 30), "実世界データの収集", ("使う", "つなぐ"), "圃場での記録（軸・単位・そろえるもの）。テーマNo.14"),
    ("基礎編", 7, (8, 6), "Physical AIの実運用", ("直す", "守る"), "導入第4コマ：リスク＝起こりやすさ×被害"),
    ("応用編1", 1, (9, 3), "MLOps・RobOps導入", ("直す",), "つくった後に、動かし続ける・直し続ける仕事がある"),
    ("応用編1", 2, (9, 10), "MLOps・RobOps実践", ("直す",), "課題研究の『ふり返る』矢印（記録して、直す）"),
    ("応用編1", 3, (9, 17), "コンピュータアーキテクチャ（メモリ・通信・仮想化・デバイスの管理）", ("つくる",), "情報Ⅰ：コンピュータのしくみ・ネットワーク"),
    ("応用編1", 4, (9, 24), "ROS2入門(1/2)", ("つなぐ",), "導入第4コマの発展：ROS 2 のシミュレータ"),
    ("応用編1", 5, (10, 1), "ROS2入門(2/2)", ("つなぐ",), "テーマNo.13：教示点の数と、時間・正確さ"),
    ("応用編1", 6, (10, 8), "Open Source in Robotics", ("つなぐ", "守る"), "情報Ⅰ：著作権・ライセンス。課題研究の引用"),
    ("応用編2", 1, (11, 12), "イントロダクション（ロボティクス分野の全体）", ("決める",), "6つの関わり方の全体地図"),
    ("応用編2", 2, (11, 19), "空間の記述と変換（ロボットの位置・姿勢、座標系）", ("つくる",), "導入第1コマ：3Dデータ＝座標の列"),
    ("応用編2", 3, (11, 26), "運動学（力を考えないロボット運動の記述と計算）", ("つくる",), "物理基礎：速度・変位。テーマNo.13"),
    ("応用編2", 4, (12, 3), "動力学（力・トルクを考えたロボット運動の記述と解析）", ("つくる",), "物理基礎：運動方程式。テーマNo.11（斜面と転倒）"),
    ("応用編2", 5, (12, 10), "ロボット制御（目標とする運動を実現する制御手法）", ("つくる", "使う"), "テーマNo.9：つかむ強さと作物の傷み"),
]
COURSE_NOTES = (
    "載せているのは日程表の見出し（題と日付）だけ。講座サイトの画面・講義のスライド・動画・課題の中身は載せない",
    "『立ち位置』と『高校での入口』は作成者の見立てで、講座の公式な分類ではない",
    "応用編2は確認できた第5回までを載せた。日程は変わることがある",
)


def lecture_status(month: int, day: int, today: dt.date) -> str:
    """講義日が今日より前なら『済』、今日以降なら『これから』（その中でいちばん早いものは next_lecture で『次回』にする）"""
    return "済" if dt.date(COURSE_YEAR, month, day) < today else "これから"


def next_lecture(today: dt.date) -> tuple | None:
    """今日以降でいちばん早い講義（全部終わっていれば None）"""
    return next((x for x in LECTURES if dt.date(COURSE_YEAR, *x[2]) >= today), None)


def lectures_of(part: str, today: dt.date) -> list[dict]:
    nxt = next_lecture(today)
    return [{"回": f"第{n}回", "日付": f"{m}/{d}", "題": title, "立ち位置（見立て）": "・".join(roles), "高校での入口": door,
             "状況": "次回" if nxt and (p, n) == (nxt[0], nxt[1]) else lecture_status(m, d, today)}
            for p, n, (m, d), title, roles, door in LECTURES if p == part]


def role_coverage() -> dict[str, int]:
    """6つの立ち位置それぞれに、講義が何回分あたるか（1回が2つの立ち位置にあたることもある）。偏りを見るための数"""
    count = {r[0]: 0 for r in ROLES}
    for *_x, roles, _door in LECTURES:
        for r in roles:
            count[r] += 1
    return count


def coverage_comment() -> str:
    """偏りを言葉にする：多い立ち位置と、少ない立ち位置（＝別の学びで補うところ）"""
    c = role_coverage()
    top, low = max(c.values()), min(c.values())
    many = "・".join(k for k, v in c.items() if v == top)
    few = "・".join(k for k, v in c.items() if v == low)
    return f"この講座でいちばん厚いのは『{many}』（{top}回分）、うすいのは『{few}』（{low}回分）。うすい所は、別の学びや経験で補う。"


def _self_check() -> None:
    assert len(FIELDS_18) == 18 == len(set(FIELDS_18))
    assert [t["no"] for t in THEMES] == list(range(1, 18))
    assert all(t["area"] in AREAS and 1 <= t["level"] <= 3 for t in THEMES)
    covered = sorted(n for r in ROLES for n in r[4])
    assert covered == [n for n in range(1, 18) if n != 7]      # 単元案の表のとおり（No.7 は立ち位置が未割り当て）
    assert role_of(7) is None
    assert len(ROLES) == 6 and role_of(17) == "守る" and role_of(14) == "決める"
    assert {t["no"] for t in filter_themes(bun_only=True)} == {10, 12, 14, 15, 16, 17}
    assert [t["no"] for t in filter_themes(fw_only=True)] == list(FW_DIRECT)
    assert all(t["level"] <= 2 for t in filter_themes(max_level=2)) and len(filter_themes(max_level=2)) == 15
    assert age_in(2040, 2026, 16) == 30
    assert risk(3, 3)[0] == 9 and risk(1, 1)[1].startswith("低い") and risk(2, 3)[1].startswith("高い")
    sheet = career_sheet("農業", "決める", {CAREER_ITEMS[0]: "草刈り"}, [CAREER_ITEMS[1]])
    assert "（未記入）" in sheet and "言えない" in sheet and "草刈り" in sheet
    assert all(set(c[4]) <= set(range(1, 18)) for c in CASES)
    assert sum(1 for _ in INTRO) == 6 and len(FLOW) == 4 and set(THEME_NOTES) <= set(range(1, 18))
    # 学びの実例（Physical AI講座）
    names = {r[0] for r in ROLES}
    assert len(LECTURES) == 18 and {x[0] for x in LECTURES} == set(COURSE_PARTS) and all(set(x[4]) <= names and x[4] for x in LECTURES)
    assert [sum(1 for x in LECTURES if x[0] == p) for p in COURSE_PARTS] == [7, 6, 5]
    dates = [dt.date(COURSE_YEAR, *x[2]) for x in LECTURES]
    assert dates == sorted(dates) and all(d.weekday() == 3 for d in dates)                 # 日付順・すべて木曜
    day = dt.date(2026, 11, 11)
    assert next_lecture(day)[:2] == ("応用編2", 1) and next_lecture(dt.date(2026, 12, 11)) is None
    assert [r["状況"] for r in lectures_of("応用編2", day)] == ["次回", "これから", "これから", "これから", "これから"]
    assert {r["状況"] for r in lectures_of("基礎編", day)} == {"済"} and lecture_status(11, 12, dt.date(2026, 11, 12)) == "これから"
    cov = role_coverage()
    assert sum(cov.values()) == sum(len(x[4]) for x in LECTURES) and max(cov, key=cov.get) == "つくる" and all(v > 0 for v in cov.values())
    assert "つくる" in coverage_comment() and len(COURSE_NOTES) == 3


if __name__ == "__main__":
    _self_check()
    print("shinro_core: 自己チェックOK")
