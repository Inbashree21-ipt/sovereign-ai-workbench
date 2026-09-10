"""
ReAct Autonomous Agent Core Engine
SIH Problem Statement 26117

Flow:
1. Plan
2. Act
3. Observe
4. Repeat
5. Produce final answer / deliverable

Runs locally using Ollama.
"""

import re
import json
import time
import urllib.request
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field

from config import OLLAMA_BASE_URL, DEFAULT_MODEL, MAX_AGENT_STEPS
from tools.registry import ToolRegistry, get_default_registry
from tools.base import ToolResult
from agent.prompts import REACT_SYSTEM_PROMPT, SOVEREIGN_USER_PROMPT_TEMPLATE
from agent.router import ModelRouter


@dataclass
class AgentStep:
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    duration_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "duration_sec": round(self.duration_sec, 3),
        }


@dataclass
class AgentExecutionResult:
    task: str
    final_answer: str
    success: bool
    steps: List[AgentStep] = field(default_factory=list)
    total_duration_sec: float = 0.0
    model_used: str = ""
    task_type: str = ""
    deliverables: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "final_answer": self.final_answer,
            "success": self.success,
            "total_duration_sec": round(self.total_duration_sec, 2),
            "model_used": self.model_used,
            "task_type": self.task_type,
            "deliverables": self.deliverables,
            "steps": [s.to_dict() for s in self.steps],
        }


