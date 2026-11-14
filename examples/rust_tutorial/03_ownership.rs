fn byte_count(text: &str) -> usize {
    text.len()
}

fn add_suffix(text: &mut String) {
    text.push_str(" Lee");
}

fn main() {
    let original = String::from("Alice");
    let mut owner = original;
    // original has been moved; it cannot be used here.
    println!("name={owner} bytes={}", byte_count(&owner));
    add_suffix(&mut owner);
    let copy = owner.clone();
    println!("owner={owner} copy={copy}");
    println!("first word={}", &owner[..5]); // This example uses ASCII.
}
