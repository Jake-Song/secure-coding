mod score;

fn doubled_score(text: &str) -> Result<u32, &'static str> {
    let score = score::parse_score(text)?;
    Ok(score * 2)
}

fn main() {
    for text in ["85", "101", "bad"] {
        match doubled_score(text) {
            Ok(value) => println!("{text}: doubled={value}"),
            Err(error) => println!("{text}: rejected: {error}"),
        }
    }
}
