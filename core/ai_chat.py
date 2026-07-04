# core/ai_chat.py
import json
import requests
from django.db.models import Count, Avg
from .models import Student, DisciplineReport, Stream

class PollinationAIChat:
    """REAL AI Chat integration with Pollination API"""
    
    def __init__(self):
        # ✅ CORRECT CONFIGURATION
        self.api_key = "sk_0V0dkm2fnpoFAqgW5W6MXjACtqD2yIPK"
        self.api_url = "https://gen.pollinations.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_system_prompt(self, student_context=None):
        """Get the system prompt for the AI"""
        base_prompt = """You are an AI Education Assistant specialized in Kenyan education law and school discipline management. You have REAL-TIME access to the school's database.

IMPORTANT RULES:
1. Use your AI knowledge to answer questions intelligently and conversationally
2. When asked about students, fetch their data from the database and analyze it
3. Provide concise, helpful, and natural responses
4. Reference Kenyan laws accurately (Basic Education Act 2013, Children's Act 2001)
5. Be conversational and friendly - like a helpful teacher or advisor
6. If you don't know something, say so honestly
7. Remember the conversation context and refer back to previous topics

Your capabilities:
1. Answer questions about Kenyan Education Law
2. Analyze student behavior and risk from database data
3. Suggest interventions based on real data
4. Provide discipline guidance
5. Reference Kenyan law sections accurately

Key Laws:
- Basic Education Act 2013 (Sections 30, 36, 37)
- Children's Act 2001
- Positive Discipline Guidelines

Be helpful, professional, and use your AI knowledge to provide thoughtful, natural responses."""
        
        if student_context:
            return base_prompt + f"\n\nCurrent Student Data from Database:\n{json.dumps(student_context, indent=2)}"
        
        return base_prompt
    
    def get_student_data(self, student_id):
        """Fetch REAL student data from database"""
        try:
            student = Student.objects.get(id=student_id, is_active=True)
            reports = student.reports.select_related('category').order_by('-reported_at')
            
            data = {
                'name': student.name,
                'admission': student.admission_number,
                'stream': student.stream.name if student.stream else 'N/A',
                'form': student.form,
                'risk_score': student.risk_score,
                'risk_level': student.risk_level,
                'total_reports': reports.count(),
                'recent_reports': []
            }
            
            for report in reports[:5]:
                data['recent_reports'].append({
                    'date': report.reported_at.strftime('%Y-%m-%d %H:%M'),
                    'category': report.category.name,
                    'rating': report.get_rating_display(),
                    'points': report.points
                })
            
            return data
        except Student.DoesNotExist:
            return None
    
    def chat(self, user_message, student_id=None, conversation_history=None):
        """Send message to REAL AI and get intelligent response"""
        
        # Get student data if available
        student_data = None
        if student_id:
            student_data = self.get_student_data(student_id)
        
        # Build messages for AI
        messages = [
            {"role": "system", "content": self.get_system_prompt(student_data)}
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append(msg)
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Call Pollination API - ✅ Using correct model
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "gpt-3.5-turbo",  # ✅ Changed from "gpt-4"
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500
                },
                timeout=45
            )
            
            print(f"🔵 API Response Status: {response.status_code}")
            print(f"🔵 API Response: {response.text[:200] if response.text else 'Empty'}")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data['choices'][0]['message']['content'],
                    'usage': data.get('usage', {})
                }
            else:
                # If 400 with invalid model, try with different model
                if response.status_code == 400 and "Invalid model" in response.text:
                    try:
                        # Try with "openai" model
                        response2 = requests.post(
                            self.api_url,
                            headers=self.headers,
                            json={
                                "model": "openai",  # Alternative model
                                "messages": messages,
                                "temperature": 0.7,
                                "max_tokens": 1500
                            },
                            timeout=45
                        )
                        if response2.status_code == 200:
                            data = response2.json()
                            return {
                                'success': True,
                                'response': data['choices'][0]['message']['content'],
                                'usage': data.get('usage', {})
                            }
                    except:
                        pass
                
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text[:200] if response.text else 'No response'}"
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "The AI is taking too long to respond. Please try again."
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': "Cannot connect to AI service. Please check your internet connection."
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }