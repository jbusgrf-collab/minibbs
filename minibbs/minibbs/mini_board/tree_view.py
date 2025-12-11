import os

def print_directory_tree(start_path='.'):
    for root, dirs, files in os.walk(start_path):
        # 階層レベルの計算
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f'{indent}{os.path.basename(root)}/')
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{sub_indent}{f}')

print_directory_tree()
