#include <algorithm>
#include <iostream>
#include <vector>

template <typename Container>
void print_values(const Container& values) {
    bool first{true};
    for (const auto& value : values) {
        if (!first) {
            std::cout << ' ';
        }
        std::cout << value;
        first = false;
    }
    std::cout << '\n';
}

int main() {
    std::vector<int> scores{90, 50, 80, 60};
    std::sort(scores.begin(), scores.end());
    print_values(scores);
    const auto passed = std::count_if(scores.begin(), scores.end(), [](int score) {
        return score >= 60;
    });
    std::cout << "passed=" << passed << '\n';
}
