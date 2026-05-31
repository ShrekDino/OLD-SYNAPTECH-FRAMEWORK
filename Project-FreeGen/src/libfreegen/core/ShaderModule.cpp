#include "freegen/core/ShaderModule.hpp"
#include "freegen/core/Device.hpp"
#include <fstream>
#include <spdlog/spdlog.h>

namespace freegen {

ShaderModule::ShaderModule(const Device& device, const std::filesystem::path& spvPath) {
    m_name = spvPath.filename().string();
    auto code = ReadFile(spvPath);
    m_module = device.createShaderModule(code);
    spdlog::debug("Loaded shader: {} ({} bytes)", m_name, code.size() * sizeof(uint32_t));
}

ShaderModule::ShaderModule(const Device& device, std::span<const uint32_t> code, std::string name)
    : m_name(std::move(name)) {
    m_module = device.createShaderModule(code);
    spdlog::debug("Created shader: {} ({} bytes)", m_name, code.size() * sizeof(uint32_t));
}

vk::PipelineShaderStageCreateInfo ShaderModule::stageCreateInfo(vk::ShaderStageFlagBits stage) const {
    return vk::PipelineShaderStageCreateInfo{
        .stage = stage,
        .module = m_module.get(),
        .pName = "main"
    };
}

std::vector<uint32_t> ShaderModule::ReadFile(const std::filesystem::path& path) {
    std::ifstream file(path, std::ios::ate | std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open shader file: " + path.string());
    }

    size_t fileSize = static_cast<size_t>(file.tellg());
    if (fileSize == 0) {
        throw std::runtime_error("Shader file is empty: " + path.string());
    }
    if (fileSize % sizeof(uint32_t) != 0) {
        throw std::runtime_error("Shader file size not aligned to 4 bytes: " + path.string());
    }
    std::vector<uint32_t> buffer(fileSize / sizeof(uint32_t));
    file.seekg(0);
    file.read(reinterpret_cast<char*>(buffer.data()), static_cast<std::streamsize>(fileSize));
    file.close();

    return buffer;
}

} // namespace freegen
