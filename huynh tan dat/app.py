from http import server
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(
    'huynh-tan-dat-firebase-adminsdk-wb8f1-f9d176e7d4.json')
appLoadData = firebase_admin.initialize_app(cred)

dbFireStore = firestore.client()

queryResults = list(dbFireStore.collection(u'tbl-20073701').stream())
listQueryResult = list(map(lambda x: x.to_dict(), queryResults))

df = pd.DataFrame(listQueryResult)

df['YEAR_ID'] = df['YEAR_ID'].astype("str")
df["QTR_ID"] = df["QTR_ID"].astype("str")
df["PROFIT"] = df["SALES"]-(df["QUANTITYORDERED"]*df["PRICEEACH"])

app = Dash(__name__)
server = app.server

app.title = "Danh Mục Sản Phẩm Tiềm Năng"

# Doanh số(Single Value)
sales = sum(df['SALES'])

# Lợi nhuận(Single Value)
profit = sum(df['PROFIT'])

# Top doanh số(Single Value)
topSales = df.groupby(['CATEGORY']).sum('SALES').max().SALES
maSP_TopSales = df.groupby(['CATEGORY']).sum('SALES').sort_values(
    by="SALES", ascending=False).reset_index().head(1)['CATEGORY'][0]

# Top lợi nhuận(Single Value)
topProfit = df.groupby(['CATEGORY']).sum('PROFIT').max().PROFIT
maSP_TopProfit = df.groupby(['CATEGORY']).sum('PROFIT').sort_values(
    by="PROFIT", ascending=False).reset_index().head(1)['CATEGORY'][0]

# Doanh số bán hàng theo năm (Bar chart)
data1 = df.groupby(['YEAR_ID']).sum('SALES').reset_index()
figDoanhSo = px.bar(data1, x='YEAR_ID', y='SALES', labels={'YEAR_ID': 'Năm', 'SALES': 'Doanh số'},
                    title='DOANH SỐ BÁN HÀNG THEO NĂM')

# Lợi nhuận bán hàng theo năm(Bar chart)
data2 = df.groupby(['YEAR_ID']).sum('PROFIT').reset_index()
figLoiNhuan = px.line(data2, x='YEAR_ID', y='PROFIT', markers=True, labels={'YEAR_ID': 'Năm', 'PROFIT': 'Lợi Nhuận'},
                      title='LỢI NHUẬN BÁN HÀNG THEO NĂM')

# Tỉ lệ đóng góp của doanh số theo từng danh mục theo từng năm(Sunbrust)
figTiLeDoanhSo = px.sunburst(df, path=['YEAR_ID', 'CATEGORY'], values='SALES',
                             color='SALES',
                             labels={'parent': 'Năm',
                                     'labels': 'Danh Mục', 'SALES': 'Doanh Số'},
                             title='TỈ LỆ DOANH SỐ THEO DANH MỤC VÀ NĂM')

# Tỉ lệ đóng góp của lợi nhuận theo từng danh mục(Sunbrust)
figTiLeLoiNhuan = px.sunburst(df, path=['YEAR_ID', 'CATEGORY'], values='PROFIT',
                              color='PROFIT',
                              labels={
                                  'parent': 'Năm', 'labels': 'Danh Mục', 'PROFIT': 'Lợi Nhuận'},
                              title='TỈ LỆ LỢI NHUẬN THEO DANH MỤC VÀ NĂM')

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H3(
                    "XÂY DỰNG SẢN PHẨM DANH MỤC TIỀM NĂNG", className="header-title"
                ),
                html.H4(
                    "Trường: IUH, Lớp: DHHTTT16C, MSSV: 20030021, Tên: Nguyễn Nhất Huy", className="header-title"
                )
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=html.Div(
                        children=[
                            html.H4(
                                "DOANH SỐ SALE",
                            ),
                            "{:.2f}".format(sales)
                        ],
                        className="label"
                    ), className="card c1"
                ),
                html.Div(
                    children=html.Div(
                        children=[
                            html.H4(
                                "LỢI NHUẬN",
                            ),
                            "{:.2f}".format(profit)
                        ],
                        className="label"
                    ), className="card c1"
                ),
                html.Div(
                    children=html.Div(
                        children=[
                            html.H4(
                                "TOP DOANH SỐ",
                            ),
                            maSP_TopSales+', '+"{:.2f}".format(topSales)
                        ],
                        className="label"
                    ), className="card c1"
                ),
                html.Div(
                    children=html.Div(
                        children=[
                            html.H4(
                                "TOP LỢI NHUẬN",
                            ),
                            maSP_TopProfit+', '+"{:.2f}".format(topProfit)
                        ],
                        className="label"
                    ), className="card c1"
                ),
                html.Div(
                    children=dcc.Graph(
                        figure=figDoanhSo,
                        className="hist"
                    ), className="card c2"
                ),
                html.Div(
                    children=dcc.Graph(
                        figure=figTiLeDoanhSo,
                        className="hist"
                    ), className="card c2"
                ),
                html.Div(
                    children=dcc.Graph(
                        figure=figLoiNhuan,
                        className="hist"
                    ), className="card c2"
                ),
                html.Div(
                    children=dcc.Graph(
                        figure=figTiLeLoiNhuan,
                        className="hist"
                    ), className="card c2"
                )
            ], className="wrapper"
        )
    ])

if __name__ == '__main__':
    app.run_server(debug=True, port=8070)
