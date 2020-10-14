from due import Due

d = Due()

# 预定场地
# 参数 : 
# -------------------------------------------
# days[1=今天, 2=明天, 3=后天]
# start[可选8-20 整点]
# end[可选9-21 整点]
# -------------------------------------------
# 函数 :
# d.get_due(days=3, start=19, end=20)   # 定场函数, 默认为可定场地的第一个
# d.check_due(True)     # 查询是否预定成功
# d.find_place(days=3, start=19, end=20)  # 找寻对应时间段的空场地
# d.cancel_due() # 取消最近的订单


d.get_due(days=3, start=19, end=21)