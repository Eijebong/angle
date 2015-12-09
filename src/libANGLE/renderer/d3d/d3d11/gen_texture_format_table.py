#!/usr/bin/python
# Copyright 2015 The ANGLE Project Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# gen_texture_format_table.py:
#  Code generation for texture format map
#

import json
import pprint

template = """// GENERATED FILE - DO NOT EDIT.
// Generated by gen_texture_format_table.py using data from texture_format_data.json
//
// Copyright 2015 The ANGLE Project Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
//
// texture_format_table:
//   Queries for full textureFormat information based in internalFormat
//

#include "libANGLE/renderer/d3d/d3d11/texture_format_table.h"

#include "libANGLE/renderer/d3d/d3d11/formatutils11.h"
#include "libANGLE/renderer/d3d/d3d11/internal_format_initializer_table.h"
#include "libANGLE/renderer/d3d/d3d11/load_functions_table.h"
#include "libANGLE/renderer/d3d/d3d11/renderer11_utils.h"
#include "libANGLE/renderer/d3d/d3d11/swizzle_format_info.h"
#include "libANGLE/renderer/d3d/loadimage.h"

namespace rx
{{

namespace d3d11
{{

namespace
{{

typedef bool (*FormatSupportFunction)(const Renderer11DeviceCaps &);

bool AnyDevice(const Renderer11DeviceCaps &deviceCaps)
{{
    return true;
}}

bool OnlyFL10Plus(const Renderer11DeviceCaps &deviceCaps)
{{
    return (deviceCaps.featureLevel >= D3D_FEATURE_LEVEL_10_0);
}}

bool OnlyFL9_3(const Renderer11DeviceCaps &deviceCaps)
{{
    return (deviceCaps.featureLevel == D3D_FEATURE_LEVEL_9_3);
}}

template <DXGI_FORMAT format, bool requireSupport>
bool SupportsFormat(const Renderer11DeviceCaps &deviceCaps)
{{
    // Must support texture, SRV and RTV support
    UINT mustSupport = D3D11_FORMAT_SUPPORT_TEXTURE2D | D3D11_FORMAT_SUPPORT_TEXTURECUBE |
                       D3D11_FORMAT_SUPPORT_SHADER_SAMPLE | D3D11_FORMAT_SUPPORT_MIP |
                       D3D11_FORMAT_SUPPORT_RENDER_TARGET;

    if (d3d11_gl::GetMaximumClientVersion(deviceCaps.featureLevel) > 2)
    {{
        mustSupport |= D3D11_FORMAT_SUPPORT_TEXTURE3D;
    }}

    bool fullSupport = false;
    if (format == DXGI_FORMAT_B5G6R5_UNORM)
    {{
        // All hardware that supports DXGI_FORMAT_B5G6R5_UNORM should support autogen mipmaps, but
        // check anyway.
        mustSupport |= D3D11_FORMAT_SUPPORT_MIP_AUTOGEN;
        fullSupport = ((deviceCaps.B5G6R5support & mustSupport) == mustSupport);
    }}
    else if (format == DXGI_FORMAT_B4G4R4A4_UNORM)
    {{
        fullSupport = ((deviceCaps.B4G4R4A4support & mustSupport) == mustSupport);
    }}
    else if (format == DXGI_FORMAT_B5G5R5A1_UNORM)
    {{
        fullSupport = ((deviceCaps.B5G5R5A1support & mustSupport) == mustSupport);
    }}
    else
    {{
        UNREACHABLE();
        return false;
    }}

    // This 'SupportsFormat' function is used by individual entries in the D3D11 Format Map below,
    // which maps GL formats to DXGI formats.
    if (requireSupport)
    {{
        // This means that ANGLE would like to use the entry in the map if the inputted DXGI format
        // *IS* supported.
        // e.g. the entry might map GL_RGB5_A1 to DXGI_FORMAT_B5G5R5A1, which should only be used if
        // DXGI_FORMAT_B5G5R5A1 is supported.
        // In this case, we should only return 'true' if the format *IS* supported.
        return fullSupport;
    }}
    else
    {{
        // This means that ANGLE would like to use the entry in the map if the inputted DXGI format
        // *ISN'T* supported.
        // This might be a fallback entry. e.g. for ANGLE to use DXGI_FORMAT_R8G8B8A8_UNORM if
        // DXGI_FORMAT_B5G5R5A1 isn't supported.
        // In this case, we should only return 'true' if the format *ISN'T* supported.
        return !fullSupport;
    }}
}}

// End Format Support Functions

// For sized GL internal formats, there are several possible corresponding D3D11 formats depending
// on device capabilities.
// This function allows querying for the DXGI texture formats to use for textures, SRVs, RTVs and
// DSVs given a GL internal format.
const TextureFormat GetD3D11FormatInfo(GLenum internalFormat,
                                       DXGI_FORMAT texFormat,
                                       DXGI_FORMAT srvFormat,
                                       DXGI_FORMAT rtvFormat,
                                       DXGI_FORMAT dsvFormat)
{{
    TextureFormat info;
    info.texFormat = texFormat;
    info.srvFormat = srvFormat;
    info.rtvFormat = rtvFormat;
    info.dsvFormat = dsvFormat;

    // Given a GL internal format, the renderFormat is the DSV format if it is depth- or
    // stencil-renderable,
    // the RTV format if it is color-renderable, and the (nonrenderable) texture format otherwise.
    if (dsvFormat != DXGI_FORMAT_UNKNOWN)
    {{
        info.renderFormat = dsvFormat;
    }}
    else if (rtvFormat != DXGI_FORMAT_UNKNOWN)
    {{
        info.renderFormat = rtvFormat;
    }}
    else if (texFormat != DXGI_FORMAT_UNKNOWN)
    {{
        info.renderFormat = texFormat;
    }}
    else
    {{
        info.renderFormat = DXGI_FORMAT_UNKNOWN;
    }}

    // Compute the swizzle formats
    const gl::InternalFormat &formatInfo = gl::GetInternalFormatInfo(internalFormat);
    if (internalFormat != GL_NONE && formatInfo.pixelBytes > 0)
    {{
        if (formatInfo.componentCount != 4 || texFormat == DXGI_FORMAT_UNKNOWN ||
            srvFormat == DXGI_FORMAT_UNKNOWN || rtvFormat == DXGI_FORMAT_UNKNOWN)
        {{
            // Get the maximum sized component
            unsigned int maxBits = 1;
            if (formatInfo.compressed)
            {{
                unsigned int compressedBitsPerBlock = formatInfo.pixelBytes * 8;
                unsigned int blockSize =
                    formatInfo.compressedBlockWidth * formatInfo.compressedBlockHeight;
                maxBits = std::max(compressedBitsPerBlock / blockSize, maxBits);
            }}
            else
            {{
                maxBits = std::max(maxBits, formatInfo.alphaBits);
                maxBits = std::max(maxBits, formatInfo.redBits);
                maxBits = std::max(maxBits, formatInfo.greenBits);
                maxBits = std::max(maxBits, formatInfo.blueBits);
                maxBits = std::max(maxBits, formatInfo.luminanceBits);
                maxBits = std::max(maxBits, formatInfo.depthBits);
            }}

            maxBits = roundUp(maxBits, 8U);

            const SwizzleFormatInfo &swizzleInfo =
                GetSwizzleFormatInfo(maxBits, formatInfo.componentType);
            info.swizzleTexFormat = swizzleInfo.mTexFormat;
            info.swizzleSRVFormat = swizzleInfo.mSRVFormat;
            info.swizzleRTVFormat = swizzleInfo.mRTVFormat;
        }}
        else
        {{
            // The original texture format is suitable for swizzle operations
            info.swizzleTexFormat = texFormat;
            info.swizzleSRVFormat = srvFormat;
            info.swizzleRTVFormat = rtvFormat;
        }}
    }}
    else
    {{
        // Not possible to swizzle with this texture format since it is either unsized or GL_NONE
        info.swizzleTexFormat = DXGI_FORMAT_UNKNOWN;
        info.swizzleSRVFormat = DXGI_FORMAT_UNKNOWN;
        info.swizzleRTVFormat = DXGI_FORMAT_UNKNOWN;
    }}

    // Check if there is an initialization function for this texture format
    info.dataInitializerFunction = GetInternalFormatInitializer(internalFormat, texFormat);
    // Gather all the load functions for this internal format
    info.loadFunctions = GetLoadFunctionsMap(internalFormat, texFormat);

    ASSERT(info.loadFunctions.size() != 0 || internalFormat == GL_NONE);

    return info;
}}

}}  // namespace

TextureFormat::TextureFormat()
    : texFormat(DXGI_FORMAT_UNKNOWN),
      srvFormat(DXGI_FORMAT_UNKNOWN),
      rtvFormat(DXGI_FORMAT_UNKNOWN),
      dsvFormat(DXGI_FORMAT_UNKNOWN),
      renderFormat(DXGI_FORMAT_UNKNOWN),
      swizzleTexFormat(DXGI_FORMAT_UNKNOWN),
      swizzleSRVFormat(DXGI_FORMAT_UNKNOWN),
      swizzleRTVFormat(DXGI_FORMAT_UNKNOWN),
      dataInitializerFunction(NULL),
      loadFunctions()
{{
}}

const TextureFormat &GetTextureFormatInfo(GLenum internalFormat,
                                          const Renderer11DeviceCaps &renderer11DeviceCaps)
{{
    // clang-format off
    switch (internalFormat)
    {{
{data}
        default:
            break;
    }}
    // clang-format on

    static const TextureFormat defaultInfo;
    return defaultInfo;
}}  // GetTextureFormatInfo

}}  // namespace d3d11

}}  // namespace rx
"""

