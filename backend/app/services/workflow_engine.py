import yaml
import re
from typing import Dict, List, Any, Optional
from .openrouter_service import OpenRouterService

class WorkflowEngine:
    """工作流引擎 - 执行案例改编业务逻辑"""
    
    def __init__(self, openrouter_service: OpenRouterService):
        self.openrouter = openrouter_service
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """加载提示词模板"""
        return {
            'case_adaptation_with_materials': """角色：你是一位精通{knowledge_points}的专家，同时熟悉{case_scenario}情景，擅长做案例撰写和改编。

职责：请你基于场景{case_scenario}，结合知识点{knowledge_points}以及考核目标{learning_objectives}改编这个案例{case_materials}。

案例要求：

1. 背景与情境设置
提示：描述背景和案例的总体情境，包括公司信息、行业概况和主要挑战。背景要简洁但信息完整，能让学习者快速理解情境的关键因素。

2. 问题引导
提示：概述案例中的核心问题，并明确指出困扰该组织的决策或战略难题，保持中立的描述以鼓励学习者自主分析。

3. 关键数据与事实
提示：给出与问题分析和决策相关的关键数据和事实，例如公司财务状况、市场动态、运营瓶颈等，使内容具备逻辑支持。

4. 选择路径和解决方案
提示：列出多种可行的方案或行动路径，使学习者可以从多个角度进行对比分析，培养批判性思维。

5. 预期结果和影响

案例主题：结合改编的案例起一个吸引人的主题；

案例正文：包括案例背景、情境设定、核心问题、决策困境与挑战、行动计划与战略、战略决策、风险与反思以及结论。（不需要分条分点罗列，内容包括以上部分即可，要求逻辑清晰语言表述连贯，不要输出"背景与情景设置""问题引导""关键数据""这一案例展示了。。。"等无关案例的语言）""",

            'case_generation_from_search': """角色：你是一位精通{knowledge_points}的专家，同时熟悉{case_scenario}情景，擅长做案例撰写和改编。

职责：请你基于场景{case_scenario}，结合搜索到的{search_context}，知识内容{knowledge_points}以及考核目标{learning_objectives}改编一则相关性最高的案例。

案例要求：

1. 背景与情境设置
2. 问题引导
3. 关键数据与事实
4. 选择路径和解决方案
5. 预期结果和影响

案例主题：结合改编的案例起一个吸引人的主题；

案例正文：包括案例背景、情境设定、核心问题、决策困境与挑战、行动计划与战略、战略决策、风险与反思以及结论。（不需要分条分点罗列，内容包括以上部分即可，要求逻辑清晰语言表述连贯）""",

            'question_generation': """#角色说明：你是一个出题专家，帮助根据提供的案例设计{case_content}生成考试题目。请设计一组复杂的选择题，每道题目提供四个选项，其中至少两个选项具有较强的混淆性，避免明显的正确答案。题目内容涉及{knowledge_points}。题目应考察理解力、分析力和应用能力，通过具体情景描述来区分选项的合理性和误导性。

2. **生成要求（与学习目标一致）：**
   - 生成{question_type}所包含的题目类型，按照{question_type}顺序生成固定数量的题目。如"单选题 3 道 多选题 2 道 判断题 3 道"要求先生成3道单选题，再生成2道多选题，最后生成3道判断题，请严格按照要求输出的题目类型和数量生成。
   - 单选题、多选题每道题目应包含**四个选项**（A、B、C、D），并标明**正确答案**。
   - 多选题应该包含多个正确答案，答案呈现形式如"AB""ABC""ABCD"等
   - 判断题应包含"正确""错误"两个选项，并标明**正确答案**。
   - 每个题目后附带**答案解析**，明确解释正确答案并说明为什么其他选项不合适。
   
3. **题目要求（相关性与学习目标高度契合）：**
   - 确保每道题目与{knowledge_points}等知识点密切相关。
   - 题目内容必须能够帮助学生达到**学习目标**，并且支持**教学评估**。
   - 提问方式：生成围绕专业实施类知识的实际应用题目，而不仅仅是基于案例的分析题目。
   - 提问表述：题目题干都以陈述句的方式提出，例如"在选择外包方案时，XYZ制造公司应该优先考虑的因素是（）。"
   - 难度递进：所生成的题目，由简单到复杂，如第一题简单，逐渐增加难度。
   - 专业性：每道题都需要考察学生对专业领域（案例相关知识点{knowledge_points}）的实际理解，并能够应用于解决实际问题。
   - 防止简单复述：避免设计只需要学生重复案例内容的题目，确保问题具有一定的知识性挑战。
   - 实用性：题目应与实际操作密切相关，关注行业标准、技术应用、管理实践等内容。

4. **时限（可在课堂或课后测评时使用）：**

**输出格式：**
- 每道题目包含**四个选项**（A、B、C、D），并明确标注正确答案。
- 每个答案选项后附带**简洁明了的答案解释**。

**输出标准：**
- 确保题目针对{knowledge_points}的核心概念，并与学生的{learning_objectives}紧密对接。
- 提供**简明的答案解析**，帮助学生更好地理解每个选择的背景和原因。"""
        }
    
    def execute_workflow(self, workflow_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行完整的工作流程
        
        Args:
            workflow_input: 工作流输入参数
            
        Returns:
            工作流执行结果
        """
        result = {
            'success': False,
            'case_content': None,
            'questions': None,
            'total_tokens_used': 0,
            'steps_completed': []
        }
        
        try:
            # 步骤1: 判断是否有参考材料
            has_materials = bool(workflow_input.get('caseMaterials', '').strip())
            
            if has_materials:
                # 路径A: 基于材料改编案例
                case_result = self._adapt_case_with_materials(workflow_input)
            else:
                # 路径B: 无材料生成案例（这里简化处理，实际应该包含搜索步骤）
                case_result = self._generate_case_without_materials(workflow_input)
            
            if not case_result['success']:
                result['error'] = case_result.get('error', '案例生成失败')
                return result
            
            result['case_content'] = case_result['content']
            result['total_tokens_used'] += case_result.get('tokens_used', 0)
            result['steps_completed'].append('case_generation')
            
            # 步骤2: 判断是否生成题目
            if workflow_input.get('yes_or_no') == '是':
                questions_result = self._generate_questions(workflow_input, case_result['content'])
                
                if questions_result['success']:
                    result['questions'] = questions_result['content']
                    result['total_tokens_used'] += questions_result.get('tokens_used', 0)
                    result['steps_completed'].append('question_generation')
                    
                    # 步骤3: 根据难度等级优化题目
                    if workflow_input.get('difficultyLevel'):
                        optimization_result = self._optimize_questions_by_difficulty(
                            workflow_input, questions_result['content']
                        )
                        if optimization_result['success']:
                            result['questions'] = optimization_result['content']
                            result['total_tokens_used'] += optimization_result.get('tokens_used', 0)
                            result['steps_completed'].append('question_optimization')
            
            result['success'] = True
            return result
            
        except Exception as e:
            result['error'] = f'工作流执行异常: {str(e)}'
            return result
    
    def _adapt_case_with_materials(self, workflow_input: Dict[str, Any]) -> Dict[str, Any]:
        """基于参考材料改编案例"""
        try:
            # 构建提示词
            prompt = self.prompts['case_adaptation_with_materials'].format(
                knowledge_points=workflow_input['knowledgePoints'],
                case_scenario=workflow_input['caseScenario'],
                learning_objectives=workflow_input['learningObjectives'],
                case_materials=workflow_input['caseMaterials']
            )
            
            messages = [{"role": "system", "content": prompt}]
            
            # 调用AI API
            api_result = self.openrouter.chat_completion(
                messages=messages,
                model_name=workflow_input['model_name'],
                api_key=workflow_input['api_key'],
                user_uuid=workflow_input['user_uuid'],
                session_id=workflow_input['session_id'],
                request_type='案例改编',
                workflow_step='case_adaptation_with_materials'
            )
            
            print(f"DEBUG: API调用结果: {api_result}")  # 添加调试日志
            
            if api_result['success']:
                content = api_result['data']['choices'][0]['message']['content']
                tokens_used = api_result['data'].get('usage', {}).get('total_tokens', 0)
                
                return {
                    'success': True,
                    'content': content,
                    'tokens_used': tokens_used
                }
            else:
                return {
                    'success': False,
                    'error': api_result.get('error', 'API调用失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'案例改编失败: {str(e)}'
            }
    
    def _generate_case_without_materials(self, workflow_input: Dict[str, Any]) -> Dict[str, Any]:
        """无参考材料时生成案例"""
        try:
            # 这里应该包含搜索步骤，暂时简化处理
            search_context = f"基于{workflow_input['caseScenario']}场景和{workflow_input['knowledgePoints']}知识点的相关案例材料"
            
            prompt = self.prompts['case_generation_from_search'].format(
                knowledge_points=workflow_input['knowledgePoints'],
                case_scenario=workflow_input['caseScenario'],
                learning_objectives=workflow_input['learningObjectives'],
                search_context=search_context
            )
            
            messages = [{"role": "system", "content": prompt}]
            
            api_result = self.openrouter.chat_completion(
                messages=messages,
                model_name=workflow_input['model_name'],
                api_key=workflow_input['api_key'],
                user_uuid=workflow_input['user_uuid'],
                session_id=workflow_input['session_id'],
                request_type='案例生成',
                workflow_step='case_generation_from_search'
            )
            
            if api_result['success']:
                content = api_result['data']['choices'][0]['message']['content']
                tokens_used = api_result['data'].get('usage', {}).get('total_tokens', 0)
                
                return {
                    'success': True,
                    'content': content,
                    'tokens_used': tokens_used
                }
            else:
                return {
                    'success': False,
                    'error': api_result.get('error', 'API调用失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'案例生成失败: {str(e)}'
            }
    
    def _generate_questions(self, workflow_input: Dict[str, Any], case_content: str) -> Dict[str, Any]:
        """生成题目"""
        try:
            prompt = self.prompts['question_generation'].format(
                case_content=case_content,
                knowledge_points=workflow_input['knowledgePoints'],
                question_type=workflow_input['questionType'],
                learning_objectives=workflow_input['learningObjectives']
            )
            
            messages = [{"role": "system", "content": prompt}]
            
            api_result = self.openrouter.chat_completion(
                messages=messages,
                model_name=workflow_input['model_name'],
                api_key=workflow_input['api_key'],
                user_uuid=workflow_input['user_uuid'],
                session_id=workflow_input['session_id'],
                request_type='题目生成',
                workflow_step='question_generation'
            )
            
            if api_result['success']:
                content = api_result['data']['choices'][0]['message']['content']
                tokens_used = api_result['data'].get('usage', {}).get('total_tokens', 0)
                
                return {
                    'success': True,
                    'content': content,
                    'tokens_used': tokens_used
                }
            else:
                return {
                    'success': False,
                    'error': api_result.get('error', 'API调用失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'题目生成失败: {str(e)}'
            }
    
    def _optimize_questions_by_difficulty(self, workflow_input: Dict[str, Any], questions: str) -> Dict[str, Any]:
        """根据难度等级优化题目"""
        try:
            difficulty_level = workflow_input.get('difficultyLevel')
            
            if difficulty_level == '初级':
                optimization_prompt = f"{questions}\n\n题目太复杂了，请简化部分题目，降低题目难度，使其更适合初学者。保证题目类型和数量不变。"
            elif difficulty_level == '高级':
                optimization_prompt = f"{questions}\n\n题目太简单了，请替换部分题目，提升题目复杂度和难度，要求选项之间具有混淆度，不能是一眼就能看出答案的。保证题目类型和数量不变。"
            else:
                # 中级或无特殊要求，返回原题目
                return {
                    'success': True,
                    'content': questions,
                    'tokens_used': 0
                }
            
            messages = [{"role": "user", "content": optimization_prompt}]
            
            api_result = self.openrouter.chat_completion(
                messages=messages,
                model_name=workflow_input['model_name'],
                api_key=workflow_input['api_key'],
                user_uuid=workflow_input['user_uuid'],
                session_id=workflow_input['session_id'],
                request_type='题目优化',
                workflow_step=f'question_optimization_{difficulty_level}'
            )
            
            if api_result['success']:
                content = api_result['data']['choices'][0]['message']['content']
                tokens_used = api_result['data'].get('usage', {}).get('total_tokens', 0)
                
                return {
                    'success': True,
                    'content': content,
                    'tokens_used': tokens_used
                }
            else:
                # 如果优化失败，返回原题目
                return {
                    'success': True,
                    'content': questions,
                    'tokens_used': 0
                }
                
        except Exception as e:
            # 如果优化失败，返回原题目
            return {
                'success': True,
                'content': questions,
                'tokens_used': 0
            }
    
    def regenerate_case(self, data: Dict[str, Any], user) -> Dict[str, Any]:
        """重新生成案例"""
        # 这里可以实现重新生成的逻辑
        # 暂时返回占位符
        return {
            'content': '重新生成的案例内容',
            'tokens_used': 0
        }
    
    def regenerate_questions(self, data: Dict[str, Any], user) -> Dict[str, Any]:
        """重新生成题目"""
        # 这里可以实现重新生成的逻辑
        # 暂时返回占位符
        return {
            'content': '重新生成的题目内容',
            'tokens_used': 0
        } 