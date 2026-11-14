mod score;

use std::env;
use std::fs::OpenOptions;
use std::io::Write;
use std::process::ExitCode;

fn run() -> Result<(), String> {
    let mut arguments = env::args_os().skip(1);
    let path = arguments
        .next()
        .ok_or("usage: score_report NEW_FILE SCORE... (1..100 scores)")?;
    let mut scores = Vec::new();
    for argument in arguments {
        if scores.len() == 100 {
            return Err("expected 1..100 scores".into());
        }
        let text = argument.to_str().ok_or("scores must contain ASCII digits")?;
        scores.push(score::parse_score(text)?);
    }
    if scores.is_empty() {
        return Err("expected 1..100 scores".into());
    }
    let total: u32 = scores.iter().sum();
    let average = f64::from(total) / scores.len() as f64;

    // create_new atomically refuses an existing path.
    let mut report = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .map_err(|error| format!("cannot create report: {error}"))?;
    writeln!(report, "count,total,average\n{},{total},{average:.2}", scores.len())
        .map_err(|error| format!("report write failed; file may be incomplete: {error}"))?;
    report
        .sync_all()
        .map_err(|error| format!("report sync failed; file may be incomplete: {error}"))?;
    println!("report saved");
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
