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


# ================================================================
# AGENT STEP
# ================================================================

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


# ================================================================
# AGENT EXECUTION RESULT
# ================================================================

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
            "steps": [
                s.to_dict()
                for s in self.steps
            ],
        }


# ================================================================
# REACT AGENT
# ================================================================

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
        step_callback: Optional[
            Callable[[AgentStep], None]
        ] = None,
    ):

        self.registry = (
            registry
            or get_default_registry()
        )

        self.router = (
            router
            or ModelRouter(
                base_url=base_url
            )
        )

        self.base_url = base_url

        self.max_steps = max_steps

        self.step_callback = step_callback

    # ============================================================
    # DETECT KNOWLEDGE BASE QUESTION
    # ============================================================

    def _is_knowledge_question(
        self,
        user_prompt: str
    ) -> bool:

        prompt = (
            user_prompt
            .lower()
            .strip()
        )

        knowledge_keywords = [

            "finding",

            "inspection",

            "inspection report",

            "pump",

            "pipeline",

            "maintenance",

            "safety",

            "sop",

            "standard operating procedure",

            "equipment",

            "leakage",

            "leak",

            "wall thickness",

            "pressure",

            "vessel",

            "hydro test",

            "hydro-test",

            "corrosion",

            "plant",

            "industrial",

            "engineering",

            "manual",

            "company knowledge",

            "company manual",

            "internal report",

            "internal document",

            "procedure",

            "compliance",

            "shutdown",

            "valve",

            "flange",

            "seal",

            "inspection finding",

            "maintenance report",
        ]

        return any(
            keyword in prompt
            for keyword in knowledge_keywords
        )

    # ============================================================
    # OLLAMA
    # ============================================================

    def _call_ollama(
        self,
        model: str,
        endpoint: str,
        prompt: str
    ) -> str:

        url = (
            f"{endpoint}/api/generate"
        )

        payload = {

            "model":
                model,

            "prompt":
                prompt,

            "stream":
                False,

            "think":
                False,

            "options": {

                "temperature":
                    0.1,

                "top_p":
                    0.9,

                "num_predict":
                    400,

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

            data=json.dumps(
                payload
            ).encode("utf-8"),

            headers={
                "Content-Type":
                    "application/json"
            },
        )

        with urllib.request.urlopen(
            req,
            timeout=180
        ) as resp:

            data = json.loads(
                resp.read().decode(
                    "utf-8"
                )
            )

            response_text = (
                data
                .get(
                    "response",
                    ""
                )
                .strip()
            )

            if (
                not response_text
                and
                data.get("thinking")
            ):

                response_text = (
                    data
                    .get(
                        "thinking",
                        ""
                    )
                    .strip()
                )

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
        # FINAL ANSWER
        # --------------------------------------------------------

        fa_match = re.search(
            r"Final Answer\s*:\s*(.*)",
            clean_text,
            re.DOTALL |
            re.IGNORECASE
        )

        if fa_match:

            final_answer = (
                fa_match
                .group(1)
                .strip()
            )

            t_match = re.search(
                r"Thought\s*:\s*(.*?)(?=Final Answer\s*:|$)",
                clean_text,
                re.DOTALL |
                re.IGNORECASE
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
        # THOUGHT
        # --------------------------------------------------------

        t_match = re.search(
            r"Thought\s*:\s*(.*?)(?=Action\s*:|$)",
            clean_text,
            re.DOTALL |
            re.IGNORECASE
        )

        if t_match:

            thought = (
                t_match
                .group(1)
                .strip()
            )

        else:

            if "Action:" in clean_text:

                thought = (
                    clean_text
                    .split(
                        "Action:"
                    )[0]
                    .strip()
                )

            else:

                thought = clean_text

        # --------------------------------------------------------
        # ACTION
        # --------------------------------------------------------

        a_match = re.search(
            r"Action\s*:\s*([a-zA-Z0-9_\-]+)",
            clean_text,
            re.IGNORECASE
        )

        if a_match:

            action = (
                a_match
                .group(1)
                .strip()
            )

        else:

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
                    r"\b"
                    + tool_name
                    + r"\b",
                    clean_text,
                    re.IGNORECASE
                ):

                    continue

                # ------------------------------------------------
                # FILE TOOLS
                # ------------------------------------------------

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

                            "file_path":
                                path_match.group(1)
                        }

                        break

                # ------------------------------------------------
                # RAG
                # ------------------------------------------------

                elif (
                    tool_name
                    ==
                    "search_company_knowledge"
                ):

                    q_match = re.search(

                        r"(?:query|search)[:\s]+"
                        r"['\"]([^'\"]+)['\"]",

                        clean_text,

                        re.IGNORECASE
                    )

                    query_text = (

                        q_match.group(1)

                        if q_match

                        else
                        "pipeline safety and minimum allowable wall thickness"
                    )

                    action = tool_name

                    action_input = {

                        "query":
                            query_text,

                        "top_k":
                            5
                    }

                    break

                # ------------------------------------------------
                # AIRGAP
                # ------------------------------------------------

                elif (
                    tool_name
                    ==
                    "verify_airgap_sovereignty"
                ):

                    action = tool_name

                    action_input = {}

                    break

        # --------------------------------------------------------
        # ACTION INPUT
        # --------------------------------------------------------

        if (
            action
            and
            not action_input
        ):

            ai_match = re.search(

                r"Action Input\s*:\s*(.*)",

                clean_text,

                re.DOTALL |
                re.IGNORECASE
            )

            if ai_match:

                raw_input = (
                    ai_match
                    .group(1)
                    .strip()
                )

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

        prompt = (
            user_prompt
            .lower()
            .strip()
        )

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
        # FORMAT
        # --------------------------------------------------------

        doc_format = str(

            args.get(
                "format",
                "docx"
            )

        ).lower()

        if doc_format not in [

            "docx",

            "xlsx"
        ]:

            doc_format = "docx"

        args["format"] = doc_format

        # --------------------------------------------------------
        # FILENAME
        # --------------------------------------------------------

        filename = str(

            args.get(

                "filename",

                "Sovereign_AI_Deliverable"
            )

        ).strip()

        filename = re.sub(

            r"\.(docx|xlsx)$",

            "",

            filename,

            flags=re.IGNORECASE
        )

        filename = re.sub(

            r'[<>:"/\\|?*]',

            "_",

            filename
        )

        if not filename:

            filename = (
                "Sovereign_AI_Deliverable"
            )

        args["filename"] = (

            filename
            +
            "."
            +
            doc_format
        )

        # --------------------------------------------------------
        # TITLE
        # --------------------------------------------------------

        title = str(

            args.get(

                "title",

                "Sovereign AI Workbench Deliverable"
            )

        ).strip()

        if not title:

            title = (
                "Sovereign AI Workbench Deliverable"
            )

        args["title"] = title

        # --------------------------------------------------------
        # WORD SECTIONS
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

                        normalized_sections.append({

                            "heading":
                                heading,

                            "body":
                                body
                        })

                    elif isinstance(
                        section,
                        str
                    ):

                        normalized_sections.append({

                            "heading":
                                f"Section {index}",

                            "body":
                                section
                        })

            # ----------------------------------------------------
            # DETECT EMPTY / USELESS SECTIONS
            # ----------------------------------------------------

            outline_only = (

                normalized_sections

                and

                all(

                    section.get(
                        "heading",
                        ""
                    )
                    .strip()
                    .lower()
                    .startswith(
                        "section "
                    )

                    and

                    section.get(
                        "body",
                        ""
                    ).strip()

                    for section
                    in normalized_sections
                )
            )

            if (

                not normalized_sections

                or

                all(

                    not section.get(
                        "body",
                        ""
                    ).strip()

                    for section
                    in normalized_sections
                )

                or

                outline_only
            ):

                rag_observation = str(

                    previous_observation
                    or
                    ""
                ).strip()

                if rag_observation:

                    normalized_sections = [

                        {

                            "heading":
                                "Pipeline Safety Findings",

                            "body":
                                rag_observation
                        },

                        {

                            "heading":
                                "Requested Task",

                            "body":
                                user_prompt
                        }
                    ]

                else:

                    normalized_sections = []

            args["sections"] = (
                normalized_sections
            )

        # --------------------------------------------------------
        # EXCEL TABLE DATA
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

        # ========================================================
        # ROUTE TO LOCAL MODEL
        # ========================================================

        if task_type is None:

            model_name, endpoint, route_meta = (
                self.router.route(
                    user_prompt
                )
            )

        else:

            model_name, endpoint, route_meta = (
                self.router.route(
                    user_prompt,
                    task_type=task_type
                )
            )

        actual_task_type = (
            route_meta[
                "task_type"
            ]
        )

        # ========================================================
        # PREPARE SYSTEM PROMPT
        # ========================================================

        tool_descriptions = (
            self.registry
            .format_react_prompt()
        )

        system_content = (
            REACT_SYSTEM_PROMPT.format(

                tool_descriptions=
                    tool_descriptions
            )
        )

        user_content = (
            SOVEREIGN_USER_PROMPT_TEMPLATE.format(

                user_prompt=
                    user_prompt
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

        # ========================================================
        # DETERMINISTIC KNOWLEDGE ROUTING
        # ========================================================
        #
        # IMPORTANT:
        #
        # Small local LLMs can sometimes incorrectly select
        # list_files for questions about company knowledge.
        #
        # Therefore, clear industrial/company knowledge questions
        # are routed directly to the RAG tool.
        #
        # Example:
        #
        # "What was the finding for Pump P-102?"
        #
        # -> search_company_knowledge
        #
        # No list_files.
        # No Python.
        # No unnecessary deliverable.
        #
        # ========================================================

        if (
            self._is_knowledge_question(
                user_prompt
            )
            and
            not deliverable_requested
        ):

            step_start = time.time()

            rag_query = (
                user_prompt.strip()
            )

            rag_args = {

                "query":
                    rag_query,

                "top_k":
                    5
            }

            tool_res: ToolResult = (
                self.registry
                .execute_tool(

                    "search_company_knowledge",

                    **rag_args
                )
            )

            observation = (

                tool_res.output

                if tool_res.success

                else
                f"Error: {tool_res.error}"
            )

            previous_observation = (
                observation
            )

            step = AgentStep(

                step_number=1,

                thought=(
                    "This is an industrial/company "
                    "knowledge question. Searching "
                    "the confidential knowledge base first."
                ),

                action=(
                    "search_company_knowledge"
                ),

                action_input=
                    rag_args,

                observation=
                    observation,

                duration_sec=(
                    time.time()
                    -
                    step_start
                ),
            )

            steps.append(step)

            if self.step_callback:

                self.step_callback(
                    step
                )

            if tool_res.success:

                final_answer = observation

            else:

                final_answer = (
                    f"Unable to search company knowledge: "
                    f"{tool_res.error}"
                )

            total_duration = (
                time.time()
                -
                start_time
            )

            return AgentExecutionResult(

                task=
                    user_prompt,

                final_answer=
                    final_answer,

                success=
                    tool_res.success,

                steps=
                    steps,

                total_duration_sec=
                    total_duration,

                model_used=
                    model_name,

                task_type=
                    actual_task_type,

                deliverables=
                    deliverables,
            )

        # ========================================================
        # REACT LOOP
        # ========================================================

        for step_idx in range(

            1,

            self.max_steps + 1
        ):

            step_start = time.time()

            # ----------------------------------------------------
            # MODEL INFERENCE
            # ----------------------------------------------------

            try:

                response = (
                    self._call_ollama(

                        model=model_name,

                        endpoint=endpoint,

                        prompt=running_history
                    )
                )

            except Exception as e:

                err_msg = (

                    f"[OLLAMA INFERENCE ERROR] "
                    f"Could not reach model "
                    f"'{model_name}' at {endpoint}: "
                    f"{str(e)}"
                )

                step = AgentStep(

                    step_number=
                        step_idx,

                    thought=
                        "Error connecting to local model.",

                    observation=
                        err_msg,

                    duration_sec=(

                        time.time()
                        -
                        step_start
                    ),
                )

                steps.append(step)

                return AgentExecutionResult(

                    task=
                        user_prompt,

                    final_answer=
                        err_msg,

                    success=
                        False,

                    steps=
                        steps,

                    total_duration_sec=(

                        time.time()
                        -
                        start_time
                    ),

                    model_used=
                        model_name,

                    task_type=
                        actual_task_type,

                    deliverables=
                        deliverables,
                )

            # ----------------------------------------------------
            # PARSE RESPONSE
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
            # FINAL ANSWER
            # ----------------------------------------------------

            if fa:

                final_answer = fa

                step = AgentStep(

                    step_number=
                        step_idx,

                    thought=(

                        thought
                        or
                        "Goal completed."
                    ),

                    duration_sec=(

                        time.time()
                        -
                        step_start
                    ),
                )

                steps.append(step)

                if self.step_callback:

                    self.step_callback(
                        step
                    )

                break

            # ----------------------------------------------------
            # NO ACTION
            # ----------------------------------------------------

            if not action:

                final_answer = response

                step = AgentStep(

                    step_number=
                        step_idx,

                    thought=(

                        thought
                        or
                        "Produced direct response."
                    ),

                    duration_sec=(

                        time.time()
                        -
                        step_start
                    ),
                )

                steps.append(step)

                if self.step_callback:

                    self.step_callback(
                        step
                    )

                break

            # ----------------------------------------------------
            # PREPARE TOOL ARGUMENTS
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
            # NORMALIZE DELIVERABLE ARGUMENTS
            # ----------------------------------------------------

            if (
                action
                ==
                "generate_deliverable"
            ):

                tool_args = (
                    self._prepare_deliverable_args(

                        tool_args,

                        previous_observation,

                        user_prompt
                    )
                )

            # ----------------------------------------------------
            # EXECUTE TOOL
            # ----------------------------------------------------

            tool_res: ToolResult = (
                self.registry
                .execute_tool(

                    action,

                    **tool_args
                )
            )

            observation = (

                tool_res.output

                if tool_res.success

                else
                f"Error: {tool_res.error}"
            )

            previous_observation = (
                observation
            )

            # ----------------------------------------------------
            # TRACK DELIVERABLES
            # ----------------------------------------------------

            if (

                action
                ==
                "generate_deliverable"

                and

                tool_res.success
            ):

                filename = (
                    tool_args.get(
                        "filename",
                        ""
                    )
                )

                if filename:

                    deliverables.append(
                        filename
                    )

            # ----------------------------------------------------
            # CREATE STEP RECORD
            # ----------------------------------------------------

            step_duration = (

                time.time()
                -
                step_start
            )

            step = AgentStep(

                step_number=
                    step_idx,

                thought=
                    thought,

                action=
                    action,

                action_input=
                    tool_args,

                observation=
                    observation,

                duration_sec=
                    step_duration,
            )

            steps.append(step)

            if self.step_callback:

                self.step_callback(
                    step
                )

            # ====================================================
            # STOP CONDITION 1
            # SUCCESSFUL FILE READ
            # ====================================================

            if (

                action
                ==
                "read_file"

                and

                tool_res.success
            ):

                final_answer = observation

                break

            # ====================================================
            # STOP CONDITION 2
            # SUCCESSFUL SPREADSHEET ANALYSIS
            # ====================================================

            if (

                action
                ==
                "analyze_spreadsheet"

                and

                tool_res.success
            ):

                final_answer = observation

                break

            # ====================================================
            # STOP CONDITION 3
            # SUCCESSFUL FILE LISTING
            # ====================================================

            if (

                action
                ==
                "list_files"

                and

                tool_res.success
            ):

                final_answer = observation

                break

            # ====================================================
            # STOP CONDITION 4
            # RAG SEARCH
            # ====================================================

            if (

                action
                ==
                "search_company_knowledge"

                and

                tool_res.success
            ):

                if not deliverable_requested:

                    final_answer = observation

                    break

                # ------------------------------------------------
                # FORCE DELIVERABLE AFTER RAG
                # ------------------------------------------------

                running_history += (

                    "\nIMPORTANT SYSTEM INSTRUCTION:\n"

                    "The company knowledge search completed "
                    "successfully.\n"

                    "The retrieved knowledge is the source "
                    "material for the requested deliverable.\n\n"

                    "NEXT ACTION MUST BE:\n"

                    "generate_deliverable\n\n"

                    "DO NOT call:\n"

                    "- analyze_spreadsheet\n"

                    "- execute_python_code\n"

                    "- search_company_knowledge again\n"

                    "- read_file unless explicitly required\n\n"

                    "Create the requested Word/Excel deliverable "
                    "directly using generate_deliverable.\n"

                    "Use the retrieved Observation as the document "
                    "content when appropriate.\n"

                    "Do not invent missing spreadsheet files, "
                    "Python functions, calculations, or sources.\n"

                    "After generate_deliverable succeeds, provide "
                    "the Final Answer.\n"
                )

            # ====================================================
            # STOP CONDITION 5
            # SUCCESSFUL DELIVERABLE
            # ====================================================

            if (

                action
                ==
                "generate_deliverable"

                and

                tool_res.success
            ):

                filename = (
                    tool_args.get(
                        "filename",
                        "deliverable"
                    )
                )

                final_answer = (

                    f"Successfully completed the task.\n\n"

                    f"Deliverable created: "
                    f"{filename}\n\n"

                    f"{observation}"
                )

                break

            # ====================================================
            # APPEND OBSERVATION
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

        # ========================================================
        # FALLBACK IF MAX STEPS REACHED
        # ========================================================

        if not final_answer:

            last_obs = (

                steps[-1].observation

                if steps

                else
                "No observation available"
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

        # ========================================================
        # FINAL RESULT
        # ========================================================

        total_duration = (

            time.time()
            -
            start_time
        )

        return AgentExecutionResult(

            task=
                user_prompt,

            final_answer=
                final_answer,

            success=
                True,

            steps=
                steps,

            total_duration_sec=
                total_duration,

            model_used=
                model_name,

            task_type=
                actual_task_type,

            deliverables=
                deliverables,
        )