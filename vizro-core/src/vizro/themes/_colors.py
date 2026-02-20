from types import SimpleNamespace

# Reference: See Figma file for DS color palettes
colors = SimpleNamespace(
    # Qualitative
    blue="#097DFE",
    dark_purple="#6F39E3",
    turquoise="#05D0F0",
    dark_green="#0F766E",
    light_purple="#8C8DE9",
    light_green="#11B883",
    light_pink="#E77EC2",
    dark_pink="#C84189",
    yellow="#C0CA33",
    gray="#3E495B",
    # Sequential
    blue_100="#DBEBFE",
    blue_200="#BDDCFE",
    blue_300="#8CC6FF",
    blue_400="#4BA5FF",
    blue_500="#097DFE",
    blue_600="#0063F6",
    blue_700="#004DE0",
    blue_800="#0B40B4",
    blue_900="#163B8B",
    purple_100="#EBE9FC",
    purple_200="#DAD6FB",
    purple_300="#C0B6FB",
    purple_400="#A08AF8",
    purple_500="#855FF6",
    purple_600="#6F39E3",
    purple_700="#6630D5",
    purple_800="#5529B1",
    purple_900="#47268E",
    turquoise_100="#D2F9FC",
    turquoise_200="#AAF2FA",
    turquoise_300="#68E8F7",
    turquoise_400="#05D0F0",
    turquoise_500="#00B7D4",
    turquoise_600="#0092B2",
    turquoise_700="#087490",
    turquoise_800="#155E74",
    turquoise_900="#1A4E61",
    green_100="#D4F9E7",
    green_200="#ADF1D3",
    green_300="#73E6BA",
    green_400="#2CD099",
    green_500="#11B883",
    green_600="#07966B",
    green_700="#0B7859",
    green_800="#0F5E48",
    green_900="#114D3C",
    pink_100="#F8E9F5",
    pink_200="#F3D3EB",
    pink_300="#EDAFDD",
    pink_400="#E77EC2",
    pink_500="#DB5AB1",
    pink_600="#C84194",
    pink_700="#AB3478",
    pink_800="#8D2D63",
    pink_900="#742A53",
    yellow_100="#F4F9D2",
    yellow_200="#EAF3A9",
    yellow_300="#DBE973",
    yellow_400="#CBD740",
    yellow_500="#C0CA33",
    yellow_600="#979912",
    yellow_700="#76720C",
    yellow_800="#605B11",
    yellow_900="#514C15",
    gray_100="#EFF1F4",
    gray_200="#E0E4E9",
    gray_300="#C9D0D9",
    gray_400="#97A1B0",
    gray_500="#6D788A",
    gray_600="#505C6F",
    gray_700="#3E495B",
    gray_800="#2A3241",
    gray_900="#1D222E",
    # Special colors
    transparent="rgba(0, 0, 0, 0)",
    white="#FFFFFF",
    black="#000000",
)
"""Colors used by palettes, plus additional colors.

Examples:
    ```python
    from vizro.themes import colors
    colors.dark_green
    # gives "#0F766E"
    ```

![Colors](../../assets/user_guides/themes/colors.png)
"""
