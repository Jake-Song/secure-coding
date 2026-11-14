#include <iostream>

void add_one(int& value) {
    ++value;
}

int main() {
    int score{85};
    const int pass_mark{60};
    const auto passed = score >= pass_mark;
    std::cout << std::boolalpha << "passed=" << passed << '\n';

    int total{0};
    for (int number = 1; number <= 5; ++number) {
        total += number;
    }
    std::cout << "sum 1..5=" << total << '\n';
    add_one(score);
    if (score >= pass_mark) {
        std::cout << "score=" << score << " pass\n";
    } else {
        std::cout << "score=" << score << " retry\n";
    }
}
