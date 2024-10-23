import requests
import pandas as pd


def realtime_data() -> pd.DataFrame:
    """
    以 东方财富网-沪深京A股-实时行情 为例，页面地址：https://quote.eastmoney.com/center/gridlist.html#hs_a_board
    """

    url = "http://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "6000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
        "fields": "f12,f14,f2,f15,f16,f17,f18,f3,f10,f6,f21,f22",
        "_": "1623833739532",
    }
    response = requests.get(url, params=params)

    if not response.json()["data"]["diff"]:
        return pd.DataFrame()

    raw_df = pd.DataFrame(response.json()["data"]["diff"])

    raw_df.columns = [
        "最新价",
        "涨跌幅",
        "成交额",
        "量比",
        "股票代码",
        "股票名称",
        "最高价",
        "最低价",
        "今开",
        "昨收",
        "流通市值",
        "涨速",
    ]

    # 数值转换
    for column in raw_df.columns:
        if column not in ["股票代码", "股票名称"]:
            raw_df[column] = pd.to_numeric(raw_df[column], errors="coerce")

    # 处理金额单位(亿)和小数位(两位小数)
    raw_df["成交额"] = (raw_df["成交额"] / 1e8).round(decimals=2)
    raw_df["流通市值"] = (raw_df["流通市值"] / 1e8).round(decimals=2)

    # 去除停牌或退市股
    raw_df = raw_df.dropna(subset=["最新价", "涨跌幅"], how="any", ignore_index=True)

    # 添加所属交易所字段
    raw_df.insert(
        0,
        "交易所",
        raw_df["股票代码"].apply(
            lambda c: "深市"
            if c < "400000"
            else ("沪市" if "600000" < c < "800000" else "北交所")
        ),
    )

    # 涨跌幅转换为小数
    raw_df["涨跌幅"] /= 100

    return raw_df


if __name__ == "__main__":
    # 写出演示数据到本地
    df = realtime_data()
    df.to_csv("演示数据.csv", index=False)
