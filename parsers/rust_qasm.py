import subprocess
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=1)
def compile_rust_parser() -> Path:
    """Compile the Rust parser once and cache the result.

    Returns
    -------
    Path
        The path to the compiled Rust parser binary.
    """
    rust_dir = Path(__file__).parent / "rust_parser"
    result = subprocess.run(
        ["cargo", "build", "--release"], cwd=rust_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to compile Rust parser: {result.stderr}")
    return rust_dir / "target" / "release" / "rust_parser"


def parse(qasm_str: str):
    """Parse OpenQASM 3 using Rust parser.

    For benchmarking, we use a simple CLI tool that just verifies parsing succeeded.

    Parameters
    ----------
    qasm_str: str
        The OpenQASM code to be parsed.
    """
    parser_binary = compile_rust_parser()
    result = subprocess.run(
        [parser_binary, qasm_str],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(f"Parsing failed: {result.stderr}")
