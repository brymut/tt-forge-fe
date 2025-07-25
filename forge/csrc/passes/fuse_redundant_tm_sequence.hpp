// SPDX-FileCopyrightText: © 2024 Tenstorrent AI ULC
//
// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <string>
#include <unordered_map>

#include "ops/op.hpp"
#include "passes/passes_utils.hpp"

namespace tt::passes
{
using OpType = tt::graphlib::OpType;
struct OpTypeItem
{
    std::string op_name;
    std::vector<OpType::Attr> attrs;
    bool check_attrs;
    OpTypeItem(OpType const& op_type, bool check_attrs) :
        op_name(op_type.name()),
        attrs(
            op_type.type() == ops::OpType::Transpose
                ? std::vector<OpType::Attr>({op_type.attr_as<int>("dim0"), op_type.attr_as<int>("dim1")})
                : op_type.legacy_attrs_),
        check_attrs(check_attrs)
    {
    }

    OpTypeItem(std::string const& op_name, std::vector<OpType::Attr> attrs, bool check_attrs) :
        op_name(op_name), attrs(attrs), check_attrs(check_attrs)
    {
    }

    OpType as_op_type() const
    {
        return op_name == "transpose"
                   ? graphlib::OpType(
                         op_name, {}, {{"dim0", std::get<int>(attrs[0])}, {"dim1", std::get<int>(attrs[1])}})
                   : graphlib::OpType(op_name, attrs);
    }
};

using TMPattern = std::vector<OpTypeItem>;
using TMPatternPairs = std::vector<std::pair<TMPattern, TMPattern>>;

// PreDefine TM sequence pattern
static TMPattern pattern_1 = {
    OpTypeItem("reshape", {}, false),
    OpTypeItem("transpose", {-3, -1}, true),
    OpTypeItem("transpose", {-2, -1}, true),
    OpTypeItem("reshape", {}, false),
};

static TMPattern replace_1 = {
    OpTypeItem("transpose", {-2, -1}, true),
};

static TMPattern pattern_2 = {
    OpTypeItem("transpose", {-2, -1}, true),
    OpTypeItem("reshape", {}, false),
    OpTypeItem("transpose", {-3, -2}, true),
    OpTypeItem("transpose", {-2, -1}, true),
    OpTypeItem("reshape", {}, false),
};

static TMPattern replace_2_0 = {
    OpTypeItem("reshape", {1, 2166, 21}, false),
};

static TMPattern replace_2_1 = {
    OpTypeItem("reshape", {1, 600, 21}, false),
};

static TMPattern replace_2_2 = {
    OpTypeItem("reshape", {1, 150, 21}, false),
};

static TMPattern replace_2_3 = {
    OpTypeItem("reshape", {1, 54, 21}, false),
};

static TMPattern replace_2_4 = {
    OpTypeItem("reshape", {1, 24, 21}, false),
};

static TMPattern replace_2_5 = {
    OpTypeItem("reshape", {1, 6, 21}, false),
};

static TMPattern replace_2_6 = {
    OpTypeItem("reshape", {1, 2166, 4}, false),
};

static TMPattern replace_2_7 = {
    OpTypeItem("reshape", {1, 600, 4}, false),
};

static TMPattern replace_2_8 = {
    OpTypeItem("reshape", {1, 150, 4}, false),
};

static TMPattern replace_2_9 = {
    OpTypeItem("reshape", {1, 54, 4}, false),
};

static TMPattern replace_2_10 = {
    OpTypeItem("reshape", {1, 24, 4}, false),
};

static TMPattern replace_2_11 = {
    OpTypeItem("reshape", {1, 6, 4}, false),
};

static TMPattern replace_2_12 = {
    OpTypeItem("reshape", {1, 384, 12}, false),
};

static TMPattern replace_2_13 = {
    OpTypeItem("reshape", {1, 512, 12}, false),
};

static TMPattern replace_2_14 = {
    OpTypeItem("reshape", {1, 384, 1}, false),
};

static TMPattern replace_2_15 = {
    OpTypeItem("reshape", {1, 512, 1}, false),
};

static TMPattern pattern_3 = {
    OpTypeItem("transpose", {-2, -1}, true),
    OpTypeItem("reshape", {}, false),
    OpTypeItem("transpose", {-4, -2}, true),
    OpTypeItem("transpose", {-3, -1}, true),
    OpTypeItem("reshape", {}, false),
};

static TMPattern replace_3_0 = {
    OpTypeItem("reshape", {1, 90000, 91}, false),
};

static TMPattern replace_3_1 = {
    OpTypeItem("reshape", {1, 22500, 91}, false),
};

static TMPattern replace_3_2 = {
    OpTypeItem("reshape", {1, 5625, 91}, false),
};

static TMPattern replace_3_3 = {
    OpTypeItem("reshape", {1, 1521, 91}, false),
};

static TMPattern replace_3_4 = {
    OpTypeItem("reshape", {1, 441, 91}, false),
};

static TMPattern replace_3_5 = {
    OpTypeItem("reshape", {1, 90000, 4}, false),
};

static TMPattern replace_3_6 = {
    OpTypeItem("reshape", {1, 22500, 4}, false),
};

static TMPattern replace_3_7 = {
    OpTypeItem("reshape", {1, 5625, 4}, false),
};

static TMPattern replace_3_8 = {
    OpTypeItem("reshape", {1, 1521, 4}, false),
};

static TMPattern replace_3_9 = {
    OpTypeItem("reshape", {1, 441, 4}, false),
};

static TMPattern pattern_4 = {
    OpTypeItem("transpose", {-2, -1}, true),
    OpTypeItem("reshape", {}, false),
    OpTypeItem("transpose", {-3, -2}, true),
    OpTypeItem("transpose", {-2, -1}, true),
};

static TMPatternPairs pattern_map = {
    {pattern_1, replace_1},    {pattern_2, replace_2_0},  {pattern_2, replace_2_1},  {pattern_2, replace_2_2},
    {pattern_2, replace_2_3},  {pattern_2, replace_2_4},  {pattern_2, replace_2_5},  {pattern_2, replace_2_6},
    {pattern_2, replace_2_7},  {pattern_2, replace_2_8},  {pattern_2, replace_2_9},  {pattern_2, replace_2_10},
    {pattern_2, replace_2_11}, {pattern_2, replace_2_12}, {pattern_2, replace_2_13}, {pattern_2, replace_2_14},
    {pattern_2, replace_2_15}, {pattern_3, replace_3_0},  {pattern_3, replace_3_1},  {pattern_3, replace_3_2},
    {pattern_3, replace_3_3},  {pattern_3, replace_3_4},  {pattern_3, replace_3_5},  {pattern_3, replace_3_6},
    {pattern_3, replace_3_7},  {pattern_3, replace_3_8},  {pattern_3, replace_3_9},
};

bool fuse_tm_sequences(tt::graphlib::Graph* graph, TMPatternPairs& pattern_map_ = pattern_map);
}  // namespace tt::passes
