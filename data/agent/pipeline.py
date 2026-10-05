import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

from agent.executor import HeadlessCodeExecutor, ExecutionResult
from agent.repair import TracebackFeedbackRepairer


@dataclass
class DiagnosticStep:
    attempt: int
    code: str
    success: bool
    error_type: Optional[str]
    stderr: str


@dataclass
class AgentSessionReport:
    prompt: str
    resolved: bool
    total_attempts: int
    steps: List[DiagnosticStep] = field(default_factory=list)
    output_figure: Optional[str] = None


class TelemetryAnalysisAgent:
    def __init__(self, max_retries: int = 4):
        self.max_retries = max_retries
        self.executor = HeadlessCodeExecutor()
        self.repairer = TracebackFeedbackRepairer()

    def run_pipeline(self, prompt: str, initial_code: str, schema_info: Dict[str, Any]) -> AgentSessionReport:
        report = AgentSessionReport(
            prompt=prompt,
            resolved=False,
            total_attempts=0,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            work_dir = Path(tmp_dir)
            current_code = initial_code

            for attempt in range(1, self.max_retries + 1):
                report.total_attempts = attempt
                res: ExecutionResult = self.executor.run(current_code, work_dir)

                step = DiagnosticStep(
                    attempt=attempt,
                    code=current_code,
                    success=res.success,
                    error_type=res.error_type,
                    stderr=res.stderr,
                )
                report.steps.append(step)

                if res.success:
                    report.resolved = True
                    report.output_figure = res.figure_path
                    break

                current_code = self.repairer.apply_correction(
                    code=current_code,
                    stderr=res.stderr,
                    error_type=res.error_type or "Unknown",
                    schema_info=schema_info,
                )

        return report
