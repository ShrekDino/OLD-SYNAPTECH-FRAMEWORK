#pragma once

#include <string>
#include <variant>

namespace freegen {

template <typename T, typename E = std::string>
class Result {
public:
    Result(T value) : m_data(std::move(value)) {}
    Result(E error) : m_data(std::move(error)) {}

    bool isOk() const { return std::holds_alternative<T>(m_data); }
    bool isError() const { return std::holds_alternative<E>(m_data); }

    T& value() { return std::get<T>(m_data); }
    const T& value() const { return std::get<T>(m_data); }

    E& error() { return std::get<E>(m_data); }
    const E& error() const { return std::get<E>(m_data); }

    T valueOr(T defaultValue) const {
        if (isOk()) return value();
        return defaultValue;
    }

private:
    std::variant<T, E> m_data;
};

} // namespace freegen
