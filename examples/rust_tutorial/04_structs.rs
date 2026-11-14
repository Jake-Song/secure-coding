struct Student {
    name: String,
    score: u32,
}

enum Assessment {
    Passed,
    Retry,
}

impl Student {
    fn new(name: &str, score: u32) -> Result<Self, &'static str> {
        if score > 100 {
            return Err("score must be from 0 to 100");
        }
        Ok(Self {
            name: String::from(name),
            score,
        })
    }

    fn assessment(&self) -> Assessment {
        if self.score >= 60 {
            Assessment::Passed
        } else {
            Assessment::Retry
        }
    }
}

fn main() {
    let student = Student::new("Alice", 85).expect("fixed example score is valid");
    let outcome = match student.assessment() {
        Assessment::Passed => "pass",
        Assessment::Retry => "retry",
    };
    println!("{}: {} ({outcome})", student.name, student.score);
    match Student::new("Bob", 101) {
        Ok(student) => println!("{} accepted", student.name),
        Err(error) => println!("rejected: {error}"),
    }
}
