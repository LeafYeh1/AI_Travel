import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from Gemini import generate_response
from maps import generate_trip_map_and_text
import string

# 初始化 bot
bot = telebot.TeleBot('telebot_api')

# 使用者選擇的地區和天數
user_choices = {}

# 定義 city 英文換中文
city = {
    'Taipei' : '台北',
    'New_Taipei' : '新北',
    'Keelung' : '基隆',
    'Taoyan' : '桃園',
    'Hsinchu' : '新竹',
    'Miaoli' : '苗栗',
    'Changhua' : '雲林',
    'Nantou' : '南投',
    'TaiChung' : '台中',
    'Chiayi' : '嘉義',
    'Tainan' : '台南',
    'Kaohsiung' : '高雄',
    'Pingtung' : '屏東',
    'Taitung' : '台東',
    'Hualien' : '花蓮',
    'Yilan' : '宜蘭'
}

# 定義 day 英文換中文
day = {
    'one_day' : '1天',
    'two_day' : '2天',
    'three_day' : '3天',
    'four_day' : '4天',
    'five_day' : '5天'
}

# 指令處理
@bot.message_handler(commands=['help', 'start'])
def send_help(message):
    bot.reply_to(message, """
你好! 我是旅行 GOGO!
我可以幫你安排你想要的任何旅遊行程，
也可以和我聊聊天!
/travel 可以幫你安排行程
/map 可以幫你查看距離和地圖
""")
    
# 選擇地區
@bot.message_handler(commands=['travel'])
def message_handler(message):
    bot.send_message(message.chat.id, "選擇你想去的地區~", reply_markup=gen_markup())
def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('北', callback_data="North"))
    markup.add(InlineKeyboardButton('中', callback_data="Center"))
    markup.add(InlineKeyboardButton('南', callback_data="South"))
    markup.add(InlineKeyboardButton('東', callback_data="East"))
    
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    #選擇地區
    if call.data == "North":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="選擇北部的縣市~", reply_markup=gen_city_markup("North"))
    elif call.data == "Center":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="選擇中部的縣市~", reply_markup=gen_city_markup("Center"))
    elif call.data == "South":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="選擇南部的縣市~", reply_markup=gen_city_markup("South"))
    elif call.data == "East":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="選擇東部的縣市~", reply_markup=gen_city_markup("East"))
    #選擇縣市
    elif call.data in ["Taipei", "New_Taipei", "Keelung", "Taoyan", "Hsinchu", "Miaoli", "Changhua", "Nantou", "TaiChung", "Chiayi", "Tainan", "Kaohsiung", "Pingtung", "Taitung", "Hualien", "Yilan"]:
        # 儲存使用者選擇的城市
        user_choices[chat_id] = {"city": call.data}  
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="選擇天數~", reply_markup=gen_day_markup())
    # 如果使用者選擇的是天數
    elif call.data in ["one_day", "two_day", "three_day", "four_day", "five_day"]:
        if chat_id in user_choices:
            # 儲存使用者選擇的天數
            user_choices[chat_id]["day"] = call.data  
            city_en = user_choices[chat_id]["city"]
            city_zh = city[city_en]
            day_en = user_choices[chat_id]["day"]
            day_zh = day[day_en]
            
            # 儲存選擇之後，詢問使用者是否有額外需求
            bot.send_message(chat_id, f"你想要 {city_zh} {day_zh} 的旅行。請問有沒有其他需求？")
            # 接下來會等待用戶回覆需求
            bot.register_next_step_handler_by_chat_id(chat_id, get_user_requirements)
            
        else:
            bot.send_message(chat_id, "請先選擇城市！")
            
