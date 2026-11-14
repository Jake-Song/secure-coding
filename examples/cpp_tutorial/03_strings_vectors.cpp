#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

// Small scores only; a general integer sum needs an overflow policy.
double average(const std::vector<int>& scores) {
    if (scores.empty()) {
        throw std::invalid_argument("scores must not be empty");
    }
    int total{0};
    for (const int score : scores) {
        total += score;
    }
    return static_cast<double>(total) / static_cast<double>(scores.size());
}

int main() {
    std::string name{"Alice"};
    name += " Lee";
    std::vector<int> scores{70, 80, 90};
    scores.push_back(100);
    std::cout << "name=" << name << " bytes=" << name.size() << '\n';
    std::cout << std::fixed << std::setprecision(2)
              << "count=" << scores.size() << " average=" << average(scores) << '\n';
    std::cout << "first=" << scores.at(0) << '\n';
}
