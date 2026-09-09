\# Sovereign AI Workbench – Backend API



\## Base URL



```text

http://127.0.0.1:8000

```



The backend runs locally using FastAPI and Ollama.



\---



\## 1. Health Check



\### Endpoint



```text

GET /

```



\### Purpose



Checks whether the backend is running.



\### Example Response



```json

{

&#x20; "message": "Sovereign AI Workbench Backend is running!"

}

```



\---



\## 2. Ask AI



\### Endpoint



```text

POST /ask

```



\### Purpose



Accepts a user prompt and automatically selects a suitable local AI model using the Model Router.



\### Request



```json

{

&#x20; "prompt": "Write a Python program to add two numbers"

}

```



\### Example Response



```json

{

&#x20; "task": "coding",

&#x20; "model": "qwen2.5-coder:3b",

&#x20; "response": "..."

}

```



\### Supported Routing



| Task               | Local Model      |

| ------------------ | ---------------- |

| Coding             | qwen2.5-coder:3b |

| General / Document | llama3.2:3b      |

| Vision             | gemma3:4b        |



\---



\## 3. Agent



\### Endpoint



```text

POST /agent

```



\### Purpose



Runs an agent that can plan and execute multiple steps using local tools.



\### Request



```json

{

&#x20; "prompt": "Calculate 25 + 15"

}

```



\### Example Response



```json

{

&#x20; "response": "The calculation result is: 40.0"

}

```



\### Available Agent Tools



\* File reading

\* Calculator

\* Python code execution

\* Local AI model interaction



The agent also supports simple multi-step planning.



\---



\## 4. Vision



\### Endpoint



```text

POST /vision

```



\### Purpose



Accepts an image and uses the local Gemma vision model to analyze it.



\### Parameters



```text

prompt

```



Optional text instruction for the image.



```text

image

```



Required image file.



\### Example Prompt



```text

Describe this image and identify the main elements visible in it.

```



\### Example Response



```json

{

&#x20; "task": "vision",

&#x20; "model": "gemma3:4b",

&#x20; "filename": "example.png",

&#x20; "response": "..."

}

```



\---



\## 5. Local AI Architecture



```text

Frontend

&#x20;  |

&#x20;  v

FastAPI Backend

&#x20;  |

&#x20;  +---- Model Router

&#x20;  |       |

&#x20;  |       +---- Coding -> qwen2.5-coder:3b

&#x20;  |       |

&#x20;  |       +---- General -> llama3.2:3b

&#x20;  |       |

&#x20;  |       +---- Vision -> gemma3:4b

&#x20;  |

&#x20;  +---- Agent

&#x20;  |       |

&#x20;  |       +---- File Tool

&#x20;  |       +---- Calculator Tool

&#x20;  |       +---- Python Tool

&#x20;  |

&#x20;  v

Ollama

&#x20;  |

&#x20;  v

Local AI Models

```



\## 6. Local Deployment



The AI inference service is provided by Ollama running locally.



Ollama listens on:



```text

127.0.0.1:11434

```



This allows the backend to communicate with the local models without requiring a cloud AI API for inference.



\## 7. Testing Status



The following backend functions have been tested successfully:



\* FastAPI server

\* Model Router

\* Coding model

\* General model

\* Vision model

\* `/ask` endpoint

\* `/agent` endpoint

\* `/vision` endpoint

\* Calculator tool

\* File tool

\* Python execution tool

\* Multi-step agent planning

\* Agent logging

\* Local Ollama inference



\## 8. Frontend Integration



The frontend can communicate with the backend using the API endpoints described above.



For normal AI requests:



```text

POST /ask

```



For agent requests:



```text

POST /agent

```



For image analysis:



```text

POST /vision

```



The frontend should send requests to:



```text

http://127.0.0.1:8000

```



