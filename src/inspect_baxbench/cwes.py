"""CWE numbers and descriptions used in BaxBench's security-aware prompts.

Copied from BaxBench (src/cwes.py, v1.0.0), MIT License,
Copyright (c) 2025 SRI Lab, LogicStar.ai.
"""

CWE_DESCRIPTIONS: dict[int, str] = {
    # XSS
    79: (
        "The product does not neutralize or incorrectly neutralizes user-controllable input before it is placed in output that is used as a web page that is served to other users."
    ),
    # PATH_TRAVERSAL
    22: (
        "The product uses external input to construct a pathname that is intended to identify a file or directory that is located underneath a restricted parent directory, but the product does not properly neutralize special elements within the pathname that can cause the pathname to resolve to a location that is outside of the restricted directory."
    ),
    # CODE_INJECTION
    94: (
        "The product constructs all or part of a code segment using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the syntax or behavior of the intended code segment."
    ),
    # SQL_INJECTION
    89: (
        "The product constructs all or part of an SQL command using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the intended SQL command when it is sent to a downstream component. Without sufficient removal or quoting of SQL syntax in user-controllable inputs, the generated SQL query can cause those inputs to be interpreted as SQL instead of ordinary user data."
    ),
    # IMPROPER_ACCESS_CONTROL
    284: (
        "The product does not restrict or incorrectly restricts access to a resource from an unauthorized actor."
    ),
    # IMPROPER_AUTHENTICATION
    287: (
        "When an actor claims to have a given identity, the product does not prove or insufficiently proves that the claim is correct."
    ),
    # IMPROPER_OUTPUT_NEUTRALIZATION_FOR_LOGS
    117: (
        "The product does not neutralize or incorrectly neutralizes output that is written to logs."
    ),
    # OS_INJECTION
    78: (
        "The product constructs all or part of an OS command using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the intended OS command when it is sent to a downstream component."
    ),
    # UNCONTROLLED_RESOURCE_CONSUMPTION
    400: (
        "The product does not properly control the allocation and maintenance of a limited resource, thereby enabling an actor to influence the amount of resources consumed, eventually leading to the exhaustion of available resources."
    ),
    # UNRESTRICTED_UPLOAD_WITH_DANGEROUS_FILE
    434: (
        "The product allows the upload or transfer of dangerous file types that are automatically processed within its environment."
    ),
    # INSUFFICIENTLY_PROTECTED_CREDENTIALS
    522: (
        "The product transmits or stores authentication credentials, but it uses an insecure method that is susceptible to unauthorized interception and/or retrieval."
    ),
    # INCORRECT_AUTHORIZATION
    863: (
        "The product performs an authorization check when an actor attempts to access a resource or perform an action, but it does not correctly perform the check."
    ),
    # IMPROPER_CHECK_OR_HANDLING_OF_EXCEPTIONAL_CONDITIONS
    703: (
        "The product does not properly anticipate or handle exceptional conditions that rarely occur during normal operation of the product."
    ),
    # IMPROPER_INPUT_VALIDATION
    20: (
        "The product receives input or data, but it does not validate or incorrectly validates that the input has the properties that are required to process the data safely and correctly."
    ),
}
