const { parseString } = require("qasm-ts");

process.stdin.setEncoding("utf8");

process.stdin.on("data", function(chunk) {
  try {
    // Log received data
    console.error(`Received data: ${chunk}`);

    try {
      parseString(chunk);
      process.stdout.write("SUCCESS\n");
      console.error("Parsing succeeded");
    } catch (error) {
      process.stdout.write(`ERROR:${error.message}\n`);
      console.error(`Parsing failed: ${error.message}`);
    }
  } catch (error) {
    process.stdout.write(`ERROR:Server error: ${error.message}\n`);
    console.error(`Server error: ${error.message}`);
  }
});

// Signal that server is ready
process.stdout.write("READY\n");
console.error("Server ready");
