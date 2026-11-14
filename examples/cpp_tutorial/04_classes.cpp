#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

class Student {
public:
    Student(std::string name, int score) : name_{std::move(name)}, score_{score} {
        if (score_ < 0 || score_ > 100) {
            throw std::invalid_argument("score must be from 0 to 100");
        }
    }

    const std::string& name() const { return name_; }
    int score() const { return score_; }
    bool passed() const { return score_ >= 60; }

private:
    std::string name_;
    int score_;
};

int main() {
    const Student student{"Alice", 85};
    std::cout << student.name() << ": " << student.score()
              << (student.passed() ? " (pass)\n" : " (retry)\n");
    try {
        const Student invalid{"Bob", 101};
        std::cout << invalid.name() << '\n';
    } catch (const std::invalid_argument& error) {
        std::cout << "rejected: " << error.what() << '\n';
    }
}
