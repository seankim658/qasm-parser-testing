import subprocess
from pathlib import Path
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class QASMTSParser:
    """Class to manage the qasm-ts Node.js parser server.

    This class ensures the parser server is started, stopped,
    communicates with the server for parsing OpenQASM 3 code.
    """

    def __init__(self):
        """Constructor, also starts the server."""
        self.process = None
        self.lock = Lock()
        self.start_server()

    def start_server(self):
        """Start the Node.js parser server if not already running."""
        if self.process is None:
            js_dir = Path(__file__).parent
            logger.info("Starting Node.js server...")
            try:
                self.process = subprocess.Popen(
                    ["node", "qasm_ts_server.js"],
                    cwd=js_dir,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )

                # Wait for ready signal with timeout
                ready_line = self.process.stdout.readline().strip()
                logger.info(f"Received from server: {ready_line}")
                if ready_line != "READY":
                    self.stop_server()
                    raise RuntimeError(f"Server failed to start: {ready_line}")
                logger.info("Server started successfully")

            except Exception as e:
                if self.process:
                    self.stop_server()
                raise RuntimeError(f"Failed to start parser server: {str(e)}")

    def stop_server(self):
        """Stop the Node.js parser server."""
        if self.process:
            logger.info("Stopping server...")
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    logger.warning("Server did not terminate gracefully, killing...")
                    self.process.kill()
            finally:
                self.process = None
                logger.info("Server stopped")

    def parse(self, qasm_str: str) -> str:
        """Parse OpenQASM 3 using qasm-ts parser.

        Parameters
        ----------
        qasm_str: str
            The OpenQASM 3 code to be parsed.

        Returns
        -------
        str
            The server response indicating success or error details.
        """
        with self.lock:
            if self.process is None or self.process.poll() is not None:
                logger.info("Server not running, starting...")
                self.start_server()

            try:
                logger.debug("Sending parse request...")
                self.process.stdin.write(qasm_str + "\n")
                self.process.stdin.flush()

                logger.debug("Waiting for response...")
                response = self.process.stdout.readline().strip()
                logger.info(f"Received response: {response}")

                if not response:
                    raise ValueError("No response from parser server")
                if response.startswith("ERROR:"):
                    raise ValueError(response[6:])
                if response != "SUCCESS":
                    raise ValueError(f"Unexpected response: {response}")

            except Exception as e:
                logger.error(f"Parse error: {str(e)}")
                # Check server stderr for any errors
                if self.process:
                    errors = self.process.stderr.read()
                    if errors:
                        logger.error(f"Server errors: {errors}")
                self.stop_server()
                raise


# Global parser instance
_parser = QASMTSParser()


def parse(qasm_str: str) -> str:
    """
    Parse OpenQASM 3 code using the global QASMTSParser instance.

    Parameters
    ----------
    qasm_str : str
        The OpenQASM 3 code to be parsed.

    Returns
    -------
    str
        The server response indicating success or error details.

    Raises
    ------
    ValueError
        If the server returns an error response.
    RuntimeError
        If the server encounters a critical failure.
    """
    return _parser.parse(qasm_str)


def cleanup():
    """Clean up resources when benchmarking is complete."""
    _parser.stop_server()
