from dataclasses import dataclass

import mlflow
from mlflow.entities import SpanType


@dataclass
class WeatherReport:
    city: str
    condition: str
    temperature_c: int
    humidity_percent: int
    wind: str


def extract_city(question: str) -> str:
    """샘플 날씨 도구가 사용할 도시명을 질문에서 간단히 추출한다."""
    # 데모 목적상 규칙 기반으로 도시만 고르고, 못 찾으면 서울로 기본값 처리한다.
    for city in ("서울", "부산", "제주", "대구", "인천", "seoul", "busan", "jeju", "daegu", "incheon"):
        if city.lower() in question.lower():
            return city
    return "서울"


def weather_data_text(weather: WeatherReport) -> str:
    return (
        f"city={weather.city}, condition={weather.condition}, "
        f"temperature_c={weather.temperature_c}, humidity_percent={weather.humidity_percent}, "
        f"wind={weather.wind}"
    )


@mlflow.trace(span_type=SpanType.TOOL)
def get_weather(city: str) -> WeatherReport:
    """로컬 날씨 도구다. 운영에서는 이 부분을 사내 API나 DB 조회로 교체하면 된다."""
    # 여기서 span이 생겨야 trace graph에서 weather lookup 노드를 클릭할 수 있다.
    reports = {
        "seoul": WeatherReport("Seoul", "clear", 27, 48, "light breeze"),
        "서울": WeatherReport("Seoul", "clear", 27, 48, "light breeze"),
        "busan": WeatherReport("Busan", "cloudy", 24, 68, "coastal wind"),
        "부산": WeatherReport("Busan", "cloudy", 24, 68, "coastal wind"),
        "jeju": WeatherReport("Jeju", "rain showers", 23, 82, "moderate wind"),
        "제주": WeatherReport("Jeju", "rain showers", 23, 82, "moderate wind"),
        "daegu": WeatherReport("Daegu", "hot", 30, 42, "calm"),
        "대구": WeatherReport("Daegu", "hot", 30, 42, "calm"),
        "incheon": WeatherReport("Incheon", "misty", 22, 73, "sea breeze"),
        "인천": WeatherReport("Incheon", "misty", 22, 73, "sea breeze"),
    }
    return reports.get(city.lower(), WeatherReport(city, "partly cloudy", 25, 55, "calm"))
