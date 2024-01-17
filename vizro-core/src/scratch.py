import yaml

data = [
                        {
                            "if": {"filter_query": "{gdpPercap} < 1045", "column_id": "gdpPercap"},
                            "backgroundColor": "#ff9222",
                        },
                        {
                            "if": {
                                "filter_query": "{gdpPercap} >= 1045 && {gdpPercap} <= 4095",
                                "column_id": "gdpPercap",
                            },
                            "backgroundColor": "#de9e75",
                        },
                        {
                            "if": {
                                "filter_query": "{gdpPercap} > 4095 && {gdpPercap} <= 12695",
                                "column_id": "gdpPercap",
                            },
                            "backgroundColor": "#aaa9ba",
                        },
                        {
                            "if": {"filter_query": "{gdpPercap} > 12695", "column_id": "gdpPercap"},
                            "backgroundColor": "#00b4ff",
                        },
                    ]


# Convert dictionary to YAML
yaml_data = yaml.dump(data, default_flow_style=False)

# Print the YAML data
print(yaml_data)
