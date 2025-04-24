"""
This file is used to test the CRUD operations of the weather app. 
It won't be used externally. 
Thus, the language is Chinese for author's convenience.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.schema import DatabaseManager
from database.crud import WeatherCRUD

def test_database_setup():
    """测试数据库初始化"""
    print("测试数据库初始化...")
    db_manager = DatabaseManager()
    db_manager.create_tables()
    print("数据库表创建成功")

def test_crud_operations():
    """测试CRUD操作"""
    crud = WeatherCRUD()
    
    print("\n--------------测试CREATE操作------------------")
    # 测试创建位置
    print("\n测试创建位置...")
    location_id = crud.create_location("北京", 39.9042, 116.4074)
    print(f"创建位置结果: ID = {location_id}")
    
    # 测试创建天气记录
    print("\n测试创建天气记录...")
    success, result = crud.create_weather_record(
        location_id, 
        "2025-04-23", 
        25.5,  # 温度
        24.0,  # 体感温度
        65,    # 湿度
        3.5,   # 风速
        "东北风", # 风向
        "晴", # 天气状况
        "晴朗无云" # 天气描述
    )
    print(f"创建天气记录结果: 成功 = {success}, 结果 = {result}")
    
    # 测试创建查询历史
    print("\n测试创建查询历史...")
    success, result = crud.create_query_history(
        location_id,
        "2025-04-20",
        "2025-04-25"
    )
    print(f"创建查询历史结果: 成功 = {success}, 结果 = {result}")
    
    print("\n---------------测试READ操作---------------")
    # 测试获取位置信息
    print("\n测试获取位置信息...")
    location = crud.get_location_by_id(location_id)
    print(f"获取位置结果: {location}")
    
    # 测试获取天气记录
    print("\n测试获取天气记录...")
    weather = crud.get_weather_by_location_and_date(location_id, "2025-04-23")
    print(f"获取天气记录结果: {weather}")
    
    # 测试获取日期范围内的天气记录
    print("\n测试获取日期范围内的天气记录...")
    weather_range = crud.get_weather_by_date_range(location_id, "2025-04-20", "2025-04-25")
    print(f"获取日期范围内的天气记录结果: {weather_range}")
    
    # 测试获取所有天气记录
    print("\n测试获取所有天气记录...")
    all_weather = crud.get_all_weather_records()
    print(f"获取所有天气记录结果: {all_weather}")
    
    # 测试获取查询历史
    print("\n测试获取查询历史...")
    history = crud.get_query_history()
    print(f"获取查询历史结果: {history}")
    
    print("\n-------------测试UPDATE操作-------------")
    # 测试更新位置信息
    print("\n测试更新位置信息...")
    success, message = crud.update_location(location_id, latitude=39.9, longitude=116.4)
    print(f"更新位置结果: 成功 = {success}, 消息 = {message}")
    


    # 测试更新天气记录
    print("\n测试更新天气记录...")
    if weather:
        success, message = crud.update_weather_record(
            weather['id'],
            temperature=26.0,
            humidity=70
        )
        print(f"更新天气记录结果: 成功 = {success}, 消息 = {message}")
    
    print("\n--------------测试DELETE操作----------------")
    print("\n创建临时位置...")
    temp_location_id = crud.create_location("临时位置", 0, 0)
    print(f"创建临时位置结果: ID = {temp_location_id}")
    
    # 测试删除位置
    print("\n测试删除位置...")
    success, message = crud.delete_location(temp_location_id)
    print(f"删除位置结果: 成功 = {success}, 消息 = {message}")
    
    # 创建一个临时天气记录用于测试删除
    print("\n创建临时天气记录用于测试删除...")
    success, result = crud.create_weather_record(
        location_id, 
        "2025-04-24", 
        27.0
    )
    temp_weather_id = result if isinstance(result, int) else None
    print(f"创建临时天气记录结果: 成功 = {success}, ID = {temp_weather_id}")
    
    if temp_weather_id and isinstance(temp_weather_id, int):
        # 测试删除天气记录
        print("\n测试删除天气记录...")
        success, message = crud.delete_weather_record(temp_weather_id)
        print(f"删除天气记录结果: 成功 = {success}, 消息 = {message}")
    
    print("\n------------------测试验证功能---------------------")
    # 测试日期验证
    print("\n测试日期验证...")
    db_manager = DatabaseManager()
    valid_date = db_manager.validate_date("2025-04-23")
    invalid_date = db_manager.validate_date("2025-13-32")
    print(f"有效日期验证结果: {valid_date}")
    print(f"无效日期验证结果: {invalid_date}")
    
    # 测试日期范围验证
    print("\n测试日期范围验证...")
    valid, result = db_manager.validate_date_range("2025-04-20", "2025-04-25")
    print(f"有效日期范围验证结果: 成功 = {valid}, 结果 = {result}")
    
    valid, result = db_manager.validate_date_range("2025-04-25", "2025-04-20")
    print(f"无效日期范围验证结果: 成功 = {valid}, 结果 = {result}")
    
    print("\n搞定")

if __name__ == "__main__":
    test_database_setup()
    test_crud_operations()
