// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2022 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <pow.h>

#include <arith_uint256.h>
#include <chain.h>
#include <primitives/block.h>
#include <serialize.h>
#include <span.h>
#include <streams.h>
#include <uint256.h>
#include <version.h>

#include <argon2.h>

std::atomic<bool> g_use_argon_pow{false};

// Network identifier salt for Argon2id (first 8 bytes of SHA256("DigiDollar PoW")).
// Argon2 requires a salt of at least 8 bytes. This fixed salt ensures that even
// if someone reuses this code with different header formats, the PoW is unique
// to this network.
static const unsigned char NET_SALT[8] = {
    0xc4, 0x33, 0x6e, 0x1c, 0xd6, 0x89, 0x8a, 0xe3
};

// ASIC-resistant memory-hard hash function (replaces double-SHA256 for PoW).
// Uses Argon2id with 256 MiB memory, 3 iterations, and 2 lanes.
// The block header is serialized as the password; the network salt ensures
// domain separation from other Argon2id-based chains.
uint256 CustomHash(const CBlockHeader& header)
{
    // Serialize the block header into a canonical byte sequence
    CDataStream ss(SER_NETWORK, PROTOCOL_VERSION);
    ss << header;
    Span<const unsigned char> headerData{MakeUCharSpan(ss)};

    // Argon2id parameters:
    //   time_cost  = 3    (3 passes — defense against tradeoff attacks)
    //   mem_cost   = 256MB (expressed in KiB: 256 * 1024 = 262144)
    //   parallelism = 2   (2 lanes — suitable for consumer CPUs)
    constexpr uint32_t t_cost = 3;
    constexpr uint32_t m_cost = 262144;  // 256 MiB
    constexpr uint32_t parallelism = 2;

    uint256 result;
    int rc = argon2id_hash_raw(
        t_cost, m_cost, parallelism,
        headerData.data(), headerData.size(),
        NET_SALT, sizeof(NET_SALT),
        result.begin(), result.size()
    );
    if (rc != ARGON2_OK) {
        throw std::runtime_error(
            std::string("CustomHash: Argon2id failed: ") + argon2_error_message(rc));
    }
    return result;
}

unsigned int CalculateNextWorkRequired(const CBlockIndex* pindexLast, int64_t nFirstBlockTime, const Consensus::Params& params)
{
    if (params.fPowNoRetargeting)
        return pindexLast->nBits;

    int64_t nActualTimespan = pindexLast->GetBlockTime() - nFirstBlockTime;
    nActualTimespan = std::max(nActualTimespan, params.nPowTargetTimespan / 4);
    nActualTimespan = std::min(nActualTimespan, params.nPowTargetTimespan * 4);

    const arith_uint256 bnPowLimit = UintToArith256(params.powLimit);
    arith_uint256 bnNew;
    bnNew.SetCompact(pindexLast->nBits);
    bnNew *= nActualTimespan;
    bnNew /= params.nPowTargetTimespan;

    if (bnNew > bnPowLimit)
        bnNew = bnPowLimit;

    return bnNew.GetCompact();
}

unsigned int GetNextWorkRequired(const CBlockIndex* pindexLast,
                                 const CBlockHeader* pblock,
                                 const Consensus::Params& params)
{
    assert(pindexLast != nullptr);
    unsigned int nProofOfWorkLimit = UintToArith256(params.powLimit).GetCompact();

    // Accelerated retarget: adjust every 60 blocks (instead of 2016).
    // With 120s block spacing, this gives a ~2-hour window.
    constexpr int64_t ADJUSTMENT_INTERVAL = 60;

    // Only change once per 60-block adjustment window
    if ((pindexLast->nHeight + 1) % ADJUSTMENT_INTERVAL != 0)
    {
        if (params.fPowAllowMinDifficultyBlocks)
        {
            if (pblock->GetBlockTime() > pindexLast->GetBlockTime() + params.nPowTargetSpacing * 2)
                return nProofOfWorkLimit;
            const CBlockIndex* pindex = pindexLast;
            while (pindex->pprev &&
                   pindex->nHeight % ADJUSTMENT_INTERVAL != 0 &&
                   pindex->nBits == nProofOfWorkLimit) {
                pindex = pindex->pprev;
            }
            return pindex->nBits;
        }
        return pindexLast->nBits;
    }

    int nHeightFirst = pindexLast->nHeight - (ADJUSTMENT_INTERVAL - 1);
    assert(nHeightFirst >= 0);
    const CBlockIndex* pindexFirst = pindexLast->GetAncestor(nHeightFirst);
    assert(pindexFirst);

    return CalculateNextWorkRequired(pindexLast, pindexFirst->GetBlockTime(), params);
}

// Check that on difficulty adjustments, the new difficulty does not increase
// or decrease beyond the permitted limits.
bool PermittedDifficultyTransition(const Consensus::Params& params, int64_t height, uint32_t old_nbits, uint32_t new_nbits)
{
    if (params.fPowAllowMinDifficultyBlocks) return true;

    if (height % params.DifficultyAdjustmentInterval() == 0) {
        int64_t smallest_timespan = params.nPowTargetTimespan / 4;
        int64_t largest_timespan = params.nPowTargetTimespan * 4;

        const arith_uint256 pow_limit = UintToArith256(params.powLimit);
        arith_uint256 observed_new_target;
        observed_new_target.SetCompact(new_nbits);

        arith_uint256 largest_difficulty_target;
        largest_difficulty_target.SetCompact(old_nbits);
        largest_difficulty_target *= largest_timespan;
        largest_difficulty_target /= params.nPowTargetTimespan;
        if (largest_difficulty_target > pow_limit) {
            largest_difficulty_target = pow_limit;
        }
        arith_uint256 maximum_new_target;
        maximum_new_target.SetCompact(largest_difficulty_target.GetCompact());
        if (maximum_new_target < observed_new_target) return false;

        arith_uint256 smallest_difficulty_target;
        smallest_difficulty_target.SetCompact(old_nbits);
        smallest_difficulty_target *= smallest_timespan;
        smallest_difficulty_target /= params.nPowTargetTimespan;
        if (smallest_difficulty_target > pow_limit) {
            smallest_difficulty_target = pow_limit;
        }
        arith_uint256 minimum_new_target;
        minimum_new_target.SetCompact(smallest_difficulty_target.GetCompact());
        if (minimum_new_target > observed_new_target) return false;
    } else if (old_nbits != new_nbits) {
        return false;
    }
    return true;
}

// Validates proof-of-work by checking that the block header hash (computed via
// the ASIC-resistant CustomHash) meets the claimed target.
// NOTE: The caller must pass the hash already computed by CustomHash (called
// from CBlockHeader::GetHash()). In a full production system, you may compute
// the hash here instead, but the current architecture computes it once in
// GetHash() and caches it in the CBlockIndex.
bool CheckProofOfWork(uint256 hash, unsigned int nBits, const Consensus::Params& params)
{
    bool fNegative;
    bool fOverflow;
    arith_uint256 bnTarget;

    bnTarget.SetCompact(nBits, &fNegative, &fOverflow);

    // Check range
    if (fNegative || bnTarget == 0 || fOverflow || bnTarget > UintToArith256(params.powLimit))
        return false;

    // Check proof of work matches claimed amount
    if (UintToArith256(hash) > bnTarget)
        return false;

    return true;
}
