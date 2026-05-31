#include <gtest/gtest.h>
#include "freegen/effects/EffectManager.hpp"
#include "freegen/effects/FSR1.hpp"
#include "freegen/effects/IntegerScale.hpp"
#include "freegen/effects/FrameGenInterpolate.hpp"

namespace freegen {

class EffectManagerTest : public ::testing::Test {
protected:
    void SetUp() override {
        manager = std::make_unique<EffectManager>();
        manager->registerEffect(std::make_unique<FSR1>());
        manager->registerEffect(std::make_unique<IntegerScale>());
        manager->registerEffect(std::make_unique<FrameGenInterpolate>());
    }

    std::unique_ptr<EffectManager> manager;
};

TEST_F(EffectManagerTest, EffectsRegistered) {
    EXPECT_EQ(manager->effectCount(), 3);
}

TEST_F(EffectManagerTest, GetEffectByName) {
    auto* fsr = manager->getEffect("FSR 1.0");
    ASSERT_NE(fsr, nullptr);
    EXPECT_EQ(fsr->name(), "FSR 1.0");
    EXPECT_EQ(fsr->category(), EffectCategory::Upscale);

    auto* integer = manager->getEffect("Integer Scale");
    ASSERT_NE(integer, nullptr);
    EXPECT_EQ(integer->name(), "Integer Scale");
    EXPECT_EQ(integer->category(), EffectCategory::Upscale);

    auto* fg = manager->getEffect("Frame Interpolation");
    ASSERT_NE(fg, nullptr);
    EXPECT_EQ(fg->name(), "Frame Interpolation");
    EXPECT_EQ(fg->category(), EffectCategory::FrameGen);
}

TEST_F(EffectManagerTest, GetNonExistentEffect) {
    auto* effect = manager->getEffect("NonExistent");
    EXPECT_EQ(effect, nullptr);
}

TEST_F(EffectManagerTest, GetEffectsByCategory) {
    auto upscales = manager->getEffectsByCategory(EffectCategory::Upscale);
    EXPECT_EQ(upscales.size(), 2);

    auto frameGens = manager->getEffectsByCategory(EffectCategory::FrameGen);
    EXPECT_EQ(frameGens.size(), 1);

    auto filters = manager->getEffectsByCategory(EffectCategory::Filter);
    EXPECT_EQ(filters.size(), 0);
}

TEST_F(EffectManagerTest, UnregisterEffect) {
    manager->unregisterEffect("FSR 1.0");
    EXPECT_EQ(manager->effectCount(), 2);
    EXPECT_EQ(manager->getEffect("FSR 1.0"), nullptr);
}

TEST_F(EffectManagerTest, BuildChain) {
    auto chain = manager->buildChain();
    EXPECT_EQ(chain.upscale.size(), 2);
    EXPECT_EQ(chain.frameGen.size(), 1);
    EXPECT_EQ(chain.preProcess.size(), 0);
    EXPECT_EQ(chain.filters.size(), 0);
}

TEST(FSR1Test, DefaultParameters) {
    FSR1 fsr;
    EXPECT_EQ(fsr.name(), "FSR 1.0");
    EXPECT_EQ(fsr.description(), "AMD FidelityFX Super Resolution 1.0 (EASU + RCAS)");
    EXPECT_EQ(fsr.category(), EffectCategory::Upscale);

    auto params = fsr.parameters();
    EXPECT_EQ(params.size(), 1);
    EXPECT_EQ(params[0].name, "Sharpness");
}

TEST(IntegerScaleTest, DefaultParameters) {
    IntegerScale scale;
    EXPECT_EQ(scale.name(), "Integer Scale");
    EXPECT_EQ(scale.category(), EffectCategory::Upscale);

    auto params = scale.parameters();
    EXPECT_EQ(params.size(), 1);
    EXPECT_EQ(params[0].name, "Scale");
}

TEST(FrameGenInterpolateTest, DefaultParameters) {
    FrameGenInterpolate fg;
    EXPECT_EQ(fg.name(), "Frame Interpolation");
    EXPECT_EQ(fg.category(), EffectCategory::FrameGen);
    EXPECT_FALSE(fg.parameters().empty());
}

} // namespace freegen
