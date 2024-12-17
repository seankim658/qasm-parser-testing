# OpenQASM 3 Parser Benchmarks

This project compares the performance and capabilities of three different OpenQASM 3 parsers:

1. Qiskit ANTLR Parser (Reference Implementation)
2. Qiskit Rust Parser (Experimental)
3. Qasm-ts

- [Parser Implementations](#parser-implementations)
  - [Qiskit ANTLR Parser](#qiskit-antlr-parser)
  - [Qiskit Rust Parser](#qiskit-rust-parser)
  - [Qasm-ts](#qasm-ts)
- [Usage](#usage)
  - [Setup](#setup)
  - [Running the Benchmarks](#running-the-benchmarks)
- [Benchmarking Implementation Notes](#benchmarking-implementation-notes)

---

## Parser Implementations

### Qiskit ANTLR Parser

The ANTLR-based parser is qiskit's reference implementation for parsing OpenQASM 3. It is accessible through the [`loads()`](https://github.com/Qiskit/qiskit/blob/40aa70c601842ba93ddcd687956b87c135d8234c/qiskit/qasm3/__init__.py#L330) and [`load()`](https://github.com/Qiskit/qiskit/blob/40aa70c601842ba93ddcd687956b87c135d8234c/qiskit/qasm3/__init__.py#L305) methods, which require installing the [`qiskit-qasm3-import`](https://github.com/Qiskit/qiskit-qasm3-import) package. This parser uses ANTLR4 to generate a parser from the official [OpenQASM 3 grammar](https://openqasm.com/grammar/index.html).

The general workflow for parsing OpenQASM 3 from the qiskit reference parser is as follows:

1. OpenQASM 3 String - Loaded script or string of OpenQASM
2. [`qiskit.qasm3.loads()`](https://github.com/Qiskit/qiskit/blob/40aa70c601842ba93ddcd687956b87c135d8234c/qiskit/qasm3/__init__.py#L330) - Entry point in qiskit
3. [`qiskit_qasm3_import.parse()`](https://github.com/Qiskit/qiskit-qasm3-import/blob/da0b82ab6a0d500eb391379f970c8b647e64feaf/src/qiskit_qasm3_import/api.py#L24) - Calls [`openqasm3`](https://github.com/openqasm/openqasm) package
4. [`openqasm3.parse()`](https://github.com/openqasm/openqasm/blob/e3b47ac3e24173799526dbff672743d368b09e6f/source/openqasm/openqasm3/parser.py#L67) - Entry point for the ANTLR parser
5. [`qasm3Lexer`](https://github.com/openqasm/openqasm/blob/e3b47ac3e24173799526dbff672743d368b09e6f/source/openqasm/openqasm3/_antlr/__init__.py#L68) - ANTLR lexer to tokenize input string
6. [`qasm3Parser`](https://github.com/openqasm/openqasm/blob/e3b47ac3e24173799526dbff672743d368b09e6f/source/openqasm/openqasm3/_antlr/__init__.py#L68) - ANTLR parser to generate the abstract syntax tree

Note: Qiskit provides further downstream steps such as converting the resulting AST to a Circuit. For sake of benchmarking, we are only concerned up to the AST generation.

### Qiskit Rust Parser

The [qiskit rust parser](https://github.com/Qiskit/openqasm3_parser) is a native high performance experimental parser that is [built](https://github.com/Qiskit/qiskit/blob/main/setup.py) as a native extension through the main [qiskit](https://github.com/Qiskit/qiskit) Python package (through PyO3 binding) and exposed through `qiskit._accerlate`. The rust parser is used when using the [`loads_experimental()`](https://github.com/Qiskit/qiskit/blob/40aa70c601842ba93ddcd687956b87c135d8234c/qiskit/qasm3/__init__.py#L353) and [`load_experimental()`](https://github.com/Qiskit/qiskit/blob/40aa70c601842ba93ddcd687956b87c135d8234c/qiskit/qasm3/__init__.py#L364) methods. The actual building of the `qiskit._accelerate` Python extension module is done through the [`qiskit-pyext`](https://github.com/Qiskit/qiskit/tree/main/crates/pyext) crate. The Python bindings are built through the [`qiskit._qasm3`](https://github.com/Qiskit/qiskit/tree/main/crates/qasm3) crate, the rust level qiskit interface to the native rust parser.

The general workflow for parsing OpenQASM 3 from the experimental rust parser is as follows:

1. OpenQASM 3 String - Loaded script or string of OpenQASM
2. [`qiskit.qasm3.loads_experimental()`](https://github.com/Qiskit/qiskit/blob/40aa70c601842ba93ddcd687956b87c135d8234c/qiskit/qasm3/__init__.py#L353) - Entry point in qiskit
3. [`qiskit._accelerate_qasm3.loads()`](https://github.com/Qiskit/qiskit/blob/40aa70c601842ba93ddcd687956b87c135d8234c/crates/qasm3/src/lib.rs#L58) - The PyO3 binding that connects Python to Rust
4. [`oq3_lexer`](https://github.com/Qiskit/openqasm3_parser/tree/main/crates/oq3_lexer) - Tokenizes the input string
5. [`oq3_parser`](https://github.com/Qiskit/openqasm3_parser/tree/main/crates/oq3_parser) - Creates the abstract syntax tree

Note: The rust rust parser provides further downstream steps such as performing semantic analysis on the resulting AST to build an abstract semantic graph (ASG). For sake of benchmarking, we are only concerned up to the AST generation.

### QASM-TS

The [qasm-ts](https://github.com/comp-phys-marc/qasm-ts) parser is an external typescript library for usage in web applications.

The general workflow for parsing OpenQASM 3 from the qasm-ts parser is as follows:

1. OpenQASM 3 String - Loaded script or string of OpenQASM
2. [`parseString()`](https://github.com/comp-phys-marc/qasm-ts/blob/master/src/main.ts) - Entry point in qasm-ts
3. [`lex()`](https://github.com/comp-phys-marc/qasm-ts/blob/master/src/lexer.ts#L8) - Tokenizes the input string
4. [`parse()`](https://github.com/comp-phys-marc/qasm-ts/blob/master/src/parser.ts) - Creates the abtract syntax tree

## Usage

### Setup

It is recommended to create a python virtual environment. 

```bash
python3 -m env env
source env/bin/activate   # For Linux/macOS
env\Script\activate       # For Windows
```

Next, install project dependencies.

For Python dependencies:

```bash
pip install -r requirements.txt
```

For Node.js dependencies:

```bash
npm install
```

### Running the Benchmarks

```
python benchmarks/parse_bench.py
```

## Benchmarking Implementation Notes

- The OpenQASM 3 Python bindings provided to the Rust parser do not expose a way to just generate an AST. Rather, the exposed `loads()` and `load()` functions also perform semantic analysis to generate abstract semantic graphs. In order to benchmark just to the AST generation, the Rust crates were used directly rather than through the Python bindings.
- Similarly, the `qiskit-qasm3-import` module only exposes functions that perform ANTLR parsing plus downstream conversion of the AST to a Qiskit circuit. To avoid this, the `openqasm` library is used directly.
- In order to avoid including Nodejs and Rust compilation in the benchmark times, a non-timed warm up run is used to initialize system resources. In the Rust instance, the warmup run is used to compile the release binary and the path is cached using an LRU cache for retrieval on subsequent timed iterations. For the Typescript library, the warm up run is used to initialize a server where the QASM snippets to be parsed will be sent.
