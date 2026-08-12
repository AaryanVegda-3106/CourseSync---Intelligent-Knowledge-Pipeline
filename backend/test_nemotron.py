import asyncio
import os
from openai import AsyncOpenAI
import time

async def main():
    api_key = "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"
    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )
    start = time.time()
    try:
        response = await client.chat.completions.create(
            model="nvidia/nemotron-mini-4b-instruct",
            messages=[{"role": "user", "content": "Hello, respond with a quick test message."}],
            temperature=0.2,
            max_tokens=100
        )
        print("Success:", response.choices[0].message.content)
        print(f"Time: {time.time() - start:.2f}s")
    except Exception as e:
        print("Error:", e)
        print(f"Time: {time.time() - start:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
