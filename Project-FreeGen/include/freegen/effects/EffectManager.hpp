#pragma once

#include "freegen/effects/IEffect.hpp"
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

namespace freegen {

class EffectManager {
public:
    EffectManager() = default;
    ~EffectManager() = default;

    void registerEffect(std::unique_ptr<IEffect> effect);
    void unregisterEffect(std::string_view name);

    IEffect* getEffect(std::string_view name) const;
    std::vector<IEffect*> getEffectsByCategory(EffectCategory category) const;

    std::vector<IEffect*> allEffects() const;
    size_t effectCount() const { return m_effects.size(); }

    void initAll(const EffectInitInfo& info);
    void shutdownAll();

    struct EffectChain {
        std::vector<IEffect*> preProcess;
        std::vector<IEffect*> upscale;
        std::vector<IEffect*> frameGen;
        std::vector<IEffect*> filters;
    };

    EffectChain buildChain() const;

private:
    std::unordered_map<std::string, std::unique_ptr<IEffect>> m_effects;
};

} // namespace freegen
