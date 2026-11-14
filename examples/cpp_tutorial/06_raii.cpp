#include <iostream>
#include <memory>
#include <string>
#include <utility>

int main() {
    auto owner = std::make_unique<std::string>("owned resource");
    std::cout << *owner << '\n';

    auto next_owner = std::move(owner);
    std::cout << std::boolalpha << "old owner empty=" << (owner == nullptr) << '\n';
    std::cout << "new owner=" << *next_owner << '\n';
    // next_owner automatically deletes its string at the end of this scope.
}
