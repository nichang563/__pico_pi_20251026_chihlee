import streamlit as st
# import pandas as pd

st.title("我的第一個 Streamlit 應用程式")

# 顯示文字
st.write("歡迎使用 Streamlit！")

# 互動式輸入
name = st.text_input("請輸入您的名字：")
if name:
    st.write(f"你好，{name}！")

# 顯示數據
# data = pd.DataFrame({
#     '姓名': ['張三', '李四', '王五'],
#     '分數': [85, 90, 78]
# })
# st.dataframe(data)

# # 繪製圖表
# st.bar_chart(data.set_index('姓名'))