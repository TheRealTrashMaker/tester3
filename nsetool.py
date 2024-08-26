from datetime import datetime
import requests
from flask import Flask, request, jsonify
app = Flask(__name__)


def nse_charter(regulation):
    """
    获取股票跌幅数据
    :param regulation: SYMBOL
    :return:
    """
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://www.nseindia.com/get-quotes/equity?symbol={regulation}',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'x-requested-with': 'XMLHttpRequest',
    }
    params = {
        'symbol': f'{regulation}',
    }
    session = requests.Session()
    session.get(url='https://www.nseindia.com/', headers=headers)
    response = session.get('https://www.nseindia.com/api/quote-equity', params=params,
                            headers=headers)
    try:
        params_S = {
            'index': response.json()["info"]["identifier"],
            'type': 'symbol',
        }
        response_s = session.get('https://www.nseindia.com/api/chart-databyindex', params=params_S,
                                headers=headers)
        json_data = response_s.json()

        def filter_continuous_prices(data):
            if not data:
                return []

            filtered_data = [data[0]]  # 初始化保留第一个元素

            for i in range(1, len(data)):
                if data[i][1] != data[i - 1][1]:  # 价格不同才添加到结果中
                    filtered_data.append(data[i])

            return filtered_data

        # filtered = []
        filtered_datas = filter_continuous_prices(json_data["grapthData"])
        # for filtered_data in filtered_datas:
        #     filtered.append(filtered_data[1])
        new_json_data = {
            "companyName": response.json()["info"]["companyName"],
            "close_prices": filtered_datas,
            "current_price": response.json()["priceInfo"]["lastPrice"],                 # 当前的股票价格
            "percent_change": response.json()["priceInfo"]["change"],    # 今日股票价格的百分比变化
            "prasent": response.json()["priceInfo"]["pChange"],                              # 表示当前的变化值
            "stock": json_data['name']                          # 股票的名称
        }
        # 打印结果
        return new_json_data
    except KeyError:
        new_json_data = {
            "error": f"Invalid parameter {regulation}",
            "note": "此参数是刚发行或即将发行的吗？请切换请求参数重新尝试！！！"
        }
    return new_json_data

@app.route('/kline_1day/<regulation>', methods=['GET'])
def kline_chart(regulation):
    chart_data = nse_charter(regulation)
    return_data = {
        "categories":[
            datetime.fromtimestamp(chart_data["close_prices"][0][0]/1000).strftime('%Y/%m/%d')
        ],
        "period": "1mo",
        "series": [
    {
      "data": [
        [
          chart_data["close_prices"][0][1],
          chart_data["close_prices"][1][1],
          chart_data["close_prices"][0][1],
          chart_data["close_prices"][1][1],
        ]
      ],
      "name": "Kline"
    }
  ],
        "stock": regulation

    }
    print(return_data)
    return jsonify(return_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5299, debug=True)
