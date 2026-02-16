#!/usr/bin/env python3
"""Fix lobster sprite transparency: fill interior holes with black.

Problem: Background removal treated ALL black pixels as background,
including eyes, shadows, and details inside the lobster body.

Solution: Flood-fill from edges to find true background, then fill
interior transparent pixels back with black.
"""
from PIL import Image
import os
import sys
from collections import deque

def flood_fill_background(img):
    """Mark background pixels by flood-filling from edges."""
    w, h = img.size
    pixels = img.load()
    
    # Track which transparent pixels are reachable from edges
    is_background = [[False]*h for _ in range(w)]
    visited = [[False]*h for _ in range(w)]
    
    queue = deque()
    
    # Seed from all edge pixels that are transparent
    for x in range(w):
        for y in [0, h-1]:
            if pixels[x, y][3] == 0:
                queue.append((x, y))
                visited[x][y] = True
    for y in range(h):
        for x in [0, w-1]:
            if pixels[x, y][3] == 0 and not visited[x][y]:
                queue.append((x, y))
                visited[x][y] = True
    
    # BFS: spread to adjacent transparent pixels
    while queue:
        x, y = queue.popleft()
        is_background[x][y] = True
        
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                if pixels[nx, ny][3] == 0:
                    visited[nx][ny] = True
                    queue.append((nx, ny))
    
    return is_background

def fix_sprite(input_path, output_path):
    """Fix a single sprite: fill interior holes with black."""
    img = Image.open(input_path).convert('RGBA')
    w, h = img.size
    pixels = img.load()
    
    is_background = flood_fill_background(img)
    
    holes_filled = 0
    for x in range(w):
        for y in range(h):
            if pixels[x, y][3] == 0 and not is_background[x][y]:
                # Interior hole — fill with black
                pixels[x, y] = (0, 0, 0, 255)
                holes_filled += 1
    
    img.save(output_path)
    return holes_filled

def main():
    sprites_dir = "/home/yama/lobster-desktop-widget/assets/sprites"
    backup_dir = "/tmp/sprites-backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    total_fixed = 0
    for fname in sorted(os.listdir(sprites_dir)):
        if not fname.endswith('.png'):
            continue
        
        src = os.path.join(sprites_dir, fname)
        backup = os.path.join(backup_dir, fname)
        
        # Backup original
        img = Image.open(src)
        img.save(backup)
        
        # Fix
        holes = fix_sprite(src, src)
        total_fixed += holes
        status = f"  {holes} holes filled" if holes > 0 else "  OK (no holes)"
        print(f"{fname}: {status}")
    
    print(f"\nTotal: {total_fixed} holes filled across all sprites")
    print(f"Backups saved to: {backup_dir}/")

if __name__ == "__main__":
    main()
