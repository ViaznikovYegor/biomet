import json
import ollama

def get_biometeo_recommendations(weather_days: list, user_profile: dict):
    print("🔄 Вызван LLM с", len(weather_days), "днями")  # ← отладка

    prompt = f"""Ты — эксперт по биометеорологии.

Пользователь: {user_profile.get('age', 35)} лет, рост {user_profile.get('height', 175)}см, вес {user_profile.get('weight', 75)}кг.
Чувствительность: {user_profile.get('sensitivity', 'medium')}.

Погода:
{json.dumps(weather_days, ensure_ascii=False, indent=2)}

Верни ТОЛЬКО JSON, к каждой активности напиши свой reason (минимум 2 предложения) почему стоит ей заняться в этот день:
{{
  "days": [
    {{
      "date": "19 мая",
      "activities": {{
        "running": {{"score": 0.9, "reason": "reason"}},
        "walking": {{"score": 0.9, "reason": "reason"}},
        "cycling": {{"score": 0.85, "reason": "reason"}},
        "yoga": {{"score": 0.85, "reason": "reason"}},
        "picnic": {{"score": 1.0, "reason": "reason"}},
        "stay_home": {{"score": 0.1, "reason": "reason"}}
      }}
    }}
  ]
}}"""

    try:
        response = ollama.chat(
            model="granite4.1:3b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3, "num_predict": 2000}
        )

        text = response['message']['content'].strip()
        print("📤 Ответ модели (первые 300 символов):")
        print(text[:300] + "..." if len(text) > 300 else text)

        # Извлекаем JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        json_text = text[start:end]

        data = json.loads(json_text)
        print("✅ УСПЕШНО распарсили JSON от LLM!")
        return data

    except Exception as e:
        print(f"❌ ОШИБКА LLM: {e}")
        import traceback
        traceback.print_exc()

        # Fallback с нормальными оценками
        print("⚠️ Используем fallback")
        fallback = {"days": []}
        for day in weather_days:
            fallback["days"].append({
                "date": day.get("date", ""),
                "activities": {
                    "running": {"score": 0.75, "reason": "Хорошая температура"},
                    "walking": {"score": 0.92, "reason": "Самая комфортная активность"},
                    "cycling": {"score": 0.65, "reason": "Может быть ветер"},
                    "yoga": {"score": 0.88, "reason": "Отлично подходит"},
                    "picnic": {"score": 0.8, "reason": "Приятная погода"}
                }
            })
        return fallback