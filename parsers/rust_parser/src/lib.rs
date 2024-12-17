use oq3_source_file::{parse_source_string, SourceTrait};
use std::path::PathBuf;

pub fn parse_qasm3(source: &str) -> Result<(), Box<dyn std::error::Error>> {
    let parsed = parse_source_string::<&str, PathBuf>(source, None, None);
    // For benchmarking purposes, we just want to verify parsing succeeded
    if parsed.any_parse_errors() {
        Err("Parsing failed".into())
    } else {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse() {
        let source = "OPENQASM 3.0;\nqubit q;";
        assert!(parse_qasm3(source).is_ok());
    }
}
