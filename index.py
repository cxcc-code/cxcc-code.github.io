import os
import re

# 将配置文件转换为数组
def prase_cfg(filename):
    dir_map=[]
    with open(filename,"r",encoding='utf-8') as file:
        for line in file:
            line = line.split('#')[0]
            if line=='' or line=='\n':
                continue
            line = line.expandtabs(4)
            cur_deep = len(line) - len(line.lstrip())
            dir_map.append([
                cur_deep,
                line.split(': ')[0].lstrip(),
                line.split(': ')[1].replace('\n','')
            ])
    return dir_map

# 根据路径查找配置
def find_cfg(dir_map,path:str,split='.',root=-1):
    if root == -1:
        min = -1
    else:
        min = dir_map[root][0]
    
    path_part = path.split(split)
    for part in path_part:
        rst = -1
        for i in range(root+1,len(dir_map)):
            if dir_map[i][0] <= min:
                break
            elif rst==-1 or dir_map[i][0] < dir_map[rst][0]:
                rst = i
        if rst==-1:
            return -1
        target_deep = dir_map[rst][0]
        flag = 0
        for i in range(root+1,len(dir_map)):
            if dir_map[i][0] != target_deep:
                continue
            if dir_map[i][1] == part:
                root = i
                min = dir_map[root][0]
                flag = 1
                break
        if flag != 1:
            return -1
    return i

# 按照目录生成index.md的主要文本
def generate_index_md(directory, dir_map,depth=0,ref_dir=None):
    if ref_dir == None:
        ref_dir = directory
    index_content = ""
    for item in sorted(os.listdir(directory)):
        if item.endswith('.md') and  item != "index.md":
            with open(os.path.join(directory, item), 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    title = first_line[2:]
                else:
                    title = item[:-3]
            link = os.path.join(directory, item).replace(" ", "%20")
            link = os.path.relpath(link,ref_dir)
            link = link.split('.md')[0]
            link = link.replace("\\", "/")
            index_content += f"{'  ' * depth}- [{title}]({link})\n"
        elif os.path.isdir(os.path.join(directory, item)) and ( not item.endswith('.assets')):
            subdir_path = os.path.join(directory, item)
            dir_map_index = find_cfg(dir_map,subdir_path,split='\\')
            if dir_map_index != -1:
                dir_value = dir_map[dir_map_index][2]
            else:
                dir_value = item
                print(f"<{subdir_path}> can't find in cfg file")
            link = subdir_path.replace(" ", "%20")
            link = os.path.relpath(link,ref_dir)
            link = link.replace("\\", "/")
            index_content += f"{'  ' * depth}- [{dir_value}]({link})\n"
            index_content += generate_index_md(subdir_path, dir_map, depth + 1,ref_dir=ref_dir)
    return index_content

# 将生成的文本带上文件标题写入到文件中
def generate_indexes(directory,dir_map,ref_dir=None):
    if ref_dir == None:
        ref_dir = directory
    index_content = generate_index_md(directory,dir_map,ref_dir=ref_dir)
    with open(os.path.join(directory, 'index.md'), 'w', encoding='utf-8') as f:
        dir_map_index = find_cfg(dir_map,directory,split='\\')
        if dir_map_index != -1:
            dir_value = dir_map[dir_map_index][2]
        else:
            dir_value = directory.split('\\')[-1]
            print(f"<{directory}> can't find in cfg file")
        f.write(f"# {dir_value}\n\n")
        f.write(index_content)

# 递归的生成index.md
def generate_indexes_r(directory,dir_map):
    generate_indexes(directory,dir_map)
    for item in sorted(os.listdir(directory)):
        sub_item = os.path.join(directory, item)
        if os.path.isdir(sub_item) and ( not item.endswith('.assets')):
            generate_indexes_r(sub_item,dir_map)

def convert_md_to_html(dir_path):
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.md'):
                md_file_path = os.path.join(root, file)
                with open(md_file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                # 使用正则表达式匹配图片引用的 Markdown 语法 ![alt text](url)
                # 将其替换为对应的 HTML 语法 <img src="url" alt="alt text">
                html_content = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', md_content)

                # 将替换后的内容写回原文件
                with open(md_file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                print(f"Converted images in {md_file_path}")

# Example usage:
root_directory = "docs"
config_file = "dir_map.cfg"
dir_map = prase_cfg(config_file)
generate_indexes_r(root_directory,dir_map)
convert_md_to_html(root_directory)
