"""
Agent Evaluation Module
========================

Provides evaluation metrics and testing framework for agent performance.

Features:
- Response quality assessment
- Task completion tracking
- Latency measurements
- Tool usage statistics
- Success/failure analysis
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TaskStatus(Enum):
    """Task completion status"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


@dataclass
class EvaluationResult:
    """Result of an agent evaluation"""
    task_id: str
    agent_name: str
    task_description: str
    status: TaskStatus
    latency_seconds: float
    tool_calls: List[str]
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None
    quality_score: Optional[float] = None  # 0.0 to 1.0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class AgentEvaluator:
    """Evaluates agent performance"""
    
    def __init__(self):
        self.results: List[EvaluationResult] = []
        self.test_cases: Dict[str, Dict] = {}
    
    def add_test_case(self, task_id: str, description: str, expected_tools: List[str]):
        """Add a test case for evaluation"""
        self.test_cases[task_id] = {
            "description": description,
            "expected_tools": expected_tools
        }
    
    def evaluate_task(
        self,
        task_id: str,
        agent_name: str,
        task_description: str,
        status: TaskStatus,
        latency: float,
        tool_calls: List[str],
        tokens_used: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> EvaluationResult:
        """
        Evaluate a completed task
        
        Args:
            task_id: Unique task identifier
            agent_name: Name of the agent
            task_description: Description of the task
            status: Task completion status
            latency: Time taken in seconds
            tool_calls: List of tools called
            tokens_used: Number of tokens consumed
            error_message: Error message if failed
        
        Returns:
            EvaluationResult with quality score
        """
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            task_id, status, tool_calls, latency
        )
        
        result = EvaluationResult(
            task_id=task_id,
            agent_name=agent_name,
            task_description=task_description,
            status=status,
            latency_seconds=latency,
            tool_calls=tool_calls,
            tokens_used=tokens_used,
            error_message=error_message,
            quality_score=quality_score
        )
        
        self.results.append(result)
        return result
    
    def _calculate_quality_score(
        self,
        task_id: str,
        status: TaskStatus,
        tool_calls: List[str],
        latency: float
    ) -> float:
        """
        Calculate quality score based on multiple factors
        
        Scoring:
        - Task success: 0.5
        - Correct tools: 0.3
        - Performance: 0.2
        """
        score = 0.0
        
        # Task success (50%)
        if status == TaskStatus.SUCCESS:
            score += 0.5
        elif status == TaskStatus.PARTIAL:
            score += 0.25
        
        # Tool correctness (30%)
        if task_id in self.test_cases:
            expected_tools = set(self.test_cases[task_id]["expected_tools"])
            actual_tools = set(tool_calls)
            
            if expected_tools:
                # Precision: correct tools / total tools used
                precision = len(expected_tools & actual_tools) / len(actual_tools) if actual_tools else 0
                # Recall: correct tools / expected tools
                recall = len(expected_tools & actual_tools) / len(expected_tools)
                # F1 score
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                score += 0.3 * f1
        
        # Performance (20%)
        # Assume target latency of 2 seconds
        target_latency = 2.0
        if latency <= target_latency:
            score += 0.2
        elif latency <= target_latency * 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def get_statistics(self, agent_name: Optional[str] = None) -> Dict:
        """
        Get evaluation statistics
        
        Args:
            agent_name: Filter by agent name (optional)
        
        Returns:
            Dictionary with statistics
        """
        # Filter results
        results = self.results
        if agent_name:
            results = [r for r in results if r.agent_name == agent_name]
        
        if not results:
            return {
                "total_tasks": 0,
                "success_rate": 0.0,
                "average_quality": 0.0,
                "average_latency": 0.0
            }
        
        # Calculate statistics
        total = len(results)
        successes = len([r for r in results if r.status == TaskStatus.SUCCESS])
        
        quality_scores = [r.quality_score for r in results if r.quality_score is not None]
        latencies = [r.latency_seconds for r in results]
        
        # Status breakdown
        status_counts = {}
        for status in TaskStatus:
            count = len([r for r in results if r.status == status])
            status_counts[status.value] = count
        
        # Tool usage
        tool_usage = {}
        for result in results:
            for tool in result.tool_calls:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # Token usage
        total_tokens = sum(r.tokens_used for r in results if r.tokens_used is not None)
        
        return {
            "total_tasks": total,
            "success_rate": successes / total if total > 0 else 0.0,
            "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            "average_latency": sum(latencies) / len(latencies) if latencies else 0.0,
            "median_latency": sorted(latencies)[len(latencies) // 2] if latencies else 0.0,
            "status_breakdown": status_counts,
            "tool_usage": tool_usage,
            "total_tokens": total_tokens,
            "average_tokens_per_task": total_tokens / total if total > 0 else 0
        }
    
    def get_failure_analysis(self) -> Dict:
        """Analyze failures to identify patterns"""
        failures = [r for r in self.results if r.status == TaskStatus.FAILURE]
        
        if not failures:
            return {
                "total_failures": 0,
                "failure_rate": 0.0,
                "common_errors": {}
            }
        
        # Group by error message
        error_counts = {}
        for failure in failures:
            error = failure.error_message or "Unknown error"
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # Sort by frequency
        common_errors = sorted(
            error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 errors
        
        return {
            "total_failures": len(failures),
            "failure_rate": len(failures) / len(self.results) if self.results else 0.0,
            "common_errors": dict(common_errors),
            "failed_agents": list(set(f.agent_name for f in failures))
        }
    
    def export_results(self, filepath: str):
        """Export results to JSON file"""
        data = {
            "evaluation_date": datetime.now().isoformat(),
            "total_results": len(self.results),
            "results": [asdict(r) for r in self.results],
            "statistics": self.get_statistics(),
            "failure_analysis": self.get_failure_analysis()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def generate_report(self) -> str:
        """Generate a human-readable evaluation report"""
        stats = self.get_statistics()
        failures = self.get_failure_analysis()
        
        report = []
        report.append("=" * 60)
        report.append("AGENT EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tasks: {stats['total_tasks']}")
        report.append("")
        
        report.append("OVERALL PERFORMANCE")
        report.append("-" * 60)
        report.append(f"Success Rate: {stats['success_rate']:.1%}")
        report.append(f"Average Quality Score: {stats['average_quality']:.2f}/1.00")
        report.append(f"Average Latency: {stats['average_latency']:.2f}s")
        report.append(f"Median Latency: {stats['median_latency']:.2f}s")
        report.append("")
        
        report.append("STATUS BREAKDOWN")
        report.append("-" * 60)
        for status, count in stats['status_breakdown'].items():
            percentage = (count / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            report.append(f"{status.capitalize()}: {count} ({percentage:.1f}%)")
        report.append("")
        
        report.append("TOOL USAGE")
        report.append("-" * 60)
        for tool, count in sorted(stats['tool_usage'].items(), key=lambda x: x[1], reverse=True)[:10]:
            report.append(f"{tool}: {count} calls")
        report.append("")
        
        report.append("TOKEN USAGE")
        report.append("-" * 60)
        report.append(f"Total Tokens: {stats['total_tokens']:,}")
        report.append(f"Average per Task: {stats['average_tokens_per_task']:.0f}")
        report.append("")
        
        if failures['total_failures'] > 0:
            report.append("FAILURE ANALYSIS")
            report.append("-" * 60)
            report.append(f"Total Failures: {failures['total_failures']}")
            report.append(f"Failure Rate: {failures['failure_rate']:.1%}")
            report.append("")
            report.append("Common Errors:")
            for error, count in list(failures['common_errors'].items())[:5]:
                report.append(f"  - {error}: {count} occurrences")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# Example test cases
def create_sample_test_cases() -> AgentEvaluator:
    """Create sample test cases for evaluation"""
    evaluator = AgentEvaluator()
    
    # Jarvis ADK test cases
    evaluator.add_test_case(
        "calendar-list",
        "List today's calendar events",
        ["list_events"]
    )
    
    evaluator.add_test_case(
        "calendar-create",
        "Create a meeting tomorrow at 2 PM",
        ["create_event"]
    )
    
    evaluator.add_test_case(
        "trip-plan",
        "Plan a trip to Paris",
        ["plan_trip"]
    )
    
    # Lenny Lang test cases
    evaluator.add_test_case(
        "translate",
        "Translate text to French",
        ["translate"]
    )
    
    evaluator.add_test_case(
        "weather",
        "Get weather in London",
        ["weather"]
    )
    
    # Taylor Crew test cases
    evaluator.add_test_case(
        "crew-trip",
        "Plan multi-city trip",
        ["city_selector", "local_expert", "travel_concierge"]
    )
    
    return evaluator


# Example usage
if __name__ == "__main__":
    # Create evaluator with test cases
    evaluator = create_sample_test_cases()
    
    # Simulate some evaluations
    evaluator.evaluate_task(
        task_id="calendar-list",
        agent_name="jarvis_adk",
        task_description="List today's events",
        status=TaskStatus.SUCCESS,
        latency=0.5,
        tool_calls=["list_events"],
        tokens_used=150
    )
    
    evaluator.evaluate_task(
        task_id="translate",
        agent_name="lenny_lang",
        task_description="Translate to French",
        status=TaskStatus.SUCCESS,
        latency=1.2,
        tool_calls=["translate"],
        tokens_used=200
    )
    
    # Generate report
    print(evaluator.generate_report())
    
    # Export results
    evaluator.export_results("evaluation_results.json")
