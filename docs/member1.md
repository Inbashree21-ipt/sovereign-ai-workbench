\# Member 1 — Backend and Local AI



\## Role



Member 1 is responsible for the backend and local AI infrastructure of the

Sovereign On-Premise Agentic AI Workbench.



\## Responsibilities



\- Build the Python/FastAPI backend.

\- Integrate local open-weight AI models using Ollama.

\- Implement automatic model selection.

\- Integrate the agent with backend APIs.

\- Implement local AI tools.

\- Add multi-step task planning and execution.

\- Add execution logging.

\- Verify that AI inference is performed through the local Ollama server.



\## Local AI Models



The project currently uses three local models:



| Model | Purpose |

|---|---|

| qwen2.5-coder:3b | Coding and programming tasks |

| llama3.2:3b | General and document-related tasks |

| gemma3:4b | Image and vision tasks |



\## Model Router



The model router analyzes the user's prompt and selects an appropriate

local model.



Example:



Coding request

→ qwen2.5-coder:3b



Document/general request

→ llama3.2:3b



Image/vision request

→ gemma3:4b



The current router uses deterministic keyword-based task classification.



\## Backend



The backend is implemented using FastAPI.



Main API endpoints:



\### GET /



Checks whether the backend is running.



\### POST /ask



Accepts a user prompt, selects the appropriate local model, sends the

request to Ollama, and returns the response.



\### POST /agent



Sends a task to the local agent. The agent creates a plan and executes

the required local tools.



\### POST /vision



Accepts an image and sends it to the local Gemma vision model for analysis.



\## Agent



The agent supports multi-step task execution.



Example:



User request:



"Read the file test.txt and calculate 25 + 15"



The planner creates:



1\. File step

2\. Calculator step



The agent then executes both steps and combines the results.



\## Local Tools



The current agent includes:



\### File Tool



Reads local text files from the machine.



\### Calculator Tool



Performs:



\- Addition

\- Subtraction

\- Multiplication

\- Division



\### Python Code Tool



Executes Python code locally with a basic timeout mechanism.



Note: This is a prototype execution tool and is not considered a

fully isolated security sandbox. A proper sandbox can be integrated

by the security/agent team later.



\## Execution Logging



Agent activity is recorded in:



`logs/agent.log`



The log records:



\- Agent requests

\- Generated plans

\- Planned steps

\- Tool execution

\- Selected local models

\- Agent completion



Example:



Agent request

→ Plan created

→ File tool executed

→ Local model selected

→ Calculator executed

→ Agent completed



\## Local Inference Verification



Ollama is running locally on:



`127.0.0.1:11434`



The local server was verified using:



`Get-NetTCPConnection -LocalPort 11434`



Result:



`127.0.0.1:11434 — Listen`



This confirms that the backend communicates with the local Ollama

inference server.



\## Testing



The model router was tested with:



\- Coding request → qwen2.5-coder:3b

\- Document request → llama3.2:3b

\- Image request → gemma3:4b



The multi-step agent was tested with:



"Read the file test.txt and calculate 25 + 15"



Result:



\- Local document processed successfully.

\- Calculation completed successfully.

\- Calculation result: 40.0



The `/agent` FastAPI endpoint was also tested through Swagger UI and

returned HTTP 200 successfully.



\## GitHub



All Member 1 backend changes are maintained in the common GitHub

repository.



Repository:



`sovereign-ai-workbench`



The working tree is currently clean and the latest changes have been

pushed to the `main` branch.

