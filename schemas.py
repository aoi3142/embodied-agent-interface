goal_schema = {
    "strict": True,
    "name": "goal_schema",
    "schema": {
        "type": "object",
        "properties": {
            "node goals": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {
                        "anyOf": [
                            {"type": "string"},
                            {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "maxItems": 2
                            }
                        ]
                    },
                    "minItems": 2,
                    "maxItems": 2
                }
            },
            "edge goals": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 3
                }
            }
        },
        "required": ["node goals", "edge goals"],
        "additionalProperties": False
    }
}
subgoal_schema = {
    "strict": True,
    "name": "subgoal_schema",
    "schema": {
        "type": "object",
        "properties": {
            "output": {
                "type": "array",
                "items": {
                    "type": "string",
                    # "pattern": ""
                },
            }
        },
        "required": ["output"],
        "additionalProperties": False
    }
}
action_schema = {
    "strict": True,
    "name": "action_schema",
    "schema": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "actions": {
                    "type": "string"
                },
                "object": {
                    "type": "string"
                }
            },
            "required": ["actions", "object"],
            "additionalProperties": False
        }
    }
}
transition_schema = {
    "strict": True,
    "name": "transition_schema",
    "schema": {
        "type": "object",
        "properties": {
            "output": {
                "type": "string",
                # "pattern": "\(\s*:action\b[\s\S]*?:parameters\b[\s\S]*?:precondition\b[\s\S]*?:effect\b[\s\S]*?\n\)+"
            }
        },
        "required": ["output"],
        "additionalProperties": False
    }
}
schemas = [goal_schema, subgoal_schema, action_schema, transition_schema]