from typing import List, Dict

def build_tree(data: List[Dict]) -> List[Dict]:
    """
    将【包含id和pid且根节点id=0】的列表转换为树形结构(子节点放在children字段中)
    :param perms: 权限列表
    :return: 树形结构的权限列表
    """
    # 创建节点字典，便于快速查找
    node_dict = {node['id']: node for node in data}
    
    # 初始化树结构
    tree = []
    
    # 遍历所有节点，构建树结构
    for node in data:
        pid = node['pid']
        if pid == 0:
            # 根节点直接添加到树中
            tree.append(node)
        else:
            # 非根节点，找到父节点并添加到其children中
            parent = node_dict.get(pid)
            if parent:
                if 'children' not in parent:
                    parent['children'] = []
                parent['children'].append(node)
    
    # 对每个节点的子节点按sort排序
    def sort_children(node: Dict):
        if 'children' in node:
            node['children'].sort(key=lambda x: x.get('sort', 0))
            for child in node['children']:
                sort_children(child)
    
    for root in tree:
        sort_children(root)
    
    return tree