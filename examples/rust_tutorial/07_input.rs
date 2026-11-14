mod score;

use std::io::{self, Write};
use std::process::ExitCode;

fn run() -> Result<(), String> {
    print!("Score (0..100): ");
    io::stdout().flush().map_err(|error| error.to_string())?;
    let mut line = String::new();
    let bytes = io::stdin()
        .read_line(&mut line)
        .map_err(|error| error.to_string())?;
    if bytes == 0 {
        return Err("could not read input".into());
    }
    let line = line.strip_suffix('\n').unwrap_or(&line);
    let line = line.strip_suffix('\r').unwrap_or(line);
    // read_line already allocated storage; this is a validation limit only.
    if line.len() > 62 {
        return Err("input too long".into());
    }
    let score = score::parse_score(line)?;
    println!("accepted={score}");
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::FAILURE
        }
    }
}
