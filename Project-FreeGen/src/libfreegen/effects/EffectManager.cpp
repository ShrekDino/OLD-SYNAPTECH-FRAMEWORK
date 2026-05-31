#include "freegen/effects/EffectManager.hpp"
#include <algorithm>
#include <spdlog/spdlog.h>

namespace freegen {

void EffectManager::registerEffect(std::unique_ptr<IEffect> effect) {
    std::string name(effect->name());
    spdlog::info("Registering effect: {} ({})", name,
                 effect->category() == EffectCategory::Upscale ? "Upscale" :
                 effect->category() == EffectCategory::FrameGen ? "FrameGen" :
                 effect->category() == EffectCategory::Filter ? "Filter" : "PreProcess");
    m_effects[name] = std::move(effect);
}

void EffectManager::unregisterEffect(std::string_view name) {
    m_effects.erase(std::string(name));
}

IEffect* EffectManager::getEffect(std::string_view name) const {
    auto it = m_effects.find(std::string(name));
    return it != m_effects.end() ? it->second.get() : nullptr;
}

std::vector<IEffect*> EffectManager::getEffectsByCategory(EffectCategory category) const {
    std::vector<IEffect*> result;
    for (const auto& [_, effect] : m_effects) {
        if (effect->category() == category) {
            result.push_back(effect.get());
        }
    }
    return result;
}

std::vector<IEffect*> EffectManager::allEffects() const {
    std::vector<IEffect*> result;
    result.reserve(m_effects.size());
    for (const auto& [_, effect] : m_effects) {
        result.push_back(effect.get());
    }
    return result;
}

void EffectManager::initAll(const EffectInitInfo& info) {
    for (auto& [_, effect] : m_effects) {
        effect->init(info);
    }
}

void EffectManager::shutdownAll() {
    for (auto& [_, effect] : m_effects) {
        effect->shutdown();
    }
}

EffectManager::EffectChain EffectManager::buildChain() const {
    EffectChain chain;
    for (const auto& [_, effect] : m_effects) {
        switch (effect->category()) {
        case EffectCategory::PreProcess:
            chain.preProcess.push_back(effect.get());
            break;
        case EffectCategory::Upscale:
            chain.upscale.push_back(effect.get());
            break;
        case EffectCategory::FrameGen:
            chain.frameGen.push_back(effect.get());
            break;
        case EffectCategory::Filter:
            chain.filters.push_back(effect.get());
            break;
        }
    }
    return chain;
}

} // namespace freegen
