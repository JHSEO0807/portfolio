# ==================
# 업비트 백테스트 코드
# ==================

import pyupbit
import pandas as pd


# 기본 설정
ticker = "KRW-XRP"      # 리플 원화 마켓
interval = "minute5"    # 5분봉
start_money = 1000000   # 초기 자본 100만원


# 캔들 갯수 계산
candles_per_day = int(60 / 5 * 24)
days = 7
need_count = candles_per_day * days + 10  # 여유분

print("데이터 가져오는 중...")


# 데이터 가져오기
df = pyupbit.get_ohlcv(ticker, interval=interval, count=need_count)

if df is None:
    print("데이터를 가져오지 못했습니다.")
    quit()

df = df.dropna()


# 이동평균선 계산
df["ma6"] = df["close"].rolling(window=6).mean()
df["ma12"] = df["close"].rolling(window=12).mean()
df["ma24"] = df["close"].rolling(window=24).mean()
df["ma48"] = df["close"].rolling(window=48).mean()

# 백테스트 변수들
holding = False         # 현재 보유 여부
buy_price = 0.0         # 매수 가격
balance = start_money   # 현재 자본
trade_list = []         # 거래 기록 저장용

prev_ma6 = None
prev_ma12 = None

# ===== 메인 루프 =====
for i in range(len(df)):
    row = df.iloc[i]

    ma6 = row["ma6"]
    ma12 = row["ma12"]

    # 이동평균 값이 아직 없는 구간은 건너뜀
    if pd.isna(ma6) or pd.isna(ma12):
        prev_ma6 = ma6
        prev_ma12 = ma12
        continue

    # 이전 값이 없으면 그냥 저장만
    if prev_ma6 is None or prev_ma12 is None:
        prev_ma6 = ma6
        prev_ma12 = ma12
        continue

    close_price = row["close"]
    time_index = df.index[i]

    # ----- 골든크로스 → 매수 -----
    if (not holding) and (prev_ma6 < prev_ma12) and (ma6 > ma12):
        holding = True
        buy_price = close_price
        print("[매수]", time_index, "가격:", close_price)

    # ----- 데드크로스 → 매도 -----
    elif holding and (prev_ma6 > prev_ma12) and (ma6 < ma12):
        holding = False
        sell_price = close_price
        profit_rate = (sell_price - buy_price) / buy_price
        balance = balance * (1 + profit_rate)

        trade_info = {
            "time": time_index,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "profit_rate": profit_rate
        }
        trade_list.append(trade_info)

        print("[매도]", time_index, "가격:", sell_price, "수익률:", profit_rate * 100, "%")

    # 다음 루프를 위해 이전 값 저장
    prev_ma6 = ma6
    prev_ma12 = ma12

# 마지막 캔들에서 아직 보유 중이면 정리
if holding:
    last_close = df["close"].iloc[-1]
    last_time = df.index[-1]
    profit_rate = (last_close - buy_price) / buy_price
    balance = balance * (1 + profit_rate)

    trade_info = {
        "time": last_time,
        "buy_price": buy_price,
        "sell_price": last_close,
        "profit_rate": profit_rate
    }
    trade_list.append(trade_info)

    print("[최종 청산]", last_time, "가격:", last_close, "수익률:", profit_rate * 100, "%")

# 결과 출력
print()
print("====== 백테스트 결과 ======")
print("초기 자본:", start_money, "원")
print("최종 자본:", balance, "원")
print("총 거래 횟수(매도 기준):", len(trade_list), "회")

if len(trade_list) > 0:
    total_profit_rate = (balance - start_money) / start_money * 100
    sum_profit = 0
    for t in trade_list:
        sum_profit += t["profit_rate"]
    avg_profit_rate = (sum_profit / len(trade_list)) * 100

    print("총 수익률:", total_profit_rate, "%")
    print("평균 거래당 수익률:", avg_profit_rate, "%")
else:
    print("매매가 한 번도 발생하지 않았습니다.")
