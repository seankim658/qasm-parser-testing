import time
from pathlib import Path
import statistics
import json
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
import logging
import traceback
from parsers import qiskit_antlr, rust_qasm, qasm_ts


@dataclass
class BenchmarkResult:
    """Data class to store benchmark results."""

    parser_name: str
    file_name: str
    execution_time: float
    success: bool
    error_message: Optional[str] = None


class QASMBenchmarker:
    """Class to manage benchmark operations."""

    def __init__(self, qasm_dir: Path, iterations: int = 10):
        """Constructor.

        Parameters
        ----------
        qasm_dir: Path
            Path to the directory of QASM files to test on.
        iterations: int (optional)
            Number of iterations to run each benchmark, defaults to 10.
        """
        self.qasm_dir = qasm_dir
        self.iterations = iterations
        self.parsers = {
            "qiskit_antlr": qiskit_antlr.QiskitANTLRParser.parse,
            "rust": rust_qasm.parse,
            "qasm_ts": qasm_ts.parse,
        }
        self.results: List[BenchmarkResult] = []

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def load_qasm_files(self) -> Dict[str, str]:
        """Load all QASM files from the qasm directory.

        Returns
        -------
        dict[str, str]
            Dictionary mapping file names to file contents.
        """
        qasm_files = {}
        for file_path in self.qasm_dir.glob("*.qasm"):
            try:
                with open(file_path, "r") as f:
                    qasm_files[file_path.name] = f.read()
            except Exception as e:
                self.logger.error(f"Failed to load {file_path}: {str(e)}")
        return qasm_files

    def benchmark_parser(
        self, parser_func: Callable, parser_name: str, qasm_content: str, file_name: str
    ) -> BenchmarkResult:
        """Benchmark a single parser on a single file.

        Parameters
        ----------
        parser_func: Callable
            The parser function to benchmark.
        parser_name: str
            Name of the parser.
        qasm_content: str
            The QASM content to parse.
        file_name: str
            Name of the file being parsed.

        Returns
        -------
        BenchmarkResult
            The result of the benchamrk.
        """
        times = []
        success = False
        error_msg = None

        try:
            # Warm-up run
            parser_func(qasm_content)

            # Timed runs
            for _ in range(self.iterations):
                start_time = time.perf_counter()
                parser_func(qasm_content)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

            success = True
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.logger.error(
                f"Parser {parser_name} failed on {file_name}: {error_msg}"
            )

        avg_time = statistics.mean(times) if times else float("inf")
        return BenchmarkResult(parser_name, file_name, avg_time, success, error_msg)

    def run_benchmarks(self) -> None:
        """Run benchmarks for all parsers on all files.
        """
        qasm_files = self.load_qasm_files()
        self.logger.info(f"Loaded {len(qasm_files)} QASM files")

        for file_name, content in qasm_files.items():
            self.logger.info(f"Benchmarking file: {file_name}")
            for parser_name, parser_func in self.parsers.items():
                self.logger.info(f"Running {parser_name}...")
                result = self.benchmark_parser(
                    parser_func, parser_name, content, file_name
                )
                self.results.append(result)

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive benchmark report.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the benchmark report.
        """
        report = {
            "summary": {
                "total_files": len(set(r.file_name for r in self.results)),
                "total_parsers": len(self.parsers),
                "iterations_per_test": self.iterations,
            },
            "parser_stats": {},
            "file_stats": {},
            "detailed_results": [],
        }

        # Generate parser statistics
        for parser_name in self.parsers.keys():
            parser_results = [r for r in self.results if r.parser_name == parser_name]
            successful_results = [r for r in parser_results if r.success]

            report["parser_stats"][parser_name] = {
                "success_rate": (
                    len(successful_results) / len(parser_results)
                    if parser_results
                    else 0
                ),
                "avg_time": (
                    statistics.mean([r.execution_time for r in successful_results])
                    if successful_results
                    else None
                ),
                "min_time": (
                    min([r.execution_time for r in successful_results])
                    if successful_results
                    else None
                ),
                "max_time": (
                    max([r.execution_time for r in successful_results])
                    if successful_results
                    else None
                ),
                "total_runs": len(parser_results),
                "successful_runs": len(successful_results),
            }

        # Generate file statistics
        for result in self.results:
            if result.file_name not in report["file_stats"]:
                report["file_stats"][result.file_name] = {
                    "parser_results": {},
                    "fastest_parser": None,
                    "success_rate": 0,
                }

            stats = report["file_stats"][result.file_name]
            stats["parser_results"][result.parser_name] = {
                "time": result.execution_time if result.success else None,
                "success": result.success,
                "error": result.error_message,
            }

        # Calculate success rates and fastest parsers
        for _, stats in report["file_stats"].items():
            successes = sum(1 for r in stats["parser_results"].values() if r["success"])
            stats["success_rate"] = successes / len(self.parsers)

            successful_times = {
                parser: data["time"]
                for parser, data in stats["parser_results"].items()
                if data["success"]
            }
            if successful_times:
                stats["fastest_parser"] = min(
                    successful_times.items(), key=lambda x: x[1]
                )[0]

        return report


def main():
    """Entry point for the benchmark script."""
    qasm_dir = Path(__file__).parent / "qasm"
    benchmarker = QASMBenchmarker(qasm_dir)

    try:
        logging.info("Starting benchmark run...")
        benchmarker.run_benchmarks()

        report = benchmarker.generate_report()

        report_path = Path(__file__).parent / "results" / "benchmark_results.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print("\nBenchmark Summary:")
        print("-----------------")
        print(f"Total files tested: {report['summary']['total_files']}")
        print(f"Iterations per test: {report['summary']['iterations_per_test']}\n")

        print("Parser Performance:")
        for parser, stats in report["parser_stats"].items():
            print(f"\n{parser}:")
            print(
                f"  Success rate: {stats['success_rate']*100:.1f}% ({stats['successful_runs']}/{stats['total_runs']} files)"
            )
            if stats["avg_time"]:
                print(
                    f"  Average time: {stats['avg_time']*1000:.2f}ms (successful runs only)"
                )
                print(f"  Min time: {stats['min_time']*1000:.2f}ms")
                print(f"  Max time: {stats['max_time']*1000:.2f}ms")
            else:
                print("  No successful runs to measure timing")
    finally:
        qasm_ts.cleanup()


if __name__ == "__main__":
    main()
