from openqasm3.parser import parse as op3_parse


class QiskitANTLRParser:

    @staticmethod
    def parse(qasm_str: str):
        """Parse OpenQASM 3 using Qiskit's ANTLR parser, stopping at AST generation.

        Parameters
        ----------
        qasm_str: str
            The OpenQASM 3 code.
        """
        return op3_parse(qasm_str)
