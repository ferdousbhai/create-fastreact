# Add AI Features to Your FastReact App

Integrate GPT-4, embeddings, image generation, and more—all in Python.

This is where FastReact shines. While JavaScript developers struggle with limited AI libraries and bindings, you have access to the entire Python ML ecosystem:

- **OpenAI** - GPT-4, DALL-E, Whisper, embeddings
- **Anthropic** - Claude models
- **Hugging Face** - Thousands of open-source models
- **LangChain** - Chains, agents, and RAG pipelines

Let's add AI features to your FastReact app.

## Prerequisites

- A FastReact project with backend deployed to Modal (or running locally)
- An [OpenAI API key](https://platform.openai.com/api-keys) (for OpenAI examples)
- Basic familiarity with async Python

## Add OpenAI Chat Completions

Let's start with the most common use case: GPT-4 chat.

### Step 1: Add Dependencies

Update your `backend/pyproject.toml`:

```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "modal>=0.68.0",
    "uvicorn>=0.32.0",
    "openai>=1.0.0",  # Add this
]
```

Install locally:

```bash
cd backend
uv sync
```

### Step 2: Create the Chat Endpoint

Add to `backend/app/main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# ... existing code ...

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "You are a helpful assistant."

class ChatResponse(BaseModel):
    reply: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.message},
            ],
        )
        return ChatResponse(reply=response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 3: Set Up Secrets in Modal

Modal handles secrets securely. Create a secret in the Modal dashboard:

1. Go to [modal.com/secrets](https://modal.com/secrets)
2. Click "Create new secret"
3. Name it `openai-secret`
4. Add key: `OPENAI_API_KEY` with your API key value

Update `backend/modal_app.py` to use the secret:

```python
import modal

app = modal.App("my-app-backend")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("uv")
    .add_local_file("pyproject.toml", "/app/pyproject.toml")
    .add_local_dir("app", "/app/app")
    .run_commands("cd /app && uv pip install --system -r pyproject.toml")
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("openai-secret")],  # Add this
)
@modal.asgi_app(requires_proxy_auth=True)
def fastapi_app():
    from app.main import app

    return app
```

### Step 4: Build the Chat UI

Create `frontend/src/Chat.tsx`:

```tsx
import { useState } from "react";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await api<{ reply: string }>("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message: input }),
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: data.reply,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-[500px] w-full max-w-2xl flex-col rounded-lg border">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`rounded-lg p-3 ${
              msg.role === "user"
                ? "ml-auto bg-blue-600 text-white"
                : "mr-auto bg-gray-100 text-gray-900"
            } max-w-[80%]`}
          >
            {msg.content}
          </div>
        ))}
        {loading && (
          <div className="mr-auto bg-gray-100 text-gray-500 rounded-lg p-3">
            Thinking...
          </div>
        )}
      </div>

      <div className="border-t p-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type a message..."
          className="flex-1 rounded-md border px-4 py-2 focus:border-blue-500 focus:outline-none"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
```

## Add Text Embeddings

Embeddings power semantic search, recommendations, and RAG pipelines.

### Backend Endpoint

```python
class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: list[float]

@app.post("/api/embed", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest):
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=request.text,
    )

    return EmbeddingResponse(embedding=response.data[0].embedding)
```

### Use Case: Semantic Search

Store embeddings in a vector database, then find similar content:

```python
import numpy as np
from pydantic import BaseModel

# In-memory store (use a real vector DB in production)
documents: list[dict] = []

class Document(BaseModel):
    content: str

@app.post("/api/documents")
async def add_document(doc: Document):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=doc.content,
    )

    documents.append({
        "content": doc.content,
        "embedding": response.data[0].embedding,
    })

    return {"status": "added", "count": len(documents)}

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

@app.post("/api/search")
async def search_documents(request: SearchRequest):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Get query embedding
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=request.query,
    )
    query_embedding = np.array(response.data[0].embedding)

    # Calculate similarities
    results = []
    for doc in documents:
        doc_embedding = np.array(doc["embedding"])
        similarity = np.dot(query_embedding, doc_embedding)
        results.append({"content": doc["content"], "score": float(similarity)})

    # Sort by similarity
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[: request.top_k]
```

