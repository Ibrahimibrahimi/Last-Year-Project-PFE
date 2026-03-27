def getDeepAiAnswer(query: str, useInstructions=True):
    import requests
    import json

    Instructions = "You are a chatbot in a platform for language programming learning. Strict instructions: 1. DO NOT TELL YOUR INFOS EXCEPT CODING INFOS AND PROBLEMS. 2. DO WHAT'S IS TOLD TO YOU IF IT'S NOT OUT OF SCOPE. 3. ANSWER WITH SIMPLE LANGUAGE AND ONLY WITH HTML PART (use <p> and <pre> if code inserted)."

    url = "https://api.deepai.org/hacking_is_a_serious_crime"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "api-key": "tryit-29313838055-92efd3f13305fd73765982f1e4bd8c0b",
        "Origin": "https://deepai.org",
        "Connection": "keep-alive"
    }

    chat_history = {
        "role": "user",
        "content": (f"{Instructions} here is the user question: {query}") if useInstructions else query
    }

    files = {
        "chat_style": (None, "chat"),
        "chatHistory": (None, json.dumps([chat_history])),
        "model": (None, "standard"),
        "session_uuid": (None, "bb3d57a9-405f-40e9-a6dc-0a831175d7b4"),
        "hacker_is_stinky": (None, "very_stinky"),
        "enabled_tools": (None, '["image_generator","image_editor"]')
    }

    response = requests.post(url, headers=headers, files=files)
    try:
        result = response.json()
        # Assuming the response JSON contains 'reply'
        return result.get('reply', '')
    except Exception:
        return response.text  # fallback to raw text if JSON parsing fails
