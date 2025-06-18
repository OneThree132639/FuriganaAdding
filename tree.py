import os

def print_directory_structure(start_path, prefix=''):
    """递归打印目录结构"""
    # 获取当前目录下的所有文件和文件夹（排除 .git、__pycache__ 等）
    try:
        entries = sorted(os.listdir(start_path))
    except PermissionError:
        print(f"{prefix}└── [无法访问]")
        return

    for i, entry in enumerate(entries):
        full_path = os.path.join(start_path, entry)
        is_last = (i == len(entries) - 1)

        if entry.startswith('.') or entry == '__pycache__':
            continue  # 忽略隐藏文件和 pycache

        # 打印当前条目
        if os.path.isdir(full_path):
            print(f"{prefix}{'└──' if is_last else '├──'} {entry}/")
            # 进入子目录
            new_prefix = prefix + ('    ' if is_last else '│   ')
            print_directory_structure(full_path, new_prefix)
        else:
            print(f"{prefix}{'└──' if is_last else '├──'} {entry}")
    

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_name = os.path.basename(current_dir)
    print(f"{project_name}/")
    print_directory_structure(current_dir, prefix='')