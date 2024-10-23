import uuid
import dash
from dash import html
import feffery_antd_charts as fact
import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style

from fetch_data import realtime_data

app = dash.Dash(__name__, title="A股热门股票可视化")


def colormap(value):
    """根据涨跌幅自定义颜色"""

    colors = [
        (-0.04, "#00d641"),
        (-0.03, "#1aa448"),
        (-0.02, "#0e6f2f"),
        (-0.01, "#085421"),
        (0.01, "#424453"),
        (0.02, "#6d1414"),
        (0.03, "#961010"),
        (0.04, "#be0808"),
        "#e41414",
    ]

    for x, color in colors[:-1]:
        if value <= x:
            return color

    return colors[-1]


def render_layout():
    # 调用自定义接口获取东方财富最新行情数据
    demo_df = realtime_data()

    return html.Div(
        [
            fac.AntdSpace(
                [
                    fac.AntdTabs(
                        id="viz-tabs",
                        items=[
                            {
                                "label": level1,
                                "key": level1,
                                "children": html.Div(
                                    fact.AntdTreemap(
                                        key=str(uuid.uuid4()),
                                        data={
                                            "name": "root",
                                            "children": [
                                                {
                                                    "name": row.股票名称,
                                                    "value": row.成交额,
                                                    "label": f"{row.股票名称}\n{row.股票代码}\n成交额：{round(row.成交额, 3)}亿\n涨跌幅：{round(row.涨跌幅 * 100, 3)}%",
                                                    "color": colormap(row.涨跌幅),
                                                    "children": [
                                                        {
                                                            "name": row.股票名称,
                                                            "value": row.成交额,
                                                            "label": f"{row.股票名称}\n{row.股票代码}\n成交额：{round(row.成交额, 3)}亿\n涨跌幅：{round(row.涨跌幅 * 100, 3)}%",
                                                            "color": colormap(
                                                                row.涨跌幅
                                                            ),
                                                        }
                                                    ],
                                                }
                                                for row in (
                                                    demo_df.query("交易所 == @level1")
                                                    .sort_values(
                                                        "成交额",
                                                        ascending=False,
                                                    )
                                                    .head(50)
                                                    .itertuples()
                                                )
                                            ],
                                        },
                                        colorField="name",
                                        rawFields=["color", "label"],
                                        color={"func": "(item) => item.color"},
                                        label={
                                            "style": {
                                                "fontSize": 14,
                                                "fontWeight": "bold",
                                                "fontFamily": "Microsoft YaHei",
                                                "lineWidth": 2,
                                                "stroke": "#262626",
                                            },
                                            "formatter": {
                                                "func": "(item) => item.label"
                                            },
                                        },
                                        rectStyle={
                                            "stroke": "black",
                                            "lineWidth": 2,
                                        },
                                        interactions=[
                                            {
                                                "type": "treemap-drill-down",
                                            },
                                        ],
                                        legend=False,
                                        padding=0,
                                    ),
                                    style=style(height="calc(100vh - 130px)"),
                                ),
                            }
                            for level1 in ["深市", "沪市", "北交所"]
                        ],
                        size="large",
                        destroyInactiveTabPane=True,
                        tabBarRightExtraContent=fac.AntdText(
                            "TOP50热门股票可视化（成交额排序）",
                            style=style(fontSize=28, fontFamily="Microsoft YaHei"),
                        ),
                    )
                ],
                direction="vertical",
                style=style(width="100%"),
            )
        ],
        style=style(padding="24px 50px"),
    )


app.layout = render_layout

if __name__ == "__main__":
    app.run(debug=False)
