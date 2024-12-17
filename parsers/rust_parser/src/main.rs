use rust_parser::parse_qasm3;
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: {} <qasm-string>", args[0]);
        std::process::exit(1);
    }

    match parse_qasm3(&args[1]) {
        Ok(_) => std::process::exit(0),
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1)
        }
    }
}
