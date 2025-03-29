import requests
# Mapbox Token
MAPBOX_TOKEN = 'MAPBOX_API'

def generate_trip_map_and_text(places):
    
    places_list = places.split('，')
    
    # 獲取每個景點的經緯度
    coordinates = []
    for place in places_list:
        print(place)
        geocode_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{place.strip()}.json?access_token={MAPBOX_TOKEN}"
        response = requests.get(geocode_url)
        print(response)
        data = response.json()
        print(data)
        
        if data.get("features"):
            # 獲取第一個結果的經緯度
            lon, lat = data["features"][0]["geometry"]["coordinates"]
            coordinates.append((lat, lon))
            print(coordinates)
        else:
            print(f"無法找到景點: {place.strip()}")

    if not coordinates:
        print("沒有有效的經緯度，請檢查景點名稱。")
        return

    # 生成 Directions API 請求 URL
    coordinates_str = ";".join([f"{lat},{lon}" for lon, lat in coordinates])
    directions_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates_str}?access_token={MAPBOX_TOKEN}"
    
    # 發送請求並解析 Directions API 回傳的路線
    response = requests.get(directions_url)
    data = response.json()
    print(data)
    if data.get("routes"):
        
        # 獲取路線的線條坐標（encoded polyline）
        route_geometry = data["routes"][0]["geometry"]

        
        # 建立靜態地圖 URL，顯示行程路線
        map_url = (
            f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/path-5+f44-0.5({route_geometry})/"
            f"auto/600x400?access_token={MAPBOX_TOKEN}"
        )

        # 獲取路線的線條坐標（encoded polyline）以及概述
        route_geometry = data["routes"][0]["geometry"]
        route_summary = data["routes"][0]["legs"][0]["summary"]
        distance = data["routes"][0]["distance"] / 1000  # 轉換為公里
        duration = data["routes"][0]["duration"] / 60  # 轉換為分鐘

        # 生成多個地點的名稱清單
        waypoint_names = [waypoint['name'] for waypoint in data['waypoints']]
        waypoint_route = " ➔ ".join(waypoint_names)  # 用箭頭表示每個地點的順序

        # 簡單的路線描述
        route_description = (
            f"您的行程路線：{waypoint_route}\n"
            #f"途經：{route_summary}\n"
            f"總距離：約 {distance:.2f} 公里\n"
            f"預計時間：約 {duration:.0f} 分鐘\n"
        )

        print(route_description)
        return {"map_url": map_url, "description": route_description}

    else:
        print("無法獲取路線。請確認地點經緯度和 Mapbox Token 是否正確。")