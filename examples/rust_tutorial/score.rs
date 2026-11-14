pub fn parse_score(text: &str) -> Result<u32, &'static str> {
    if text.is_empty() || !text.bytes().all(|byte| byte.is_ascii_digit()) {
        return Err("expected ASCII digits representing a score from 0 to 100");
    }
    let score = text.parse::<u32>().map_err(|_| "integer out of range")?;
    if score > 100 {
        return Err("score must be from 0 to 100");
    }
    Ok(score)
}
