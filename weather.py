"""每日天气查询 CLI 工具，使用 wttr.in 免费 API（无需注册）。"""

import sys

import requests


def fetch_weather(city: str) -> dict:
    """向 wttr.in 请求指定城市的天气数据，返回解析后的 JSON。

    带有重试机制（最多 3 次），超时时间逐次递增。
    """
    url = f"https://wttr.in/{city}"
    params = {"format": "j1"}
    headers = {"User-Agent": "weather-cli/2.0"}

    last_error = None
    for attempt in range(3):
        timeout = 15 + attempt * 10  # 15s, 25s, 35s
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)

            if resp.status_code == 404:
                print(f"错误: 找不到城市 '{city}'，请检查城市名是否正确。")
                sys.exit(1)
            resp.raise_for_status()

            return resp.json()

        except requests.exceptions.ConnectionError:
            last_error = "网络连接失败，请检查网络设置。"
        except requests.exceptions.Timeout:
            last_error = "请求超时，服务器无响应。"
        except requests.exceptions.HTTPError as e:
            print(f"错误: HTTP {e.response.status_code} — {e.response.reason}")
            sys.exit(1)
        except ValueError:
            last_error = "无法解析 API 返回的数据。"

        if attempt < 2:
            print(f"警告: {last_error} 正在重试... ({attempt + 1}/3)")

    print(f"错误: {last_error}")
    sys.exit(1)


def display_weather(data: dict, city: str) -> None:
    """从 API 响应中提取并打印温度、天气状况和湿度。"""
    try:
        current = data["current_condition"][0]
    except (KeyError, IndexError):
        print("错误: API 返回了意外的数据格式。")
        sys.exit(1)

    # wttr.in 的天气描述在 weatherDesc 列表中
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