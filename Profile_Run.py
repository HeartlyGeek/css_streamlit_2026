# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 11:58:05 2026

@author: Emmie
"""

import subprocess

file = "Researcher_Profile.py"

subprocess.Popen(
    ["streamlit", "run", file], shell=True
)
