fn add_one(value: &mut i32) {
    *value += 1;
}

fn main() {
    let mut score: i32 = 85;
    let pass_mark = 60;
    let passed = score >= pass_mark;
    println!("passed={passed}");

    let mut total = 0;
    for number in 1..=5 {
        total += number;
    }
    println!("sum 1..5={total}");
    add_one(&mut score);
    let outcome = if score >= pass_mark { "pass" } else { "retry" };
    println!("score={score} {outcome}");

    let scores = [70, 80, 90];
    println!("first={} count={}", scores[0], scores.len());
}