def get_texture_format_item(idx, texture_format):
    table_data = '';

    tex_format = texture_format["texFormat"] if "texFormat" in texture_format else "DXGI_FORMAT_UNKNOWN"
    srv_format = texture_format["srvFormat"] if "srvFormat" in texture_format else "DXGI_FORMAT_UNKNOWN"
    rtv_format = texture_format["rtvFormat"] if "rtvFormat" in texture_format else "DXGI_FORMAT_UNKNOWN"
    dsv_format = texture_format["dsvFormat"] if "dsvFormat" in texture_format else "DXGI_FORMAT_UNKNOWN"
    requirements_fn = texture_format["requirementsFcn"] if "requirementsFcn" in texture_format else "AnyDevice"

    if idx == 0:
        table_data += '            if (' + requirements_fn + '(renderer11DeviceCaps))\n'
    else:
        table_data += '            else if (' + requirements_fn + '(renderer11DeviceCaps))\n'
    table_data += '            {\n'
    table_data += '                static const TextureFormat textureFormat = GetD3D11FormatInfo(internalFormat,\n'
    table_data += '                                                                              ' + tex_format + ',\n'
    table_data += '                                                                              ' + srv_format + ',\n'
    table_data += '                                                                              ' + rtv_format + ',\n'
    table_data += '                                                                              ' + dsv_format + ');\n'
    table_data += '                return textureFormat;\n'
    table_data += '            }\n'

    return table_data

def parse_json_into_switch_string(json_data):
    table_data = ''
    for internal_format_item in sorted(json_data.iteritems()):
        internal_format = internal_format_item[0]
        table_data += '        case ' + internal_format + ':\n'
        table_data += '        {\n'

        for idx, texture_format in enumerate(sorted(json_data[internal_format])):
            table_data += get_texture_format_item(idx, texture_format)

        table_data += '            else\n'
        table_data += '            {\n'
        table_data += '                break;\n'
        table_data += '            }\n'
        table_data += '        }\n'

    return table_data

with open('texture_format_data.json') as texture_format_json_file:
    texture_format_data = texture_format_json_file.read();
    texture_format_json_file.close()
    json_data = json.loads(texture_format_data)

    table_data = parse_json_into_switch_string(json_data)
    output = template.format(data=table_data)

    with open('texture_format_table_autogen.cpp', 'wt') as out_file:
        out_file.write(output)
        out_file.close()
