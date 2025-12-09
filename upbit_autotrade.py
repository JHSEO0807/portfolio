# ===============================
# 업비트 실전매매 코드(모의코드 포함)
# Upbit auto trading code
# 2025/11/1
# ===============================


import time
import datetime
import pyupbit
import pandas as pd


# ============= 기본 설정(基本設定＆ログイン) ===============
ACCESS_KEY = "여기에_본인_ACCESS_키_입력"
SECRET_KEY = "여기에_본인_SECRET_키_입력"

TICKER = "KRW-XRP"     # 리플
INTERVAL = "minute5"   # 5분봉
DRY_RUN = True         # 처음에는 꼭 True로 해두고 테스트(模擬売買設定)
CHECK_SECONDS = 60     # 몇 초마다 체크할지 (60초 = 1분)


# =========== 업비트 객체 (실매매 모드에서만 사용)(実践モード) ============
upbit = None
if not DRY_RUN:
    upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)
    print("실매매 모드로 실행합니다.")
else:
    print("DRY_RUN 모드입니다. 실제 주문은 보내지 않습니다.")


# ===== 5분봉 데이터에서 이동평균선 계산하고 골든크로스 / 데드크로스 여부를 알려주는 함수 =====
def get_ma_signal():
    try:
        df = pyupbit.get_ohlcv(TICKER, interval=INTERVAL, count=50)
    except Exception as e:
        print("캔들 조회 중 에러:", e)
        return None

    if df is None:
        print("캔들 데이터를 가져오지 못했습니다.")
        return None

    # 이동평균선 계산
    df["ma6"] = df["close"].rolling(window=6).mean()
    df["ma12"] = df["close"].rolling(window=12).mean()
    df["ma24"] = df["close"].rolling(window=24).mean()
    df["ma48"] = df["close"].rolling(window=48).mean()

    # 직전 봉, 현재 봉
    ma6_prev = df["ma6"].iloc[-2]
    ma12_prev = df["ma12"].iloc[-2]
    ma6_now = df["ma6"].iloc[-1]
    ma12_now = df["ma12"].iloc[-1]

    # NaN이면 아직 계산 안 된 구간이므로 종료
    if pd.isna(ma6_prev) or pd.isna(ma12_prev) or pd.isna(ma6_now) or pd.isna(ma12_now):
        return None

    golden = (ma6_prev < ma12_prev) and (ma6_now > ma12_now)
    dead = (ma6_prev > ma12_prev) and (ma6_now < ma12_now)

    close_now = df["close"].iloc[-1]
    candle_time = df.index[-1]

    result = {
        "golden": golden,
        "dead": dead,
        "close": close_now,
        "time": candle_time
    }
    return result

# ===== 현재 XRP 보유 수량 조회 DRY_RUN 모드일 때는 0으로 처리 =====
def get_balance_xrp():
    if DRY_RUN:
        return 0.0

    try:
        amount = upbit.get_balance("XRP")
        if amount is None:
            return 0.0
        return float(amount)
    except Exception as e:
        print("XRP 잔고 조회 에러:", e)
        return 0.0


# =========== 현재 원화 잔고 조회 ============
def get_balance_krw():
    if DRY_RUN:
        return 0.0

    try:
        krw = upbit.get_balance("KRW")
        if krw is None:
            return 0.0
        return float(krw)
    except Exception as e:
        print("KRW 잔고 조회 에러:", e)
        return 0.0

# ================  매수 함수 ================
def buy_xrp(price):
    now = datetime.datetime.now()
    print("[매수 시도]", now, "현재가:", price)

    if DRY_RUN:
        print("DRY_RUN 모드라서 실제로 매수 주문을 보내지 않습니다.")
        return

    krw = get_balance_krw()
    # 수수료 고려
    order_krw = krw * 0.9

    if order_krw < 5000:
        print("KRW가 너무 적어서 매수하지 않습니다.")
        return

    try:
        upbit.buy_market_order(TICKER, order_krw)
        print("시장가 매수 주문 보냈습니다. 금액:", order_krw)
    except Exception as e:
        print("매수 주문 에러:", e)


# ================ 매도함수 =================
def sell_xrp(price):
    now = datetime.datetime.now()
    print("[매도 시도]", now, "현재가:", price)

    if DRY_RUN:
        print("DRY_RUN 모드라서 실제로 매도 주문을 보내지 않습니다.")
        return

    amount = get_balance_xrp()
    if amount <= 0:
        print("보유한 XRP가 없어서 매도하지 않습니다.")
        return

    try:
        upbit.sell_market_order(TICKER, amount)
        print("시장가 매도 주문 보냈습니다. 수량:", amount)
    except Exception as e:
        print("매도 주문 에러:", e)



# ============= 메인 루프 ================
print("리플 이동평균선 자동매매 시작")


# ========== DRY_RUN 모드일 때는 단순히 변수로 보유 상태 관리 ============
holding_sim = False

while True:
    try:
        signal = get_ma_signal()

        if signal is None:
            print("신호를 계산하지 못했습니다. 다음에 다시 시도합니다.")
        else:
            golden = signal["golden"]
            dead = signal["dead"]
            close_price = signal["close"]
            candle_time = signal["time"]

            print("[체크]", candle_time, "종가:", close_price, "골든:", golden, "데드:", dead)

            if DRY_RUN:
                # 모의매매용 단순 로직(模擬売買ロジック)
                if (not holding_sim) and golden:
                    print("→ DRY_RUN: 골든크로스 발생, 매수했다고 가정")
                    holding_sim = True
                elif holding_sim and dead:
                    print("→ DRY_RUN: 데드크로스 발생, 매도했다고 가정")
                    holding_sim = False
            else:
                # 실제 매매 로직(実践売買ロジック)
                amount_real = get_balance_xrp()

                if amount_real == 0 and golden:
                    print("→ 골든크로스 발생, 실제 매수")
                    buy_xrp(close_price)
                elif amount_real > 0 and dead:
                    print("→ 데드크로스 발생, 실제 매도")
                    sell_xrp(close_price)

        time.sleep(CHECK_SECONDS)

    except KeyboardInterrupt:
        print("사용자에 의해 종료되었습니다.")
        break
    except Exception as e:
        print("메인 루프 에러:", e)
        
        # 잠깐 쉬었다가 재시도
        time.sleep(5)