# 選地區裡的城市
def gen_city_markup(region):
    markup = InlineKeyboardMarkup()
    
    if region == "North":
        markup.row_width =  1
        markup.add(InlineKeyboardButton('台北', callback_data="Taipei"), 
                   InlineKeyboardButton('新北', callback_data="New_Taipei"),
                   InlineKeyboardButton('基隆', callback_data="Keelung"),
                   InlineKeyboardButton('桃園', callback_data="Taoyan"),
                   InlineKeyboardButton('新竹', callback_data="Hsinchu"))
    elif region == "Center":
        markup.row_width =  1
        markup.add(InlineKeyboardButton('苗栗', callback_data="Miaoli"), 
                   InlineKeyboardButton('彰化', callback_data="Changhua"),
                   InlineKeyboardButton('南投', callback_data="Nantou"),
                   InlineKeyboardButton('台中', callback_data="TaiChung"),)
    elif region == "South":
        markup.row_width =  1
        markup.add(InlineKeyboardButton('嘉義', callback_data="Chiayi"), 
                   InlineKeyboardButton('台南', callback_data="Tainan"),
                   InlineKeyboardButton('高雄', callback_data="Kaohsiung"),
                   InlineKeyboardButton('屏東', callback_data="Pingtung"))
    elif region == "East":
        markup.row_width =  1
        markup.add(InlineKeyboardButton('台東', callback_data="Taitung"), 
                   InlineKeyboardButton('花蓮', callback_data="Hualien"),
                   InlineKeyboardButton('宜蘭', callback_data="Yilan"),)
        cities = ['花蓮', '台東', '宜蘭']
    
    return markup

# 選擇天數
def gen_day_markup():
    markup = InlineKeyboardMarkup()
    
    markup.row_width =  1
    markup.add(InlineKeyboardButton('1天', callback_data="one_day"), 
                InlineKeyboardButton('2天', callback_data="two_day"),
                InlineKeyboardButton('3天', callback_data="three_day"),
                InlineKeyboardButton('4天', callback_data="four_day"),
                InlineKeyboardButton('5天', callback_data="five_day"))
    
    return markup

# 使用者輸入要求
def get_user_requirements(message):
    chat_id = message.chat.id
    requirements = message.text  # 儲存使用者輸入的需求
    if chat_id in user_choices:
        user_choices[chat_id]["user_prompt"] = requirements  # 儲存需求
        print(user_choices)
        
        # 獲取城市和天數
        city_en = user_choices[chat_id]["city"]
        city_zh = city[city_en]
        day_en = user_choices[chat_id]["day"]
        day_zh = day[day_en]
        user_prompt = user_choices[chat_id]["user_prompt"]

        # 最終回覆
        bot.send_message(chat_id, f"沒問題，這就幫你安排\n {city_zh} {day_zh} 的旅行。\n你的需求：{user_prompt}")
        trip = call_AI(city_zh, day_zh, user_prompt)
        bot.send_message(chat_id, trip)
        
# 生成AI回應
def call_AI(city_name, num_days, user_prompt):
    
    prompt = f"幫我推薦 {city_name} 的 {num_days} 日行程 ， 要求有這些 {user_prompt}"
     # 這裡是AI生成行程
    trip = generate_response(prompt)
    return trip

#地圖
@bot.message_handler(commands=['map'])
def send_help(message):
    bot.reply_to(message, """
Hi! 我是你的貼心 map! 請告訴我你要去哪裡，使用逗號分隔每個景點名稱。
例如 : 漁光島，台南火車站
""")
    # 等待用戶回覆需求
    bot.register_next_step_handler(message, process_places)

def process_places(message):
    # 獲取用戶的回覆，即景點名稱
    places = message.text.strip()  # 確保去掉前後空白
    print(places)
    trip_data = generate_trip_map_and_text(places)  # 將用戶的輸入傳遞給生成地圖的函數
    if trip_data:
        map_url = trip_data["map_url"]
        route_description = trip_data["description"]

        # 發送地圖和路線描述到 Telegram
        bot.send_photo(message.chat.id, photo=map_url, caption="這是您的行程路線！")
        bot.send_message(message.chat.id, route_description)
    else:
        bot.send_message(message.chat.id, "無法生成行程地圖，請確認輸入的景點是否正確。")

    
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "我好想旅行":
        bot.reply_to(message, "快去吧!我把一切都藏在那裡!!")
    else:
        bot_prompt = f"你是一個喜歡聊台灣的各個旅遊景點和美食的大學生，非常喜歡暢談台灣的美麗，以下是用戶的提問：{message.text}"
        ai_response = generate_response(bot_prompt)
        bot.reply_to(message, ai_response)
        
print("I'm online!")

# 開始接收訊息
bot.infinity_polling()
