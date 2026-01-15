import time
import requests
from config.config import browser_agent_headers
from enum import Enum

class StockStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"
    FLAT = "FLAT"

class StockProvider:

    API_BASE_URL = "https://stock.xueqiu.com/v5/stock/realtime/quotec.json"


    def fetch_stock_data(self, stock_symbol):
        timestamp = int(time.time())
        params = {
            'symbol': stock_symbol,
            '_': timestamp
        }
        
        headers = browser_agent_headers
        
        response = requests.get(self.API_BASE_URL, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def extract_stock_info(self, data)-> dict:
        # 处理API返回的数据结构
        data_list = data.get('data', [])
        if not data_list or not isinstance(data_list, list) or len(data_list) == 0:
            return {
                "price": "0.00",
                "percent": "0.00%",
                "status": StockStatus.FLAT
            }
        
        # 取第一个股票数据
        stock_data = data_list[0]
        
        current_price = stock_data.get('current', 0)
        percent_change = stock_data.get('percent', 0.0)
        
        # 判断涨跌状态
        if percent_change > 0:
            status = StockStatus.UP
        elif percent_change < 0:
            status = StockStatus.DOWN
        else:
            status = StockStatus.FLAT
            
        return {
            "price": f"{current_price:.2f}",  # 转换为字符串格式
            "percent": f"{percent_change:.2f}%",
            "status": status
        }

    @staticmethod
    def get_stock_data(stock_symbol):
        """静态方法，供项目其他部分调用，返回兼容格式的数据"""
        provider = StockProvider()
        try:
            raw_data = provider.fetch_stock_data(stock_symbol)
            stock_info = provider.extract_stock_info(raw_data)
            
            # 兼容旧格式，添加 is_up 字段
            stock_info['is_up'] = (stock_info['status'] == StockStatus.UP)
            
            return stock_info
        except Exception as e:
            print(f"获取股票 {stock_symbol} 数据失败: {e}")
            return {
                "price": "0.00",  # 返回字符串格式
                "percent": "0.00%", 
                "status": StockStatus.FLAT,
                "is_up": False
            }