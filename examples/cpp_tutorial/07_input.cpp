#include "score.hpp"

#include <iostream>
#include <string>

int main() {
    std::cout << "Score (0..100): " << std::flush;
    std::string line;
    if (!std::getline(std::cin, line)) {
        std::cerr << "could not read input\n";
        return 1;
    }
    // getline has already allocated storage; this is a validation limit only.
    if (line.size() > 62) {
        std::cerr << "input too long\n";
        return 1;
    }
    const auto score = parse_score(line);
    if (!score) {
        std::cerr << "expected ASCII digits representing a score from 0 to 100\n";
        return 1;
    }
    std::cout << "accepted=" << *score << '\n';
}
