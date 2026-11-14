#ifndef CPP_TUTORIAL_SCORE_HPP
#define CPP_TUTORIAL_SCORE_HPP

#include <charconv>
#include <optional>
#include <string_view>
#include <system_error>

inline std::optional<int> parse_score(std::string_view text) {
    if (text.empty()) {
        return std::nullopt;
    }
    for (const char character : text) {
        if (character < '0' || character > '9') {
            return std::nullopt;
        }
    }
    int score{0};
    const auto result = std::from_chars(text.data(), text.data() + text.size(), score);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()
        || score < 0 || score > 100) {
        return std::nullopt;
    }
    return score;
}

#endif
