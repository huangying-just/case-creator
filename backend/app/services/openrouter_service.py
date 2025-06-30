import requests
import json
import time
from typing import Dict, List, Optional
from flask import current_app
from ..models import APIUsage
from .. import db

class OpenRouterService:
    """OpenRouter API集成服务"""
    
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = 30
        
        # 模型定价信息（每1000 tokens的价格，单位：美元）
        self.model_pricing = {
            'gpt-4o': {'input': 0.005, 'output': 0.015},
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'claude-3-opus': {'input': 0.015, 'output': 0.075},
            'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
            'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
            # 默认定价
            'default': {'input': 0.001, 'output': 0.002}
        }
    
    def get_default_api_key(self) -> Optional[str]:
        """获取默认API密钥"""
        return current_app.config.get('OPENROUTER_API_KEY')
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        return current_app.config.get('DEFAULT_MODEL', 'gpt-4o-mini')
    
    def chat_completion(self, messages: List[Dict], model_name: str = None, api_key: str = None, 
                       user_uuid: str = None, session_id: str = None, 
                       request_type: str = None, workflow_step: str = None, **kwargs) -> Dict:
        """
        调用OpenRouter聊天完成API
        
        Args:
            messages: 对话消息列表
            model_name: 模型名称（如果为空则使用默认模型）
            api_key: API密钥（如果为空则使用默认密钥）
            user_uuid: 用户UUID
            session_id: 会话ID
            request_type: 请求类型
            workflow_step: 工作流步骤
            **kwargs: 其他参数
        
        Returns:
            API响应结果
        """
        # 使用默认值填充缺失参数
        api_key = api_key or self.get_default_api_key()
        model_name = model_name or self.get_default_model()
        
        if not api_key:
            return {
                'success': False,
                'error': 'API密钥未设置，请在环境变量或用户设置中配置OpenRouter API密钥'
            }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
            "HTTP-Referer": "https://case-creator.local",
            "X-Title": "Case Creator Expert"  # 使用英文避免编码问题
        }
        
        # 准备请求数据
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 2000),
            "top_p": kwargs.get('top_p', 1.0),
            "frequency_penalty": kwargs.get('frequency_penalty', 0),
            "presence_penalty": kwargs.get('presence_penalty', 0)
        }
        
        # 如果有系统提示，可以添加stream选项
        if kwargs.get('stream', False):
            payload['stream'] = True
        
        try:
            start_time = time.time()
            
            # 发送请求，显式处理UTF-8编码
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                timeout=self.timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                
                # 记录API使用情况
                if user_uuid:
                    self._log_api_usage(
                        user_uuid=user_uuid,
                        model_name=model_name,
                        response=result,
                        session_id=session_id,
                        request_type=request_type,
                        workflow_step=workflow_step,
                        response_time=response_time
                    )
                
                return {
                    'success': True,
                    'data': result,
                    'response_time': response_time
                }
            else:
                error_message = f"API请求失败: {response.status_code} - {response.text}"
                return {
                    'success': False,
                    'error': error_message,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'API请求超时，请稍后重试'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': '网络连接错误，请检查网络连接'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'API调用异常: {str(e)}'
            }
    
    def _log_api_usage(self, user_uuid: str, model_name: str, response: Dict,
                      session_id: str = None, request_type: str = None,
                      workflow_step: str = None, response_time: float = None):
        """记录API使用统计"""
        try:
            # 提取token使用信息
            usage = response.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
            
            # 计算成本
            cost = self._calculate_cost(model_name, prompt_tokens, completion_tokens)
            
            # 创建使用记录
            api_usage = APIUsage(
                user_uuid=user_uuid,
                model_name=model_name,
                tokens_used=total_tokens,
                cost=cost,
                request_type=request_type,
                workflow_step=workflow_step,
                session_id=session_id
            )
            
            db.session.add(api_usage)
            db.session.commit()
            
        except Exception as e:
            # 记录日志失败不应该影响主要功能
            print(f"记录API使用情况失败: {str(e)}")
            db.session.rollback()
    
    def _calculate_cost(self, model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
        """计算API调用成本"""
        # 获取模型定价，如果没有则使用默认定价
        pricing = self.model_pricing.get(model_name, self.model_pricing['default'])
        
        # 计算成本（价格是每1000个token）
        input_cost = (prompt_tokens / 1000) * pricing['input']
        output_cost = (completion_tokens / 1000) * pricing['output']
        
        return round(input_cost + output_cost, 6)
    
    def get_available_models(self) -> List[Dict]:
        """获取可用模型列表"""
        return [
            {
                'id': 'gpt-4o',
                'name': 'GPT-4o',
                'provider': 'OpenAI',
                'description': '最新的GPT-4模型，性能优异',
                'pricing': self.model_pricing.get('gpt-4o')
            },
            {
                'id': 'gpt-4o-mini',
                'name': 'GPT-4o Mini',
                'provider': 'OpenAI',
                'description': '轻量级GPT-4模型，成本较低',
                'pricing': self.model_pricing.get('gpt-4o-mini')
            },
            {
                'id': 'claude-3-opus',
                'name': 'Claude 3 Opus',
                'provider': 'Anthropic',
                'description': '最强大的Claude模型',
                'pricing': self.model_pricing.get('claude-3-opus')
            },
            {
                'id': 'claude-3-sonnet',
                'name': 'Claude 3 Sonnet',
                'provider': 'Anthropic',
                'description': '平衡性能和成本的Claude模型',
                'pricing': self.model_pricing.get('claude-3-sonnet')
            },
            {
                'id': 'claude-3-haiku',
                'name': 'Claude 3 Haiku',
                'provider': 'Anthropic',
                'description': '快速且经济的Claude模型',
                'pricing': self.model_pricing.get('claude-3-haiku')
            }
        ]
    
    def validate_api_key(self, api_key: str = None) -> Dict:
        """验证API密钥有效性"""
        api_key = api_key or self.get_default_api_key()
        
        if not api_key:
            return {'valid': False, 'message': 'API密钥未设置'}
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 发送简单的测试请求
        test_payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 1
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'valid': True, 'message': 'API密钥有效'}
            elif response.status_code == 401:
                return {'valid': False, 'message': 'API密钥无效或已过期'}
            else:
                return {'valid': False, 'message': f'验证失败: {response.status_code}'}
                
        except Exception as e:
            return {'valid': False, 'message': f'验证异常: {str(e)}'}
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """获取模型信息"""
        models = self.get_available_models()
        for model in models:
            if model['id'] == model_name:
                return model
        return None 