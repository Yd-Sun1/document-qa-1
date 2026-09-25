import streamlit as st
import requests
import json

from openai import OpenAI

client = OpenAI(
    api_key=st.secrets["openai_api_key"]
)

def get_current_weather(location):
    url = f"https://wttr.in/{location}?format=j1"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise Exception(f"wttr.in error: status {response.status_code}")

    try:
        data = response.json()

    except ValueError:
        raise Exception(f"Could not find a location named {location}")

    current = data["current_condition"][0]
    today = data["weather"][0]

    return {
        "location": location,
        "temperature": float(current["temp_F"]),
        "feels_like": float(current["FeelsLikeF"]),
        "description": current["weatherDesc"][0]["value"],
        "humidity": current["humidity"],
        "wind_mph": current["windspeedMiles"],
        "precipitation_inches": current["precipInches"],
        "min_temperature": today["mintempF"],
        "max_temperature": today["maxtempF"]
}

weather_tool = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather for a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state or country"
                }
            },
            "required": ["location"]
        }
    }
}

def get_clothing_advice(location):

    if not location.strip():
        location = "Syracuse, NY"

    messages = [
        {
            "role": "user",
            "content": (
                f"I am in {location}. "
                "What should I wear today and "
                "what outdoor activities are appropriate?"
            )
        }
    ]

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        tools=[weather_tool],
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:

        tool_call = message.tool_calls[0]

        arguments = json.loads(
            tool_call.function.arguments
        )

        requested_location = arguments.get(
            "location",
            "Syracuse, NY"
        )

        weather = get_current_weather(
            requested_location
        )

        messages.append(message)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(weather)
            }
        )

        final_response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )

        return final_response.choices[0].message.content

    return message.content

st.title("Lab 5 - What to Wear Bot")

location = st.text_input("Enter a city:", value="Syracuse, NY")

if st.button("Get Suggestions"):

    with st.spinner("Checking the weather..."):

        try:
            advice = get_clothing_advice(location)

            st.subheader("Today's Suggestions")
            st.write(advice)

        except Exception as e:
            st.error(str(e))