## Run Hugging Face Models on GPU

Modal makes GPU inference trivial. Run any Hugging Face model:

### Image with Transformers

Update your `modal_app.py`:

```python
import modal

app = modal.App("my-app-backend")

# Image with ML dependencies
ml_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "fastapi",
        "transformers",
        "torch",
        "accelerate",
    )
)

@app.function(image=ml_image, gpu="T4")
@modal.web_endpoint()
def analyze_sentiment(text: str):
    from transformers import pipeline

    classifier = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )
    result = classifier(text)[0]

    return {
        "label": result["label"],
        "confidence": result["score"],
    }
```

### Text Generation with LLaMA

```python
@app.function(
    image=ml_image,
    gpu="A10G",
    timeout=300,
)
@modal.web_endpoint()
def generate_text(prompt: str, max_tokens: int = 100):
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch

    model_name = "meta-llama/Llama-2-7b-chat-hf"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=max_tokens)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return {"generated": response}
```

## Image Generation with DALL-E

```python
class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"

@app.post("/api/generate-image")
async def generate_image(request: ImageRequest):
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.images.generate(
        model="dall-e-3",
        prompt=request.prompt,
        size=request.size,
        quality="standard",
        n=1,
    )

    return {"url": response.data[0].url}
```

### Frontend Component

```tsx
import { useState } from "react";
import { api } from "@/lib/api";

export default function ImageGenerator() {
  const [prompt, setPrompt] = useState("");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function generate() {
    if (!prompt.trim() || loading) return;
    setLoading(true);

    try {
      const data = await api<{ url: string }>("/api/generate-image", {
        method: "POST",
        body: JSON.stringify({ prompt }),
      });
      setImageUrl(data.url);
    } catch (error) {
      console.error("Generation error:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-4 w-full max-w-2xl">
      <div className="flex gap-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="A futuristic city at sunset..."
          className="flex-1 rounded-md border px-4 py-2"
        />
        <button
          onClick={generate}
          disabled={loading}
          className="rounded-md bg-purple-600 px-4 py-2 text-white"
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>

      {imageUrl && (
        <img
          src={imageUrl}
          alt={prompt}
          className="rounded-lg w-full"
        />
      )}
    </div>
  );
}
```

## Streaming Responses

For long AI responses, stream them to improve UX:

### Backend with Streaming

```python
from fastapi.responses import StreamingResponse

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def generate():
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.message},
            ],
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")
```

### Frontend with Streaming

```typescript
async function streamChat(message: string) {
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  let fullResponse = "";

  while (reader) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    fullResponse += chunk;

    // Update UI with each chunk
    setStreamingMessage(fullResponse);
  }
}
```

## Best Practices

### 1. Cache Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_embedding(text: str) -> list[float]:
    # This result is cached
    ...
```

### 2. Handle Rate Limits

```python
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_openai_with_retry(messages):
    ...
```

### 3. Use Appropriate Models

| Task | Recommended Model |
|------|-------------------|
| Chat | gpt-4o (smart) or gpt-4o-mini (fast) |
| Embeddings | text-embedding-3-small |
| Images | dall-e-3 |
| Code | gpt-4o |

### 4. Secure Your API Keys

Never expose API keys to the frontend. Always call AI services from your backend.

## Next Steps

You've added AI to your FastReact app! Explore more:

- [LangChain Documentation](https://python.langchain.com/) - Build complex AI pipelines
- [Hugging Face Hub](https://huggingface.co/models) - Discover open-source models
- [Modal GPU Guide](https://modal.com/docs/guide/gpu) - Optimize GPU usage

---

**The Python AI ecosystem is yours.** No JavaScript limitations. No second-class bindings. Just import and build.
