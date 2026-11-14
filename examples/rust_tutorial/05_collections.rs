use std::collections::BTreeMap;

fn first<T>(values: &[T]) -> Option<&T> {
    values.first()
}

fn main() {
    let mut scores = vec![90_u32, 50, 80];
    scores.push(60);
    scores.sort_unstable();
    println!("{scores:?}");
    let passed = scores.iter().filter(|&&score| score >= 60).count();
    let total: u32 = scores.iter().sum();
    println!("count={} total={total} passed={passed}", scores.len());
    match first(&scores) {
        Some(score) => println!("first={score}"),
        None => println!("no scores"),
    }

    let mut counts = BTreeMap::new();
    for name in ["Alice", "Bob", "Alice"] {
        *counts.entry(name).or_insert(0_u32) += 1;
    }
    for (name, count) in counts {
        println!("{name}={count}");
    }
}
