# LangGraph Weather Agent

This is a small LangGraph example that uses a Groq chat model with a custom weather tool.

The weather tool is not calling a real weather API. It returns fixed sample responses for a few cities, which keeps the project simple and makes it easier to understand how tool calling works.

## What It Does

- Loads a Groq model using `GROQ_API_KEY`
- Creates a simple weather tool
- Lets the model decide when to call the tool
- Sends the tool result back to the model
- Keeps conversation state using LangGraph memory

## Setup

Install the required packages:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project folder. You can copy the example file and replace the placeholder value:

```env
GROQ_API_KEY=your_api_key_here
```

You can create a Groq API key from:

```text
https://console.groq.com/keys
```

## Run

Ask a question from the terminal:

```powershell
python weather_agent.py "what is the weather in delhi?"
```

You can also ask for other cities:

```powershell
python weather_agent.py "what is the weather in indore?"
python weather_agent.py "what is the weather in bengaluru?"
```

## Notes

The default model is:

```text
llama-3.3-70b-versatile
```

The older model used in the class notebook, `deepseek-r1-distill-llama-70b`, is no longer supported by Groq, so this project uses the newer model instead.

If the script says the API key is missing, check that `.env` is in the same folder as `weather_agent.py` and that the key name is exactly `GROQ_API_KEY`.
