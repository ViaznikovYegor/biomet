import json
import ollama


def get_biometeo_recommendations(weather_days: list, user_profile: dict):
    print(f"🔄 Вызван LLM с {len(weather_days)} днями")

    prompt = f"""Ты — эксперт по биометеорологии.

Пользователь: {user_profile.get('age', 35)} лет, рост {user_profile.get('height', 175)} см, вес {user_profile.get('weight', 75)} кг.
Метеочувствительность: {user_profile.get('sensitivity', 'medium')}.

Прогноз погоды на {len(weather_days)} дней:
{json.dumps(weather_days, ensure_ascii=False, indent=2)}

Верни ТОЛЬКО JSON для **всех** дней, со своим обоснованием почему именно эта активность:

{{
  "days": [
    {{
      "date": "22 мая",
      "activities": {{
        "running": {{"score": 0.85, "reason": "Два предложения обоснования."}},
        "walking": {{"score": 0.9, "reason": "Два предложения обоснования."}},
        "cycling": {{"score": 0.75, "reason": "Два предложения обоснования."}},
        "yoga": {{"score": 0.95, "reason": "Два предложения обоснования."}},
        "picnic": {{"score": 0.8, "reason": "Два предложения обоснования."}},
        "stay_home": {{"score": 0.3, "reason": "Два предложения обоснования."}}
      }}
    }}
    // и остальные дни
  ]
}}"""

    try:
        response = ollama.chat(
            model="granite4.1:3b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3, "num_predict": 4500}
        )

        text = response['message']['content'].strip()
        print("📤 Ответ модели (первые 400 символов):", text[:400])

        start = text.find('{')
        end = text.rfind('}') + 1
        data = json.loads(text[start:end])

        print(f"✅ УСПЕШНО! Получено дней: {len(data.get('days', []))}")
        return data

    except Exception as e:
        print(f"❌ ОШИБКА LLM: {e}")
        import traceback
        traceback.print_exc()

        # Fallback
        fallback = {"days": []}
        for day in weather_days:
            fallback["days"].append({
                "date": day.get("date", ""),
                "activities": {
                    "running": {"score": 0.75, "reason": "Условия позволяют комфортно заниматься."},
                    "walking": {"score": 0.92, "reason": "Самая безопасная активность почти в любую погоду."},
                    "cycling": {"score": 0.65, "reason": "Может мешать ветер."},
                    "yoga": {"score": 0.88, "reason": "Хороший вариант для восстановления."},
                    "picnic": {"score": 0.7, "reason": "Зависит от осадков."},
                    "stay_home": {"score": 0.25, "reason": "Не самый удачный день для улицы."}
                }
            })
        return fallback