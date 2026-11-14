#include "score.hpp"

#include <cstdio>
#include <iostream>
#include <memory>
#include <numeric>
#include <vector>

struct FileCloser {
    void operator()(std::FILE* file) const { std::fclose(file); }
};

int main(int argc, char* argv[]) {
    constexpr int max_scores{100};
    if (argc < 3 || argc > max_scores + 2) {
        std::cerr << "usage: 08_score_report NEW_FILE SCORE... (1..100 scores)\n";
        return 1;
    }

    std::vector<int> scores;
    for (int index = 2; index < argc; ++index) {
        const auto score = parse_score(argv[index]);
        if (!score) {
            std::cerr << "invalid score at position " << index - 1 << '\n';
            return 1;
        }
        scores.push_back(*score);
    }
    const int total = std::accumulate(scores.begin(), scores.end(), 0);
    const double average = static_cast<double>(total) / static_cast<double>(scores.size());

    // C++17 file streams lack exclusive creation; wrap a C file in an RAII owner.
    using File = std::unique_ptr<std::FILE, FileCloser>;
    File report{std::fopen(argv[1], "wx")};
    if (!report) {
        std::perror("cannot create report");
        return 1;
    }
    if (std::fprintf(report.get(), "count,total,average\n%zu,%d,%.2f\n",
                     scores.size(), total, average) < 0) {
        std::cerr << "report write failed; the new file may be incomplete\n";
        return 1;
    }
    // Transfer ownership to fclose so its result can be checked without a double close.
    if (std::fclose(report.release()) != 0) {
        std::cerr << "report close failed; the new file may be incomplete\n";
        return 1;
    }
    std::cout << "report saved\n";
}
