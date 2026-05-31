# Effect System

FreeGen's effect system is designed for extensibility. Anyone can add new upscaling algorithms, frame generation models, or image filters without modifying core engine code.

## Architecture

```
IEffect (abstract base class)
├── UpscaleEffect (base for upscalers)
│   ├── FSR1          → FidelityFX Super Resolution 1.0
│   ├── IntegerScale  → Nearest-neighbor integer replication
│   └── Passthrough   → No-op (identity)
├── FrameGenEffect (base for frame generators)
│   ├── FrameGenInterpolate → Motion-adaptive blend
│   └── (future) AI Frame Gen → ONNX/Vulkan ML model
└── FilterEffect (base for image filters)
    ├── (future) CAS      → Contrast Adaptive Sharpening
    ├── (future) Deband   → Banding artifact removal
    └── (future) ColorAdj → Color space adjustment
```

## IEffect Interface

```cpp
class IEffect {
public:
    // Metadata
    virtual std::string_view name() const = 0;
    virtual std::string_view description() const = 0;
    virtual EffectCategory category() const = 0;

    // Lifecycle
    virtual void init(const EffectInitInfo& info) = 0;
    virtual void shutdown() = 0;

    // Processing
    virtual void process(vk::CommandBuffer cmd,
                         const EffectInput& input,
                         EffectOutput& output) = 0;

    // Parameters
    virtual std::span<EffectParam> parameters();
    virtual void setParameter(std::string_view name, float value);
    virtual float getParameter(std::string_view name) const;

    // UI
    virtual void drawSettingsUI();
};
```

## Adding a New Effect

### Step 1: Create the C++ class

```cpp
// include/freegen/effects/MyUpscaler.hpp
#include "freegen/effects/IEffect.hpp"
#include "freegen/render/ComputePipeline.hpp"
#include "freegen/core/ShaderModule.hpp"

class MyUpscaler : public freegen::IEffect {
public:
    std::string_view name() const override { return "My Upscaler"; }
    std::string_view description() const override {
        return "Custom upscaling algorithm description";
    }
    EffectCategory category() const override {
        return EffectCategory::Upscale;
    }

    void init(const EffectInitInfo& info) override {
        // 1. Load shader from disk
        // 2. Create compute pipeline
        // 3. Initialize parameters
    }

    void shutdown() override {
        // Release GPU resources
    }

    void process(vk::CommandBuffer cmd,
                 const EffectInput& input,
                 EffectOutput& output) override {
        // 1. Bind pipeline
        // 2. Push constants
        // 3. Dispatch compute shader
        // 4. Set output
    }

    void drawSettingsUI() override {
        // ImGui controls for parameters
    }

private:
    std::unique_ptr<freegen::ComputePipeline> m_pipeline;
    std::unique_ptr<freegen::ShaderModule> m_shader;
    std::vector<freegen::EffectParam> m_params;
};
```

### Step 2: Write the GLSL compute shader

```glsl
// shaders/my_upscaler.comp
#version 460

layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

layout(set = 0, binding = 0, rgba8) uniform readonly image2D uInput;
layout(set = 0, binding = 1, rgba8) uniform writeonly image2D uOutput;

layout(push_constant) uniform PushConstants {
    float inputWidth;
    float inputHeight;
    float outputWidth;
    float outputHeight;
    float param1;
} pc;

void main() {
    ivec2 outPos = ivec2(gl_GlobalInvocationID.xy);
    // ... your algorithm
    imageStore(uOutput, outPos, result);
}
```

### Step 3: Register

```cpp
// In src/main.cpp
effectManager->registerEffect(std::make_unique<MyUpscaler>());
```

### Step 4: Build

The shader is automatically compiled by `glslc` during the CMake build. No additional build configuration needed.

## Effect Parameters

Effects can expose parameters for runtime adjustment:

```cpp
m_params = {
    {"Sharpness", "Edge sharpening strength",
     EffectParamType::FloatRange, 0.0f, 2.0f, 0.5f, 0.5f},
    {"Scale", "Output scale factor",
     EffectParamType::IntRange, 1.0f, 6.0f, 2.0f, 2.0f}
};
```

Parameters are automatically serialized to config files and exposed in the ImGui UI.

## Built-in Effects

| Name | Type | Description |
|------|------|-------------|
| FSR 1.0 | Upscale | AMD FidelityFX Super Resolution (EASU + RCAS) |
| Integer Scale | Upscale | Nearest-neighbor pixel replication |
| Passthrough | Upscale | No-op, passes input to output unchanged |
| Frame Interpolation | FrameGen | Motion-adaptive blend between consecutive frames |
