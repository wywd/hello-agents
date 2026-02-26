import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

# Binance API
BASE_URL = "https://api.binance.com/api/v3/klines"
SPINNER = "正在加载比特币价格数据……请稍等"
REFRESH_INTERVAL = 60  # 防止频繁刷新操作（秒）

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        try:
            return st.experimental_rerun()
        except TypeError:
            pass
    st.session_state["_rerun_toggle"] = not st.session_state.get("_rerun_toggle", False)

@st.cache_data(ttl=300)  # 缓存 5 分钟
def fetch_bitcoin_data():
    """从 Binance 获取过去 24 小时的 1 分钟 K 线数据"""
    try:
        params = {
            "symbol": "BTCUSDT",
            "interval": "1m",
            "limit": 1440  # 24小时 * 60分钟
        }

        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data or not isinstance(data, list):
            return None, "无有效价格数据（API 数据结构错误）"

        # 提取 [timestamp, close_price]
        prices = [[item[0], float(item[4])] for item in data]

        return prices, None

    except requests.exceptions.RequestException as e:
        return None, str(e)

def plot_price_trend(prices):
    """绘制比特币价格曲线图"""
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["price"],
            mode="lines",
            name="价格趋势"
        )
    )

    fig.update_layout(
        title="比特币价格变化趋势（过去24小时）",
        xaxis_title="时间",
        yaxis_title="价格（USDT）",
        template="plotly_white"
    )

    return fig

def main():
    st.title("比特币价格实时显示")
    st.caption("数据来源于 Binance API (更新间隔：5 分钟)")

    with st.spinner(SPINNER):
        prices, error = fetch_bitcoin_data()

    if error:
        st.error(f"无法加载数据：{error}")
        return

    if prices:
        current_price = prices[-1][1]
        start_price = prices[0][1]

        if start_price > 0:
            change = current_price - start_price
            change_pct = (change / start_price) * 100

            st.metric(
                "当前比特币价格",
                f"${current_price:,.2f}",
                f"{change:,.2f} ({change_pct:.2f}%)"
            )
        else:
            st.warning("起始价格为 0，无法计算涨跌幅。")

        st.plotly_chart(plot_price_trend(prices), use_container_width=True)

    if st.button("刷新价格"):
        safe_rerun()

if __name__ == "__main__":
    main()