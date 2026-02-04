#!/usr/bin/env python3
"""
Runtime hook for InsightFace to properly set model paths in PyInstaller bundle
"""

import os
import sys

# Set InsightFace model directory when running as bundled app
if hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller bundle
    # Models are bundled with their full path structure
    bundle_dir = sys._MEIPASS
    
    # Set HOME environment variable to bundle directory
    # This makes ~/.insightface resolve to the bundled location
    os.environ['HOME'] = bundle_dir
    os.environ['USERPROFILE'] = bundle_dir  # For Windows
    
    # Also set INSIGHTFACE_ROOT explicitly
    insightface_root = os.path.join(bundle_dir, '.insightface')
    os.environ['INSIGHTFACE_ROOT'] = insightface_root
    
    print(f"[Runtime Hook] Bundle directory: {bundle_dir}")
    print(f"[Runtime Hook] HOME set to: {os.environ['HOME']}")
    print(f"[Runtime Hook] INSIGHTFACE_ROOT set to: {insightface_root}")
    
    # Check if models exist
    buffalo_l_path = os.path.join(insightface_root, 'models', 'buffalo_l')
    if os.path.exists(buffalo_l_path):
        print(f"[Runtime Hook] buffalo_l model found at: {buffalo_l_path}")
        for file in os.listdir(buffalo_l_path):
            file_path = os.path.join(buffalo_l_path, file)
            print(f"[Runtime Hook]   - {file} (exists: {os.path.isfile(file_path)})")
    else:
        print(f"[Runtime Hook] WARNING: buffalo_l model not found at: {buffalo_l_path}")
        
    # List what's in the bundle directory
    insightface_dir = os.path.join(bundle_dir, '.insightface')
    if os.path.exists(insightface_dir):
        print(f"[Runtime Hook] Contents of {insightface_dir}:")
        for root, dirs, files in os.walk(insightface_dir):
            level = root.replace(insightface_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"[Runtime Hook] {indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files
                print(f"[Runtime Hook] {subindent}{file}")