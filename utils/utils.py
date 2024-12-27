#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tools for Terraform code generation
"""

import re

def to_snake_case(text):
    """
    Converts string to snake_case.
    @param text: The string to be converted to snake_case.
    @return: The converted string in snake_case format.
    """
    # Replace spaces with underscores
    text = re.sub(r'[\s]+', '_', text)
    # Insert underscores before each capital letter
    text = re.sub(r'(?<!^)(?=[A-Z])', '_', text)
    return text.lower()

def tf_name(text):
    """
    Converts string to Terraform resource name.
    @param text: The string to be converted to Terraform resource name.
    @return: The converted string in Terraform resource name format.
    """
    return re.sub(r'[^a-zA-Z0-9]', '_', text).lower()
