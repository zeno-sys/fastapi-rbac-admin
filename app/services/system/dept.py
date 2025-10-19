from typing import Dict, List, Optional
from sqlmodel import select
from app.core.db import AsyncSession
from app.core.logger import LoggerDep
from app.models.system import DeptModel
from app.utils.tree import build_tree
from app.core.system_context import SystemContext

class DeptService:
    def __init__(self, session: AsyncSession, logger: LoggerDep) -> None:
        self.session = session
        self.logger = logger

    async def lists(self) -> List[DeptModel]:
        """获取所有部门"""
        sql = select(DeptModel)
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_dept_by_id(self, dept_id: int) -> DeptModel | None:
        """根据ID获取部门"""
        sql = select(DeptModel).where(DeptModel.id == dept_id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def create_dept(self, dept: DeptModel) -> DeptModel:
        """创建部门"""
        # 设置租户ID
        tenant_id = SystemContext.get_tenant_id()
        if tenant_id:
            dept.tenant_id = tenant_id
        
        self.session.add(dept)
        await self.session.commit()
        await self.session.refresh(dept)
        return dept

    async def update_dept(self, dept_data: dict) -> DeptModel | None:
        """更新部门"""
        dept_id = dept_data.pop("id")
        dept = await self.get_dept_by_id(dept_id)
        if not dept:
            return None
            
        for key, value in dept_data.items():
            setattr(dept, key, value)
            
        await self.session.commit()
        await self.session.refresh(dept)
        return dept

    async def delete_dept(self, dept_id: int) -> bool:
        """逻辑删除部门"""
        dept = await self.get_dept_by_id(dept_id)
        if not dept:
            return False
            
        # 设置逻辑删除标志
        dept.deleted = 1
        await self.session.commit()
        return True

    async def get_dept_tree(self, dept_id: int = None) -> List[dict]:
        """获取部门树结构
        :param dept_id: 部门ID，如果为None则返回完整树结构
        """
        sql = select(DeptModel)
        result = await self.session.execute(sql)
        depts = result.scalars().all()
        
        depts_dict = [dept.model_dump() for dept in depts]
        
        if dept_id is not None:
            # 如果是查询子树，则先构建完整树，然后找到指定节点
            full_tree = build_tree(depts_dict)
            subtree = find_subtree(full_tree, dept_id)
            return [subtree] if subtree else []
        else:
            # 否则返回完整树结构
            return build_tree(depts_dict)

    async def import_depts_from_json(self, dept_data: List[dict]) -> dict:
        """从JSON数据批量导入部门
        :param dept_data: 部门数据列表
        :return: 导入结果统计
        """
        success_count = 0
        error_count = 0
        errors = []
        
        # 先删除remark字段包含"从钉钉导入"字符串的数据
        try:
            from sqlmodel import delete
            delete_sql = delete(DeptModel).where(DeptModel.remark.like("%从钉钉导入%"))
            await self.session.execute(delete_sql)
            await self.session.commit()
            self.logger.info("已删除之前从钉钉导入的部门数据")
        except Exception as e:
            self.logger.error(f"删除之前从钉钉导入的部门数据失败: {str(e)}")
            error_count += 1
            errors.append(f"删除之前从钉钉导入的部门数据失败: {str(e)}")
        
        # 创建ID映射字典，用于处理parentid到pid的转换
        id_mapping = {}
        
        # 先创建所有部门，使用钉钉的部门ID作为数据库主键
        for dept_info in dept_data:
            try:
                # 提取JSON中的部门信息
                dept_id = dept_info.get('id')
                name = dept_info.get('name')
                parentid = dept_info.get('parentid')
                
                if not name or not dept_id:
                    error_count += 1
                    errors.append(f"部门ID {dept_id}: 缺少部门名称或ID")
                    continue
                
                # 特殊处理：当部门名称为"拓尔思天行网安信息技术有限责任公司"时，ID设置为99999
                if name == "拓尔思天行网安信息技术有限责任公司":
                    final_dept_id = 99999
                else:
                    final_dept_id = dept_id
                
                # 创建部门模型，使用处理后的部门ID
                dept_model = DeptModel(
                    id=final_dept_id,
                    name=name,
                    remark=f"从钉钉导入 - 原ID: {dept_id}",
                    pid=None,  # 先设为None，后续更新
                    level=1,   # 默认层级，后续会根据父级调整
                    sort=0,
                    status=0
                )
                
                self.session.add(dept_model)
                await self.session.flush()  # 刷新以获取生成的ID
                
                # 记录ID映射关系（钉钉ID -> 最终数据库ID）
                id_mapping[dept_id] = final_dept_id
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"部门ID {dept_info.get('id', 'unknown')}: {str(e)}")
        
        # 提交第一轮创建
        await self.session.commit()
        
        # 第二轮：更新父级关系和层级
        for dept_info in dept_data:
            try:
                dept_id = dept_info.get('id')
                parentid = dept_info.get('parentid')
                
                if dept_id in id_mapping:
                    # 查询部门
                    sql = select(DeptModel).where(DeptModel.id == dept_id)
                    result = await self.session.execute(sql)
                    dept = result.scalar_one_or_none()
                    
                    if dept:
                        # 特殊处理：当部门名称为"拓尔思天行网安信息技术有限责任公司"时，pid设置为0
                        if dept.name == "拓尔思天行网安信息技术有限责任公司":
                            dept.pid = 0
                            dept.level = 1
                        elif parentid and parentid in id_mapping:
                            # 有父级部门，使用映射后的父级ID
                            dept.pid = id_mapping[parentid]
                            # 计算层级：父级层级 + 1
                            parent_sql = select(DeptModel).where(DeptModel.id == id_mapping[parentid])
                            parent_result = await self.session.execute(parent_sql)
                            parent_dept = parent_result.scalar_one_or_none()
                            if parent_dept:
                                dept.level = (parent_dept.level or 1) + 1
                            else:
                                dept.level = 2
                        else:
                            # 顶级部门
                            dept.level = 1
                        
            except Exception as e:
                error_count += 1
                errors.append(f"更新父级关系失败 - 部门ID {dept_info.get('id', 'unknown')}: {str(e)}")
        
        # 提交第二轮更新
        await self.session.commit()
        
        # 第三轮：获取并设置部门负责人
        await self._set_dept_leaders(dept_data, id_mapping, errors)
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }
    
    async def _set_dept_leaders(self, dept_data: List[dict], id_mapping: dict, errors: list) -> None:
        """设置部门负责人
        :param dept_data: 部门数据列表
        :param id_mapping: ID映射字典
        :param errors: 错误列表
        """
        try:
            from app.services.dingtalk import DingTalkService
            from app.core.logger import LoggerDep
            
            # 创建钉钉服务实例
            dingtalk_service = DingTalkService(self.logger)
            
            for dept_info in dept_data:
                try:
                    dept_id = dept_info.get('id')
                    if dept_id not in id_mapping:
                        continue
                    
                    # 现在id_mapping中存储的就是钉钉的部门ID，直接使用
                    db_dept_id = id_mapping[dept_id]
                    
                    # 获取部门下的用户列表
                    user_ids = await dingtalk_service.get_department_user_ids(dept_id)
                    
                    if not user_ids:
                        self.logger.info(f"部门 {dept_info.get('name')} 没有用户")
                        continue
                    
                    # 获取部门负责人（优先选择管理员或部门主管）
                    leader_name = None
                    for user_id in user_ids:
                        try:
                            user_detail = await dingtalk_service.get_user_detail(user_id)
                            user_name = user_detail.get('name')
                            is_admin = user_detail.get('is_admin', False)
                            is_boss = user_detail.get('is_boss', False)
                            
                            # 优先选择管理员或部门主管
                            if is_admin or is_boss:
                                leader_name = user_name
                                self.logger.info(f"找到部门管理员/主管: {leader_name}")
                                break
                            elif not leader_name:  # 如果没有找到管理员，选择第一个用户
                                leader_name = user_name
                                
                        except Exception as e:
                            self.logger.warning(f"获取用户 {user_id} 详细信息失败: {str(e)}")
                            continue
                    
                    if leader_name:
                        # 更新部门的leader字段
                        sql = select(DeptModel).where(DeptModel.id == db_dept_id)
                        result = await self.session.execute(sql)
                        dept = result.scalar_one_or_none()
                        
                        if dept:
                            dept.leader = leader_name
                            self.logger.info(f"设置部门 {dept.name} 的负责人为: {leader_name}")
                    
                except Exception as e:
                    error_msg = f"设置部门负责人失败 - 部门ID {dept_info.get('id', 'unknown')}: {str(e)}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
            
            # 提交负责人更新
            await self.session.commit()
            self.logger.info("部门负责人设置完成")
            
        except Exception as e:
            error_msg = f"设置部门负责人异常: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        
def find_subtree(tree: List[Dict], dept_id: int) -> Optional[Dict]:
    """
    在树中查找指定部门ID的子树
    :param tree: 部门树
    :param dept_id: 要查找的部门ID
    :return: 找到的子树节点，如果没找到返回None
    """
    for node in tree:
        if node['id'] == dept_id:
            return node
        if 'children' in node:
            found = find_subtree(node['children'], dept_id)
            if found:
                return found
    return None