class ReActAgent:
    """
    Autonomous ReAct agent powered by local Ollama models.
    """

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        router: Optional[ModelRouter] = None,
        base_url: str = OLLAMA_BASE_URL,
        max_steps: int = MAX_AGENT_STEPS,
        step_callback: Optional[Callable[[AgentStep], None]] = None,
    ):
        self.registry = registry or get_default_registry()
        self.router = router or ModelRouter(base_url=base_url)
        self.base_url = base_url
        self.max_steps = max_steps
        self.step_callback = step_callback

    # ============================================================
    # OLLAMA
    # ============================================================

    def _call_ollama(
        self,
        model: str,
        endpoint: str,
        prompt: str
    ) -> str:

        url = f"{endpoint}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 400,
                "stop": [
                    "Observation:",
                    "Observation :",
                    "\nObservation",
                    "Observation",
                ],
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
        )

        with urllib.request.urlopen(req, timeout=180) as resp:

            data = json.loads(
                resp.read().decode("utf-8")
            )

            response_text = data.get(
                "response",
                ""
            ).strip()

            if not response_text and data.get("thinking"):
                response_text = data.get(
                    "thinking",
                    ""
                ).strip()

            return response_text

    # ============================================================
    # PARSE REACT OUTPUT
    # ============================================================

    def _parse_react_output(
        self,
        text: str
    ) -> Tuple[
        str,
        Optional[str],
        Optional[Dict[str, Any]],
        Optional[str]
    ]:

        clean_text = re.sub(
            r"<think>.*?</think>",
            "",
            text,
            flags=re.DOTALL
        ).strip()

        if not clean_text:
            clean_text = text

        thought = ""
        action = None
        action_input = None
        final_answer = None

        # --------------------------------------------------------
        # Final Answer
        # --------------------------------------------------------

        fa_match = re.search(
            r"Final Answer\s*:\s*(.*)",
            clean_text,
            re.DOTALL | re.IGNORECASE
        )

        if fa_match:

            final_answer = fa_match.group(1).strip()

            t_match = re.search(
                r"Thought\s*:\s*(.*?)(?=Final Answer\s*:|$)",
                clean_text,
                re.DOTALL | re.IGNORECASE
            )

            thought = (
                t_match.group(1).strip()
                if t_match
                else ""
            )

            return (
                thought,
                None,
                None,
                final_answer
            )

        # --------------------------------------------------------
        # Thought
        # --------------------------------------------------------

        t_match = re.search(
            r"Thought\s*:\s*(.*?)(?=Action\s*:|$)",
            clean_text,
            re.DOTALL | re.IGNORECASE
        )

        if t_match:

            thought = t_match.group(1).strip()

        else:

            if "Action:" in clean_text:

                thought = clean_text.split(
                    "Action:"
                )[0].strip()

            else:

                thought = clean_text

        # --------------------------------------------------------
        # Action
        # --------------------------------------------------------

        a_match = re.search(
            r"Action\s*:\s*([a-zA-Z0-9_\-]+)",
            clean_text,
            re.IGNORECASE
        )

        if a_match:

            action = a_match.group(1).strip()

        else:

            # Fallback detection
            known_tools = [
                "read_file",
                "search_company_knowledge",
                "analyze_spreadsheet",
                "execute_python_code",
                "generate_deliverable",
                "verify_airgap_sovereignty",
                "list_files",
            ]

            for tool_name in known_tools:

                if not re.search(
                    r"\b" + tool_name + r"\b",
                    clean_text,
                    re.IGNORECASE
                ):
                    continue

                # File tools
                if tool_name in [
                    "read_file",
                    "analyze_spreadsheet"
                ]:

                    path_match = re.search(
                        r"['\"]([a-zA-Z0-9_\-/\\]+\."
                        r"(?:txt|csv|xlsx|md|docx))['\"]",
                        clean_text
                    )

                    if path_match:

                        action = tool_name

                        action_input = {
                            "file_path": path_match.group(1)
                        }

                        break

                # RAG
                elif tool_name == "search_company_knowledge":

                    q_match = re.search(
                        r"(?:query|search)[:\s]+"
                        r"['\"]([^'\"]+)['\"]",
                        clean_text,
                        re.IGNORECASE
                    )

                    query_text = (
                        q_match.group(1)
                        if q_match
                        else "pipeline safety and minimum allowable wall thickness"
                    )

                    action = tool_name

                    action_input = {
                        "query": query_text,
                        "top_k": 5
                    }

                    break

                # Airgap
                elif tool_name == "verify_airgap_sovereignty":

                    action = tool_name
                    action_input = {}

                    break

        # --------------------------------------------------------
        # Action Input
        # --------------------------------------------------------

        if action and not action_input:

            ai_match = re.search(
                r"Action Input\s*:\s*(.*)",
                clean_text,
                re.DOTALL | re.IGNORECASE
            )

            if ai_match:

                raw_input = ai_match.group(1).strip()

                if "```" in raw_input:

                    cleaned = re.sub(
                        r"```(?:json)?(.*?)```",
                        r"\1",
                        raw_input,
                        flags=re.DOTALL
                    ).strip()

                else:

                    cleaned = raw_input

                json_candidate = cleaned

                if not json_candidate.startswith("{"):

                    if "{" in json_candidate:

                        json_candidate = (
                            json_candidate[
                                json_candidate.find("{"):
                            ]
                        )

                if "}" in json_candidate:

                    json_candidate = (
                        json_candidate[
                            :json_candidate.rfind("}") + 1
                        ]
                    )

                try:

                    action_input = json.loads(
                        json_candidate
                    )

                except Exception:

                    action_input = {}

        return (
            thought,
            action,
            action_input,
            final_answer
        )

    # ============================================================
    # CHECK DELIVERABLE REQUEST
    # ============================================================

    def _deliverable_requested(
        self,
        user_prompt: str
    ) -> bool:

        prompt = user_prompt.lower()

        keywords = [
            "create",
            "generate",
            "write",
            "report",
            "word",
            "document",
            "approval note",
            "deliverable",
            "excel",
            "spreadsheet",
            "ppt",
            "powerpoint",
            "presentation",
        ]

        return any(
            keyword in prompt
            for keyword in keywords
        )

    # ============================================================
    # NORMALIZE DOCUMENT INPUT
    # ============================================================

    def _prepare_deliverable_args(
        self,
        tool_args: Dict[str, Any],
        previous_observation: str,
        user_prompt: str
    ) -> Dict[str, Any]:

        args = dict(tool_args)

        # --------------------------------------------------------
        # Format
        # --------------------------------------------------------

        doc_format = str(
            args.get("format", "docx")
        ).lower()

        if doc_format not in [
            "docx",
            "xlsx"
        ]:

            doc_format = "docx"

        args["format"] = doc_format

        # --------------------------------------------------------
        # Filename
        # --------------------------------------------------------

        filename = str(
            args.get(
                "filename",
                "Sovereign_AI_Deliverable"
            )
        ).strip()

        # Remove existing extension before adding it
        filename = re.sub(
            r"\.(docx|xlsx)$",
            "",
            filename,
            flags=re.IGNORECASE
        )

        # Make filename Windows-safe
        filename = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            filename
        )

        if not filename:

            filename = "Sovereign_AI_Deliverable"

        args["filename"] = (
            filename + "." + doc_format
        )

        # --------------------------------------------------------
        # Title
        # --------------------------------------------------------

        title = str(
            args.get(
                "title",
                "Sovereign AI Workbench Deliverable"
            )
        ).strip()

        if not title:

            title = "Sovereign AI Workbench Deliverable"

        args["title"] = title

        # --------------------------------------------------------
        # Word sections
        # --------------------------------------------------------

        if doc_format == "docx":

            sections = args.get(
                "sections",
                []
            )

            normalized_sections = []

            if isinstance(
                sections,
                list
            ):

                for index, section in enumerate(
                    sections,
                    start=1
                ):

                    # Correct format:
                    # {"heading": "...", "body": "..."}
                    if isinstance(
                        section,
                        dict
                    ):

                        heading = str(
                            section.get(
                                "heading",
                                f"Section {index}"
                            )
                        )

                        body = str(
                            section.get(
                                "body",
                                ""
                            )
                        )

                        normalized_sections.append(
                            {
                                "heading": heading,
                                "body": body
                            }
                        )

                    # If model sends a plain string
                    elif isinstance(
                        section,
                        str
                    ):

                        normalized_sections.append(
                            {
                                "heading": f"Section {index}",
                                "body": section
                            }
                        )

                       # ----------------------------------------------------
                       # If model supplied no useful sections OR
                       # the sections have empty bodies, use the RAG observation.
                       # ----------------------------------------------------

                        # ----------------------------------------------------
            # Detect empty sections OR outline-only sections.
            # Example:
            #   Section 1 -> Introduction
            #   Section 2 -> Safety Requirements
            #   Section 3 -> Conclusion
            #
            # These are headings, not actual document content.
            # Use the RAG observation instead.
            # ----------------------------------------------------

            outline_only = (
                normalized_sections
                and all(
                    section.get("heading", "")
                    .strip()
                    .lower()
                    .startswith("section ")
                    and section.get("body", "").strip()
                    for section in normalized_sections
                )
            )

            if (
                not normalized_sections
                or all(
                    not section.get("body", "").strip()
                    for section in normalized_sections
                )
                or outline_only
            ):
                rag_observation = str(
                    previous_observation or ""
                ).strip()

                if rag_observation:
                    normalized_sections = [
                        {
                            "heading": "Pipeline Safety Findings",
                            "body": rag_observation
                        },
                        {
                            "heading": "Requested Task",
                            "body": user_prompt
                        }
                    ]
                else:
                    normalized_sections = []

            args["sections"] = normalized_sections

        # --------------------------------------------------------
        # Excel table data
        # --------------------------------------------------------

        if doc_format == "xlsx":

            table_data = args.get(
                "table_data",
                []
            )

            if not isinstance(
                table_data,
                list
            ):

                table_data = []

            args["table_data"] = table_data

        return args

    # ============================================================
    # MAIN AGENT LOOP
    # ============================================================

    def run(
        self,
        user_prompt: str,
        task_type: Optional[str] = None
    ) -> AgentExecutionResult:

        start_time = time.time()

        steps: List[AgentStep] = []

        deliverables: List[str] = []

        # --------------------------------------------------------
        # Route to local model
        # --------------------------------------------------------

        model_name, endpoint, route_meta = (
            self.router.route(
                user_prompt,
                task_type=task_type
            )
        )

        actual_task_type = route_meta[
            "task_type"
        ]

        # --------------------------------------------------------
        # Prepare system prompt
        # --------------------------------------------------------

        tool_descriptions = (
            self.registry.format_react_prompt()
        )

        system_content = (
            REACT_SYSTEM_PROMPT.format(
                tool_descriptions=tool_descriptions
            )
        )

        user_content = (
            SOVEREIGN_USER_PROMPT_TEMPLATE.format(
                user_prompt=user_prompt
            )
        )

        running_history = (
            f"{system_content}\n\n"
            f"{user_content}"
        )

        final_answer = None

        previous_observation = ""

        deliverable_requested = (
            self._deliverable_requested(
                user_prompt
            )
        )

        # --------------------------------------------------------
        # ReAct Loop
        # --------------------------------------------------------

        for step_idx in range(
            1,
            self.max_steps + 1
        ):

            step_start = time.time()

            # ----------------------------------------------------
            # Model inference
            # ----------------------------------------------------

            try:

                response = self._call_ollama(
                    model=model_name,
                    endpoint=endpoint,
                    prompt=running_history
                )

            except Exception as e:

                err_msg = (
                    f"[OLLAMA INFERENCE ERROR] "
                    f"Could not reach model "
                    f"'{model_name}' at {endpoint}: "
                    f"{str(e)}"
                )

                step = AgentStep(
                    step_number=step_idx,
                    thought=(
                        "Error connecting to "
                        "local model."
                    ),
                    observation=err_msg,
                    duration_sec=(
                        time.time() -
                        step_start
                    ),
                )

                steps.append(step)

                return AgentExecutionResult(
                    task=user_prompt,
                    final_answer=err_msg,
                    success=False,
                    steps=steps,
                    total_duration_sec=(
                        time.time() -
                        start_time
                    ),
                    model_used=model_name,
                    task_type=actual_task_type,
                    deliverables=deliverables,
                )

            # ----------------------------------------------------
            # Parse response
            # ----------------------------------------------------

            (
                thought,
                action,
                action_input,
                fa
            ) = self._parse_react_output(
                response
            )

            # ----------------------------------------------------
            # Final Answer
            # ----------------------------------------------------

            if fa:

                final_answer = fa

                step = AgentStep(
                    step_number=step_idx,
                    thought=(
                        thought or
                        "Goal completed."
                    ),
                    duration_sec=(
                        time.time() -
                        step_start
                    ),
                )

                steps.append(step)

                if self.step_callback:

                    self.step_callback(step)

                break

            # ----------------------------------------------------
            # No action
            # ----------------------------------------------------

            if not action:

                final_answer = response

                step = AgentStep(
                    step_number=step_idx,
                    thought=(
                        thought or
                        "Produced direct response."
                    ),
                    duration_sec=(
                        time.time() -
                        step_start
                    ),
                )

                steps.append(step)

                if self.step_callback:

                    self.step_callback(step)

                break

            # ----------------------------------------------------
            # Prepare arguments
            # ----------------------------------------------------

            tool_args = (
                action_input
                if isinstance(
                    action_input,
                    dict
                )
                else {}
            )

            # ----------------------------------------------------
            # IMPORTANT:
            # If generating a deliverable, normalize
            # the model's arguments before execution.
            # ----------------------------------------------------

            if action == "generate_deliverable":

                tool_args = (
                    self._prepare_deliverable_args(
                        tool_args,
                        previous_observation,
                        user_prompt
                    )
                )

            # ----------------------------------------------------
            # Execute tool
            # ----------------------------------------------------

            tool_res: ToolResult = (
                self.registry.execute_tool(
                    action,
                    **tool_args
                )
            )

            observation = (
                tool_res.output
                if tool_res.success
                else (
                    f"Error: {tool_res.error}"
                )
            )

            previous_observation = observation

            # ----------------------------------------------------
            # Track deliverables
            # ----------------------------------------------------

            if (
                action ==
                "generate_deliverable"
                and
                tool_res.success
            ):

                filename = tool_args.get(
                    "filename",
                    ""
                )

                if filename:

                    deliverables.append(
                        filename
                    )

            # ----------------------------------------------------
            # Create step record
            # ----------------------------------------------------

            step_duration = (
                time.time() -
                step_start
            )

            step = AgentStep(
                step_number=step_idx,
                thought=thought,
                action=action,
                action_input=tool_args,
                observation=observation,
                duration_sec=step_duration,
            )

            steps.append(step)

            if self.step_callback:

                self.step_callback(step)

            # ====================================================
            # STOP CONDITION 1
            # Successful file read
            # ====================================================

            if (
                action == "read_file"
                and
                tool_res.success
            ):

                final_answer = observation

                break

            # ====================================================
            # STOP CONDITION 2
            # Successful spreadsheet analysis
            # ====================================================

            if (
                action ==
                "analyze_spreadsheet"
                and
                tool_res.success
            ):

                final_answer = observation

                break

            # ====================================================
            # STOP CONDITION 3
            # Successful file listing
            # ====================================================

            if (
                action == "list_files"
                and
                tool_res.success
            ):

                final_answer = observation

                break

            # ====================================================
            # STOP CONDITION 4
            # RAG search
            #
            # Only stop if the user did NOT request
            # a deliverable.
            # ====================================================

            if (
                action ==
                "search_company_knowledge"
                and
                tool_res.success
            ):

                if not deliverable_requested:

                    final_answer = observation

                    break

                # For deliverable requests:
                # continue to document generation.
                running_history += (
                    "\nIMPORTANT: The knowledge search "
                    "has completed successfully.\n"
                    "Use the retrieved information to "
                    "create the requested deliverable.\n"
                    "Do NOT invent Python functions.\n"
                    "Do NOT use execute_python_code "
                    "to create the Word document.\n"
                    "Use generate_deliverable directly.\n"
                )

            # ====================================================
            # STOP CONDITION 5
            # Successful deliverable generation
            #
            # THIS IS THE IMPORTANT FIX.
            # ====================================================

            if (
                action ==
                "generate_deliverable"
                and
                tool_res.success
            ):

                filename = tool_args.get(
                    "filename",
                    "deliverable"
                )

                final_answer = (
                    f"Successfully completed the task.\n\n"
                    f"Deliverable created: "
                    f"{filename}\n\n"
                    f"{observation}"
                )

                break

            # ====================================================
            # Append observation for next ReAct step
            # ====================================================

            obs_compact = observation

            if len(obs_compact) > 1200:

                obs_compact = (
                    obs_compact[:1200]
                    +
                    "\n... "
                    "[truncated for context efficiency]"
                )

            running_history += (
                f"\nThought: {thought}\n"
                f"Action: {action}\n"
                f"Action Input: "
                f"{json.dumps(tool_args)}\n"
                f"Observation: {obs_compact}\n"
            )

        # --------------------------------------------------------
        # Fallback if max steps reached
        # --------------------------------------------------------

        if not final_answer:

            last_obs = (
                steps[-1].observation
                if steps
                else "No observation available"
            )

            if deliverables:

                final_answer = (
                    f"Task completed after "
                    f"{len(steps)} steps.\n\n"
                    f"Deliverables created: "
                    f"{', '.join(deliverables)}\n\n"
                    f"Last observation:\n"
                    f"{last_obs}"
                )

            else:

                final_answer = (
                    f"Task completed after "
                    f"{len(steps)} steps.\n"
                    f"Last tool observation:\n"
                    f"{last_obs}"
                )

        # --------------------------------------------------------
        # Final result
        # --------------------------------------------------------

        total_duration = (
            time.time() -
            start_time
        )

        return AgentExecutionResult(
            task=user_prompt,
            final_answer=final_answer,
            success=True,
            steps=steps,
            total_duration_sec=total_duration,
            model_used=model_name,
            task_type=actual_task_type,
            deliverables=deliverables,
        )

