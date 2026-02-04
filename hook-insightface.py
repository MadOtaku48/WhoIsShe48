"""
PyInstaller hook for insightface
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
import os

# Collect all insightface submodules
hiddenimports = collect_submodules('insightface')

# Collect data files
datas = collect_data_files('insightface')

# Add metadata
datas += copy_metadata('insightface')

# Manually add InsightFace models from home directory
home_insightface = os.path.expanduser('~/.insightface')
if os.path.exists(home_insightface):
    # Add the entire .insightface directory structure
    datas.append((home_insightface, '.insightface'))