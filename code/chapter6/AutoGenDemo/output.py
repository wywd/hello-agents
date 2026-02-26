import streamlit as st
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 配置 API URL 和参数
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
API_PARAMS = {
    "ids": "bitcoin",
    "vs_currencies": "usd",
    "include_24hr_change": "true"
}

# ...existing code...
def safe_rerun():
    # 优先使用旧版/常用的 API
    if hasattr(st, "experimental_rerun"):
        try:
            return st.experimental_rerun()
        except TypeError:
            # 某些版本可能改变签名，退回到 session_state 切换
            pass
    # 避免直接抛出 RerunException（不同版本签名不同），使用 session_state 切换触发重跑
    st.session_state["_rerun_toggle"] = not st.session_state.get("_rerun_toggle", False)

# 定义获取比特币数据的函数（包含重试机制）
@st.cache_data(ttl=10)  # 缓存60秒
def fetch_bitcoin_data_with_retries(retries=3, delay=2):
    """
    引入重试机制的比特币实时数据获取函数。
    :param retries: 最大重试次数
    :param delay: 每次重试间隔时间（秒）
    :return: 包含比特币价格和涨跌信息的字典，或失败时返回None
    """
    for attempt in range(retries):
        try:
            response = requests.get(COINGECKO_API_URL, params=API_PARAMS, timeout=10)
            response.raise_for_status()  # 检查HTTP状态码
            
            # 校验数据结构
            if "bitcoin" in response.json():
                data = response.json()
                price = data["bitcoin"]["usd"]
                change_24h = data["bitcoin"]["usd_24h_change"]
                return {"price": price, "change_24h": change_24h}
        except requests.exceptions.Timeout:
            st.warning(f"请求超时，重试中 ({attempt + 1}/{retries})...")
        except requests.exceptions.HTTPError:
            st.warning(f"服务器响应错误，重试中 ({attempt + 1}/{retries})...")
        except Exception as e:
            st.error(f"未知错误: {e}")
        time.sleep(delay)  # 等待一段时间后重试
    
    st.error("无法获取数据，请稍后再试。")
    return None

# 设置 Streamlit 页面配置
st.set_page_config(
    page_title="Bitcoin价格监控",
    page_icon="💰",
    layout="centered"
)

# 应用标题
st.title("💰 比特币价格实时监控")

# 侧边栏配置
st.sidebar.title("额外设置")
refresh_interval = st.sidebar.slider("自动刷新间隔 (秒)", min_value=10, max_value=60, value=30)
st.sidebar.markdown("数据来源: [CoinGecko API](https://www.coingecko.com)")
st.sidebar.markdown("---")

# 获取数据
with st.spinner("加载数据中..."):
    data = fetch_bitcoin_data_with_retries()

if data:
    # 提取数据
    current_price = data["price"]
    change_24h = data["change_24h"]
    change_amount = current_price * change_24h / 100  # 计算涨跌金额

    # 涨跌颜色指示
    change_color = "green" if change_24h >= 0 else "red"

    # 显示比特币数据
    st.metric(
        label="当前价格 (USD)", 
        value=f"${current_price:,.2f}",
        delta=f"${change_amount:,.2f} ({change_24h:.2f}%)",
        delta_color="normal" if change_24h == 0 else ("inverse" if change_24h < 0 else "off"),
    )
    
    # 更新时间显示
    st.caption(f"数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 手动刷新按钮
if st.button("🔄 刷新数据"):
    safe_rerun()

# 自动刷新功能（兼容处理）
try:
    if hasattr(st, "autorefresh"):
        st.autorefresh(interval=refresh_interval * 1000, key="auto_refresh")
    else:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=refresh_interval * 1000, key="auto_refresh")
except Exception:
    # 若以上都不可用，保持安全降级（不抛错）
    pass

# 底部说明
st.markdown("---")
st.markdown("""
数据来源: [CoinGecko API](https://www.coingecko.com/)  
此应用每进行 API 调用前会重试 3 次，以确保数据获取稳定。
""")