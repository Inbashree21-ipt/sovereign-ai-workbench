"""
Isolated Code Execution Sandbox
Supports:
1. Docker Sandbox: 'docker run --network none' (when Docker is available)
2. Local Process Sandbox: In-process AST inspection, network socket isolation guard,
   timeout enforcement, and workspace confinement.
"""

import sys
import time
import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List

from config import SANDBOX_DIR, SANDBOX_TIMEOUT_SECONDS, SANDBOX_MAX_OUTPUT_BYTES
from sandbox.security import validate_python_code


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_sec: float
    is_success: bool
    engine: str
    security_violations: Optional[List[str]] = None

    def __post_init__(self):
        if self.security_violations is None:
            self.security_violations = []

    def to_dict(self):
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "duration_sec": round(self.duration_sec, 3),
            "is_success": self.is_success,
            "engine": self.engine,
            "security_violations": self.security_violations or [],
        }


class CodeSandbox:
    """
    Executes Python code in an isolated, secure, air-gapped sandbox.
    """

    def __init__(self, sandbox_dir: Optional[Path] = None, timeout: float = SANDBOX_TIMEOUT_SECONDS):
        self.sandbox_dir = Path(sandbox_dir) if sandbox_dir else SANDBOX_DIR
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.docker_available = self._check_docker()

    def _check_docker(self) -> bool:
        """Check if Docker daemon is available and running."""
        docker_cmd = shutil.which("docker")
        if not docker_cmd:
            return False
        try:
            res = subprocess.run([docker_cmd, "info"], capture_output=True, timeout=2)
            return res.returncode == 0
        except Exception:
            return False

    def execute(self, code: str, use_docker_if_available: bool = True) -> ExecutionResult:
        """
        Main execution entrypoint.
        First validates safety via AST checks, then executes in the appropriate engine.
        """
        # Step 1: AST Security Validation
        is_safe, violations = validate_python_code(code)
        if not is_safe:
            return ExecutionResult(
                stdout="",
                stderr="[SECURITY REJECTION] Code was rejected by the sovereign security policy:\n" + "\n".join(violations),
                exit_code=-1,
                duration_sec=0.0,
                is_success=False,
                engine="ast_validator",
                security_violations=violations,
            )

        # Step 2: Choose engine
        if use_docker_if_available and self.docker_available:
            return self._execute_docker(code)
        else:
            return self._execute_local_process(code)

    def _execute_local_process(self, code: str) -> ExecutionResult:
        """
        Executes code via an isolated subprocess with an injected network kill-switch.
        """
        start_time = time.time()
        script_file = self.sandbox_dir / f"task_{int(time.time() * 1000)}.py"

        # Runtime isolation preamble: blocks socket-level connection attempts
        runtime_preamble = (
            "# --- Sovereign Sandbox Air-Gap Preamble ---\n"
            "import socket\n"
            "def _disallow_network(*args, **kwargs):\n"
            "    raise PermissionError('[SOVEREIGN AIR-GAP] Outbound network connection blocked by sandbox.')\n"
            "socket.socket.connect = _disallow_network\n"
            "socket.socket.connect_ex = _disallow_network\n"
            "socket.create_connection = _disallow_network\n"
            "# ------------------------------------------\n\n"
        )

        full_code = runtime_preamble + code

        try:
            script_file.write_text(full_code, encoding="utf-8")

            # Run in isolated subprocess
            proc = subprocess.run(
                [sys.executable, str(script_file.name)],
                cwd=str(self.sandbox_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            duration = time.time() - start_time
            stdout = proc.stdout[:SANDBOX_MAX_OUTPUT_BYTES]
            stderr = proc.stderr[:SANDBOX_MAX_OUTPUT_BYTES]

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=proc.returncode,
                duration_sec=duration,
                is_success=(proc.returncode == 0),
                engine="local_process_sandbox",
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ExecutionResult(
                stdout="",
                stderr=f"[TIMEOUT ERROR] Execution exceeded maximum allowed time of {self.timeout}s.",
                exit_code=-2,
                duration_sec=duration,
                is_success=False,
                engine="local_process_sandbox",
            )
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                stdout="",
                stderr=f"[EXECUTION ERROR] {str(e)}",
                exit_code=-3,
                duration_sec=duration,
                is_success=False,
                engine="local_process_sandbox",
            )
        finally:
            if script_file.exists():
                try:
                    script_file.unlink()
                except Exception:
                    pass

    def _execute_docker(self, code: str) -> ExecutionResult:
        """
        Executes code inside a Docker container with zero network access:
        docker run --rm --network none -v <dir>:/app -w /app python:3.11-slim python task.py
        """
        start_time = time.time()
        script_file = self.sandbox_dir / f"docker_task_{int(time.time() * 1000)}.py"

        try:
            script_file.write_text(code, encoding="utf-8")
            container_cmd = [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",  # strict air-gap
                "--memory",
                "512m",  # memory limit
                "--cpus",
                "1.0",   # cpu limit
                "-v",
                f"{str(self.sandbox_dir.resolve())}:/sandbox",
                "-w",
                "/sandbox",
                "python:3.11-slim",
                "python",
                script_file.name,
            ]

            proc = subprocess.run(
                container_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            duration = time.time() - start_time
            return ExecutionResult(
                stdout=proc.stdout[:SANDBOX_MAX_OUTPUT_BYTES],
                stderr=proc.stderr[:SANDBOX_MAX_OUTPUT_BYTES],
                exit_code=proc.returncode,
                duration_sec=duration,
                is_success=(proc.returncode == 0),
                engine="docker_isolated",
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                stdout="",
                stderr=f"[DOCKER TIMEOUT] Container exceeded {self.timeout}s limit.",
                exit_code=-2,
                duration_sec=time.time() - start_time,
                is_success=False,
                engine="docker_isolated",
            )
        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=f"[DOCKER ERROR] {str(e)}",
                exit_code=-3,
                duration_sec=time.time() - start_time,
                is_success=False,
                engine="docker_isolated",
            )
        finally:
            if script_file.exists():
                try:
                    script_file.unlink()
                except Exception:
                    pass
