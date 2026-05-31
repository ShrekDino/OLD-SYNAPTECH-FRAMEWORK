#pragma once

#include <vulkan/vulkan.hpp>
#include <filesystem>
#include <memory>
#include <string>
#include <vector>

namespace freegen {

class Device;

class ShaderModule {
public:
    ShaderModule(const Device& device, const std::filesystem::path& spvPath);
    ShaderModule(const Device& device, std::span<const uint32_t> code, std::string name);
    ~ShaderModule() = default;

    ShaderModule(const ShaderModule&) = delete;
    ShaderModule& operator=(const ShaderModule&) = delete;
    ShaderModule(ShaderModule&&) = default;
    ShaderModule& operator=(ShaderModule&&) = default;

    vk::ShaderModule handle() const { return *m_module; }
    const std::string& name() const { return m_name; }

    vk::PipelineShaderStageCreateInfo stageCreateInfo(vk::ShaderStageFlagBits stage) const;

    static std::vector<uint32_t> ReadFile(const std::filesystem::path& path);

private:
    std::string m_name;
    vk::UniqueShaderModule m_module;
};

} // namespace freegen
