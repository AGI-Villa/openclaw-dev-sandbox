"""每日天气查询 CLI 工具，使用 wttr.in 免费 API。"""

import sys
import json
import urllib.request
import urllib.error
import time


def fetch_weather(city: str) -> dict:
    """向 wttr.in 请求指定城市的天气数据，返回解析后的 JSON。"""
    url = f"https://wttr.in/{urllib.request.quote(city)}?format=j1"
    
    # 尝试3次，每次增加超时时间
    for attempt in range(3):
        timeout = 15 + attempt * 10  # 15s, 25s, 35s
        req = urllib.request.Request(url, headers={"User-Agent": "weather-cli/1.0"})
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"错误: 找不到城市 '{city}'，请检查城市名是否正确。")
            else:
                print(f"错误: HTTP {e.code} — {e.reason}")
            sys.exit(1)
        except urllib.error.URLError as e:
            if attempt < 2:  # 不是最后一次尝试
                print(f"警告: 网络连接超时，正在重试... ({attempt + 1}/3)")
                time.sleep(2)
                continue
            else:
                print(f"错误: 网络连接失败 — {e.reason}")
                sys.exit(1)
        except json.JSONDecodeError:
            if attempt < 2:
                print(f"警告: 无法解析数据，正在重试... ({attempt + 1}/3)")
                time.sleep(2)
                continue
            else:
                print("错误: 无法解析 API 返回的数据。")
                sys.exit(1)
        except Exception as e:
            if attempt < 2:
                print(f"警告: 未知错误，正在重试... ({attempt + 1}/3)")
                time.sleep(2)
                continue
            else:
                print(f"错误: {str(e)}")
                sys.exit(1)


def display_weather(data: dict, city: str) -> None:
    """从 API 响应中提取并打印温度、天气状况和湿度。"""
    try:
        current = data["current_condition"][0]
    except (KeyError, IndexError):
        print("错误: API 返回了意外的数据格式。")
        sys.exit(1)

    # wttr.in 返回的天气描述在 weatherDesc 列表中
    description = current.get("weatherDesc", [{}])[0].get("value", "未知")
    temp_c = current.get("temp_C", "N/A")
    humidity = current.get("humidity", "N/A")
    feels_like = current.get("FeelsLikeC", "N/A")

    area = data.get("nearest_area", [{}])[0]
    area_name = area.get("areaName", [{}])[0].get("value", city)
    country = area.get("country", [{}])[0].get("value", "")

    print(f"\n📍 {area_name}, {country}")
    print(f"🌡  温度: {temp_c}°C (体感 {feels_like}°C)")
    print(f"☁  天气: {description}")
    print(f"💧 湿度: {humidity}%\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: python weather.py <城市名>")
        print("示例: python weather.py Beijing")
        sys.exit(1)

    city = " ".join(sys.argv[1:])
    data = fetch_weather(city)
    display_weather(data, city)


if __name__ == "__main__":
    main()
