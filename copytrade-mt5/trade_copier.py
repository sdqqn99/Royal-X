# ملف: trade_copier.py
import MetaTrader5 as mt5
import time
from datetime import datetime

class TradeCopier:
    def __init__(self, source_account, dest_accounts):
        self.source_account = source_account
        self.dest_accounts = dest_accounts
        self.connected = False

    def connect(self, password, server):
        if not mt5.initialize():
            return False
            
        authorized = mt5.login(
            login=self.source_account,
            password=password,
            server=server
        )
        
        self.connected = authorized
        return authorized

    def copy_trades(self):
        if not self.connected:
            return False

        # جلب الصفقات المفتوحة
        positions = mt5.positions_get()
        
        for position in positions:
            for dest in self.dest_accounts:
                self.execute_trade(dest, position)

        return True

    def execute_trade(self, dest_account, position):
        # تبديل الحساب الهدف
        mt5.login(
            login=dest_account['login'],
            password=dest_account['password'],
            server=dest_account['server']
        )

        # إعداد طلب التداول
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY if position.type == 0 else mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(position.symbol).ask,
            "deviation": 20,
            "magic": 10032023,
            "comment": f"Copied from {self.source_account}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }
        
        # إرسال الطلب
        result = mt5.order_send(request)
        return result.retcode == mt5.TRADE_RETCODE_DONE

if __name__ == "__main__":
    copier = TradeCopier(
        source_account=123456,
        dest_accounts=[
            {'login': 654321, 'password': '*****', 'server': 'Broker-Server'}
        ]
    )
    
    if copier.connect(password='source_password', server='Broker-Server'):
        while True:
            copier.copy_trades()
            time.sleep(5)  # تحديث كل 5 ثواني