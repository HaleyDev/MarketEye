"""
股票数据提供者接口
"""
import random

class StockProvider:
    @staticmethod
    def get_stock_data(code: str):
        """
        获取股票实时数据 (Mock)
        :param code: 股票代码
        :return: 字典 {"price": str, "percent": str, "is_up": bool}
        """
        # 这里预留真实API调用位置
        # data = api.get(code)
        
        # Mock数据生成
        base_price = random.uniform(10, 1000)
        change_percent = random.uniform(-10, 10)
        current_price = base_price * (1 + change_percent / 100)
        
        return {
            "price": f"{current_price:.2f}",
            "percent": f"{change_percent:+.2f}%",
            "is_up": change_percent >= 0
        }
