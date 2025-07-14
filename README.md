# Smooth Normal Transfer Tool for Maya

**Author:** Lefi Shan (Leficious)  
**Date:** July 13, 2025  
**Version:** 1.1  
**Compatible with:** Autodesk Maya (tested in 2024+)

---

## Overview

The Smooth Normal Transfer Tool is a Python script for Autodesk Maya that transfers clean, unified vertex normals from a generated ovoid preview sphere to a target mesh. Ideal for stylized assets like foliage, this tool enables artists to achieve soft shading with minimal setup.

---

## Features

- Auto-generates a smooth sphere based on the target’s bounding box
- Interactive UI with:
  - Scale, resolution, and world offset sliders
  - Live preview toggle
  - Reset to default values
- Auto-combine prompt for multi-object selections
- One-click transfer with confirmation dialog

---

## Installation

1. Download or copy the script file.
2. In Maya, open the **Script Editor** and paste the script into a Python tab.
3. Execute the script.
4. The tool will launch automatically. You can also run `smart_launch_normal_tool()` from the script anytime.

---

## Usage

1. Select a mesh object in your scene.
2. Adjust the preview sphere settings using the UI.
3. Click **Show Preview** to visualize the sphere.
4. Click **Apply Transfer** to project the smooth normals onto your mesh.
