# Global Mantine (DMC) theme for dmc.MantineProvider.
# Reference: https://www.dash-mantine-components.com/theme-object
mantine_theme = {
    "primaryColor": "gray",
    "defaultRadius": 0,
    "font-family": "var(--bs-body-font-family)",
    "headings": {
        "sizes": {
            "h1": {"fontSize": "2rem"},
            "h2": {"fontSize": "1.5rem"},
            "h3": {"fontSize": "1.25rem"},
            "h4": {"fontSize": "1rem"},
        }
    },
    "components": {
        "Card": {
            "styles": {
                "root": {
                    "backgroundColor": "var(--bs-card-bg)",
                    "boxShadow": "var(--bs-box-shadow)",
                }
            }
        },
        "Paper": {
            "styles": {
                "root": {
                    "backgroundColor": "var(--bs-card-bg)",
                    "boxShadow": "var(--bs-box-shadow)",
                    "border": "1px solid var(--bs-border-color)",
                }
            }
        },
        "Progress": {
            "styles": {
                "section": {
                    "backgroundColor": "var(--bs-primary)",
                }
            }
        },
        "Stepper": {
            "styles": {
                "stepIcon": {
                    "backgroundColor": "var(--bs-primary-bg-subtle)",
                    "color": "var(--bs-secondary)",
                    "borderColor": "var(--bs-border-color)",
                }
            }
        },
        "Alert": {
            "styles": {
                "root": {
                    "backgroundColor": "var(--bs-primary-bg-subtle)",
                    "borderLeft": "4px solid var(--alert-color)",
                }
            }
        },
        "Highlight": {
            "defaultProps": {
                "color": "cyan",
            }
        },
        "Blockquote": {
            "styles": {
                "root": {
                    "backgroundColor": "var(--bs-primary-bg-subtle)",
                    "borderLeft": "4px solid var(--bs-secondary)",
                }
            }
        },
        "Accordion": {
            "styles": {
                "item": {
                    "--item-filled-color": "var(--bs-primary-bg-subtle)",
                    "--item-border-color": "var(--bs-border-color)",
                }
            }
        },
        "Tabs": {
            "styles": {
                "root": {
                    "--tab-hover-color": "var(--bs-highlight-bg)",
                    "--tabs-color": "var(--bs-primary)",
                }
            }
        },
        "Timeline": {
            "defaultProps": {
                "lineWidth": 2,
                "bulletSize": 16,
            }
        },
        "RadioIndicator": {
            "defaultProps": {"size": "xs"},
            "styles": {"indicator": {"--radio-icon-color": "var(--bs-primary)"}},
        },
        "Checkbox": {
            "defaultProps": {"size": "xs"},
        },
        "Slider": {
            "defaultProps": {"size": "xs"},
        },
        "RangeSlider": {
            "defaultProps": {"size": "xs"},
        },
        "Chip": {
            "defaultProps": {"color": "primary"},
            "styles": {
                "label": {
                    "--chip-bg": "var(--bs-primary)",
                    "--chip-color": "var(--text-primary-inverted)",
                    "--chip-icon-color": "var(--text-primary-inverted)",
                    "--chip-hover": "var(--bs-primary-text-emphasis)",
                }
            },
        },
    },
}
