# Contributing to FreeGen

First off, thank you for considering contributing to FreeGen! We welcome contributions of all kinds: bug fixes, new effects, documentation, and more.

## Code of Conduct

By participating, you agree to be respectful and constructive. We follow a standard [Contributor Covenant](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- C++20 compiler (GCC 13+, Clang 16+, MSVC 2022+)
- CMake 3.24+
- Vulkan SDK 1.3+
- SDL2
- PipeWire 0.3+ (Linux) or Windows SDK (Windows)

### Setup

```bash
git clone https://github.com/ShrekDino/Project-FreeGen.git
cd Project-FreeGen
./scripts/manage.sh build
```

## Adding a New Effect

Effects are the heart of FreeGen. Here is how to add one:

### 1. Create a new class implementing `IEffect`

```cpp
// include/freegen/effects/MyEffect.hpp
#include "freegen/effects/IEffect.hpp"

class MyEffect : public freegen::IEffect {
public:
    std::string_view name() const override { return "My Effect"; }
    std::string_view description() const override { return "What it does"; }
    EffectCategory category() const override { return EffectCategory::Upscale; }

    void init(const EffectInitInfo& info) override;
    void shutdown() override;
    void process(vk::CommandBuffer cmd, const EffectInput& input, EffectOutput& output) override;
};
```

### 2. Write the GLSL compute shader

Place your shader in `shaders/my_effect.comp`:

```glsl
#version 460
layout(local_size_x = 8, local_size_y = 8) in;
layout(set = 0, binding = 0, rgba8) uniform readonly image2D uInput;
layout(set = 0, binding = 1, rgba8) uniform writeonly image2D uOutput;
// ... your algorithm
```

### 3. Register in main.cpp

```cpp
effectManager->registerEffect(std::make_unique<MyEffect>());
```

### 4. Add to build

The shader is automatically compiled via `glslc` — just add it to `shaders/`.

## Coding Standards

- Follow `.clang-format` (LLVM style, 4-space indent)
- Follow `.clang-tidy` checks
- Use `camelBack` for functions/variables, `CamelCase` for classes
- Prefix member variables with `m_`
- Use `const` whenever possible
- Prefer `std::span` over raw pointers
- All public API must have Doxygen-style comments

## Pull Request Process

1. Create a feature branch from `dev`
2. Make your changes
3. Format: `./scripts/manage.sh format`
4. Lint: `./scripts/manage.sh lint`
5. Test: `./scripts/manage.sh test`
6. PR against `dev` with clear description

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add FSR 2.0 upscaling effect
fix: correct swapchain resize on Wayland
docs: update capture backend documentation
```

## Testing

Tests use Google Test. Add tests in `src/tests/`:

```cpp
TEST_F(MyEffectTest, DefaultParameters) {
    MyEffect effect;
    EXPECT_EQ(effect.parameters().size(), 2);
}
```

## Questions?

Open a [Discussion](https://github.com/ShrekDino/Project-FreeGen/discussions) or an Issue.
