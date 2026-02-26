
import os
import shutil
import glob


def clean_pytest_cache(root_dir=None):
    if root_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("开始清理目录: " + root_dir)
    print("=" * 60)
    
    patterns = [
        os.path.join(root_dir, "pytest-cache-files-*"),
        os.path.join(root_dir, "**", "__pycache__"),
        os.path.join(root_dir, ".pytest_cache"),
        os.path.join(root_dir, "**", ".pytest_cache"),
    ]
    
    deleted_count = 0
    deleted_size = 0
    
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            if os.path.exists(path):
                try:
                    if os.path.isfile(path):
                        size = os.path.getsize(path)
                    else:
                        size = 0
                        for dirpath, dirnames, filenames in os.walk(path):
                            for filename in filenames:
                                filepath = os.path.join(dirpath, filename)
                                if os.path.exists(filepath):
                                    size += os.path.getsize(filepath)
                    
                    if os.path.isfile(path):
                        os.remove(path)
                        print("[删除文件] " + path)
                    else:
                        shutil.rmtree(path)
                        print("[删除目录] " + path)
                    
                    deleted_count += 1
                    deleted_size += size
                    
                except Exception as e:
                    print("[删除失败] " + path + ": " + str(e))
    
    print("=" * 60)
    print("清理完成！共删除 " + str(deleted_count) + " 个文件/目录")
    
    if deleted_size < 1024:
        size_str = str(deleted_size) + " B"
    elif deleted_size < 1024 * 1024:
        size_str = "{:.2f} KB".format(deleted_size / 1024)
    elif deleted_size < 1024 * 1024 * 1024:
        size_str = "{:.2f} MB".format(deleted_size / (1024 * 1024))
    else:
        size_str = "{:.2f} GB".format(deleted_size / (1024 * 1024 * 1024))
    
    print("释放空间: " + size_str)
    return deleted_count, deleted_size


if __name__ == "__main__":
    clean_pytest_cache()

