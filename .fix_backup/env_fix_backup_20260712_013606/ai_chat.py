# core/ai_chat.py
import json
import os
import re
import requests
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from .models import (
    Student, DisciplineReport, DisciplineCategory, 
    Stream, TeacherProfile, School, GradeLevel
)


class PollinationAIChat:
    """Enhanced AI Chat with full database integration"""
    
    def __init__(self):
        self.api_key = os.environ.get("POLLINATION_API_KEY", "")
        self.api_url = "https://gen.pollinations.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.primary_model = "openai"
        self.fallback_model = "mistral"
        self.backup_models = ["llama", "gpt-4"]
        
        # Cache for frequently accessed data
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = 300  # 5 minutes
    
    def _get_cached(self, key):
        """Get cached data if valid"""
        if key in self._cache and key in self._cache_time:
            if (timezone.now() - self._cache_time[key]).seconds < self._cache_duration:
                return self._cache[key]
        return None
    
    def _set_cache(self, key, value):
        """Set cached data"""
        self._cache[key] = value
        self._cache_time[key] = timezone.now()
    
    def get_system_prompt(self, context=None):
        """Get enhanced system prompt with context"""
        base_prompt = """You are an AI Education Assistant with FULL ACCESS to the school's discipline management system database. You can query ANY data about students, reports, teachers, streams, and school statistics.

CAPABILITIES:
1. Query student records by name, admission number, stream, or form
2. Retrieve discipline reports with dates, categories, and ratings
3. Generate school-wide statistics and analytics
4. Provide personalized student recommendations
5. Answer questions about Kenyan Education Law
6. Analyze trends and patterns in student behavior
7. Compare students, streams, and classes
8. Track intervention effectiveness

RESPONSE FORMAT:
- Be conversational and helpful
- Use bullet points for lists
- Bold important information
- Provide specific numbers and dates when available
- If data is not found, suggest alternatives

PERSONALITY:
- Professional but friendly
- Proactive in offering help
- Clear and concise
- Confident but not arrogant

ACCESSIBLE DATA:
- All students (name, admission, stream, form, risk score)
- All discipline reports (date, category, rating, points)
- Teacher profiles and assignments
- School statistics (totals, averages, distributions)
- Academic terms and streams
- Category breakdowns and trends

RESPONSE GUIDELINES:
1. Always confirm what you found
2. If multiple matches, list them
3. Offer to drill down deeper
4. Suggest related information they might need
5. Reference Kenyan laws when relevant

You are the ultimate assistant for this school's discipline management - use your database access to provide comprehensive, accurate, and helpful responses."""

        if context:
            return base_prompt + f"\n\nCURRENT CONTEXT:\n{json.dumps(context, indent=2)}"
        
        return base_prompt
    
    def get_student_data(self, student_id=None, name=None, admission=None):
        """Fetch detailed student data from database"""
        try:
            if student_id:
                student = Student.objects.get(id=student_id, is_active=True)
            elif admission:
                student = Student.objects.get(admission_number=admission, is_active=True)
            elif name:
                # Try exact match first, then partial
                student = Student.objects.filter(name__iexact=name, is_active=True).first()
                if not student:
                    student = Student.objects.filter(name__icontains=name, is_active=True).first()
            else:
                return None
            
            if not student:
                return None
            
            # Get reports
            reports = student.reports.select_related('category', 'reported_by').order_by('-reported_at')
            total_reports = reports.count()
            
            # Category breakdown
            category_breakdown = list(
                reports.values('category__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # Get class teacher
            class_teacher = None
            if student.stream:
                teacher_profile = TeacherProfile.objects.filter(
                    assigned_stream=student.stream,
                    assigned_form=student.form,
                    is_approved=True
                ).first()
                if teacher_profile:
                    class_teacher = {
                        'name': teacher_profile.user.get_full_name() or teacher_profile.user.username,
                        'email': teacher_profile.user.email,
                        'phone': teacher_profile.phone_number,
                    }
            
            # Recent reports with details
            recent_reports = []
            for report in reports[:10]:
                recent_reports.append({
                    'date': report.reported_at.strftime('%Y-%m-%d %H:%M'),
                    'category': report.category.name,
                    'rating': report.get_rating_display(),
                    'points': report.points,
                    'reported_by': report.reported_by.get_full_name() or report.reported_by.username,
                    'comments': report.comments[:100] + '...' if len(report.comments) > 100 else report.comments,
                })
            
            # Calculate days since last incident
            days_since = None
            if student.last_incident_date:
                delta = timezone.now() - student.last_incident_date
                days_since = delta.days
            
            data = {
                'id': student.id,
                'name': student.name,
                'admission_number': student.admission_number,
                'stream': student.stream.name if student.stream else 'Not Assigned',
                'form': student.form,
                'year': student.year,
                'risk_score': student.risk_score,
                'risk_level': student.risk_level,
                'total_reports': total_reports,
                'intervention_count': student.intervention_count,
                'days_since_last_incident': days_since,
                'is_active': student.is_active,
                'created_at': student.created_at.strftime('%Y-%m-%d'),
                'class_teacher': class_teacher,
                'category_breakdown': category_breakdown,
                'recent_reports': recent_reports,
                'optional_notes': student.optional_notes,
            }
            
            # Cache the data
            self._set_cache(f'student_{student.id}', data)
            
            return data
            
        except Student.DoesNotExist:
            return None
        except Exception as e:
            return {'error': str(e)}
    
    def get_school_stats(self):
        """Get comprehensive school statistics"""
        cache_key = 'school_stats'
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            students = Student.objects.filter(is_active=True)
            total_students = students.count()
            
            # Risk distribution
            critical = students.filter(risk_level='CRITICAL').count()
            warning = students.filter(risk_level='WARNING').count()
            good = students.filter(risk_level='GOOD').count()
            
            # Stream breakdown
            stream_stats = {}
            for stream in Stream.objects.filter(is_active=True):
                count = students.filter(stream=stream).count()
                if count > 0:
                    stream_stats[stream.name] = count
            
            # Form breakdown
            form_stats = {}
            for form in Student.FORM_CHOICES:
                form_name = form[0]
                count = students.filter(form=form_name).count()
                if count > 0:
                    form_stats[form_name] = count
            
            # Report statistics
            total_reports = DisciplineReport.objects.count()
            reports_today = DisciplineReport.objects.filter(
                reported_at__date=timezone.now().date()
            ).count()
            reports_this_week = DisciplineReport.objects.filter(
                reported_at__week=timezone.now().isocalendar()[1]
            ).count()
            
            # Top categories
            top_categories = list(
                DisciplineReport.objects.values('category__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            )
            
            # Online teachers
            online_teachers = TeacherProfile.objects.filter(is_online=True).count()
            total_teachers = TeacherProfile.objects.filter(is_approved=True).count()
            
            # Average risk
            avg_risk = students.aggregate(avg=Avg('risk_score'))['avg'] or 0
            
            stats = {
                'total_students': total_students,
                'critical_count': critical,
                'warning_count': warning,
                'good_count': good,
                'avg_risk_score': round(avg_risk, 1),
                'total_reports': total_reports,
                'reports_today': reports_today,
                'reports_this_week': reports_this_week,
                'online_teachers': online_teachers,
                'total_teachers': total_teachers,
                'top_categories': top_categories,
                'stream_breakdown': stream_stats,
                'form_breakdown': form_stats,
                'timestamp': timezone.now().isoformat(),
            }
            
            self._set_cache(cache_key, stats)
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def search_students(self, query):
        """Search for students by name or admission number"""
        cache_key = f'search_{query}'
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            results = []
            
            # Search by admission number
            if query.isdigit():
                students = Student.objects.filter(
                    admission_number__icontains=query,
                    is_active=True
                )[:5]
            else:
                # Search by name
                students = Student.objects.filter(
                    Q(name__icontains=query) | Q(name__istartswith=query),
                    is_active=True
                )[:10]
            
            for student in students:
                results.append({
                    'id': student.id,
                    'name': student.name,
                    'admission_number': student.admission_number,
                    'stream': student.stream.name if student.stream else 'N/A',
                    'form': student.form,
                    'risk_score': student.risk_score,
                    'risk_level': student.risk_level,
                    'total_reports': student.reports.count(),
                })
            
            self._set_cache(cache_key, results)
            return results
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_stream_analysis(self, stream_id):
        """Get detailed analysis for a specific stream"""
        try:
            stream = Stream.objects.get(id=stream_id, is_active=True)
            students = Student.objects.filter(stream=stream, is_active=True)
            
            total = students.count()
            if total == 0:
                return {
                    'stream': stream.name,
                    'message': 'No students in this stream',
                }
            
            critical = students.filter(risk_level='CRITICAL').count()
            warning = students.filter(risk_level='WARNING').count()
            good = students.filter(risk_level='GOOD').count()
            avg_risk = students.aggregate(avg=Avg('risk_score'))['avg'] or 0
            
            # Top offenders
            top_offenders = list(
                students.annotate(report_count=Count('reports'))
                .filter(report_count__gt=0)
                .order_by('-report_count')[:5]
                .values('name', 'admission_number', 'report_count', 'risk_score')
            )
            
            return {
                'stream': stream.name,
                'total_students': total,
                'critical_count': critical,
                'warning_count': warning,
                'good_count': good,
                'average_risk': round(avg_risk, 1),
                'top_offenders': top_offenders,
            }
            
        except Stream.DoesNotExist:
            return {'error': 'Stream not found'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_all_students_summary(self):
        """Get summary of all students with basic info"""
        cache_key = 'all_students_summary'
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            students = Student.objects.filter(is_active=True).select_related('stream')
            summary = []
            
            for student in students[:50]:  # Limit to 50 for performance
                summary.append({
                    'id': student.id,
                    'name': student.name,
                    'admission': student.admission_number,
                    'stream': student.stream.name if student.stream else 'N/A',
                    'form': student.form,
                    'risk': student.risk_score,
                    'level': student.risk_level,
                    'reports': student.reports.count(),
                })
            
            self._set_cache(cache_key, summary)
            return summary
            
        except Exception as e:
            return {'error': str(e)}
    
    def _try_model(self, messages, model_name):
        """Try sending a request with a specific model"""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500
                },
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data['choices'][0]['message']['content'],
                    'usage': data.get('usage', {}),
                    'model_used': model_name
                }
            elif response.status_code == 400 and "Invalid model" in response.text:
                return {
                    'success': False,
                    'error': f"Model '{model_name}' is invalid",
                    'invalid_model': True
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error ({model_name}): {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_user_intent(self, message):
        """Parse user message to understand intent and extract entities"""
        message_lower = message.lower()
        
        intent = {
            'type': 'general',
            'entities': {},
            'action': None
        }
        
        # Check for student queries
        student_patterns = [
            r'student\s+(\w+)',
            r'admission\s*[#:]*\s*(\d+)',
            r'pupil\s+(\w+)',
            r'learner\s+(\w+)',
            r'about\s+(\w+)',
        ]
        
        for pattern in student_patterns:
            match = re.search(pattern, message_lower)
            if match:
                intent['type'] = 'student'
                intent['entities']['query'] = match.group(1)
                break
        
        # Check for admission number
        admission_match = re.search(r'\b(\d{4,6})\b', message)
        if admission_match:
            intent['type'] = 'student'
            intent['entities']['admission'] = admission_match.group(1)
        
        # Check for statistics queries
        if any(word in message_lower for word in ['how many', 'total', 'count', 'statistics', 'stats']):
            intent['type'] = 'stats'
        
        # Check for stream queries
        stream_match = re.search(r'stream\s+(\w+)', message_lower)
        if stream_match:
            intent['type'] = 'stream'
            intent['entities']['stream'] = stream_match.group(1)
        
        # Check for reports queries
        if any(word in message_lower for word in ['report', 'case', 'offense', 'incident']):
            intent['action'] = 'reports'
        
        return intent
    
    def _generate_fallback_response(self, intent, data):
        """Generate intelligent fallback response based on intent and data"""
        response = ""
        
        if intent['type'] == 'student' and data:
            student_data = data
            name = student_data.get('name', 'the student')
            
            response = f"📊 **Student Profile: {name}**\n\n"
            response += f"• **Admission:** {student_data.get('admission_number', 'N/A')}\n"
            response += f"• **Stream:** {student_data.get('stream', 'Not Assigned')}\n"
            response += f"• **Form:** {student_data.get('form', 'N/A')}\n"
            response += f"• **Risk Level:** {student_data.get('risk_level', 'Unknown')}\n"
            response += f"• **Risk Score:** {student_data.get('risk_score', 0)}%\n"
            response += f"• **Total Reports:** {student_data.get('total_reports', 0)}\n"
            
            if student_data.get('days_since_last_incident') is not None:
                response += f"• **Days Since Last Incident:** {student_data['days_since_last_incident']}\n"
            
            if student_data.get('intervention_count', 0) > 0:
                response += f"• **Interventions:** {student_data['intervention_count']}\n"
            
            if student_data.get('class_teacher'):
                response += f"• **Class Teacher:** {student_data['class_teacher']['name']}\n"
            
            # Category breakdown
            if student_data.get('category_breakdown'):
                response += "\n**Top Offenses:**\n"
                for cat in student_data['category_breakdown'][:3]:
                    response += f"• {cat['category__name']}: {cat['count']} reports\n"
            
            # Recent reports
            if student_data.get('recent_reports'):
                response += "\n**Recent Reports:**\n"
                for report in student_data['recent_reports'][:3]:
                    response += f"• {report['date']} - {report['category']} ({report['rating']})\n"
            
            # Recommendations based on risk level
            if student_data.get('risk_level') == 'CRITICAL':
                response += "\n⚠️ **Immediate Action Required:**\n"
                response += "1. Schedule parent-teacher conference TODAY\n"
                response += "2. Refer to school counselor\n"
                response += "3. Create behavior intervention plan\n"
            elif student_data.get('risk_level') == 'WARNING':
                response += "\n📋 **Recommended Actions:**\n"
                response += "1. Schedule parent meeting within 1 week\n"
                response += "2. Implement behavior tracking\n"
                response += "3. Assign mentor or buddy\n"
            else:
                response += "\n✅ **Status: Good**\n"
                response += "Continue positive reinforcement and monitoring.\n"
        
        elif intent['type'] == 'stats':
            stats = data.get('stats', {})
            response = f"📊 **School Statistics**\n\n"
            response += f"• **Total Students:** {stats.get('total_students', 0)}\n"
            response += f"• **Critical Cases:** {stats.get('critical_count', 0)}\n"
            response += f"• **Warning Cases:** {stats.get('warning_count', 0)}\n"
            response += f"• **Good Status:** {stats.get('good_count', 0)}\n"
            response += f"• **Average Risk:** {stats.get('avg_risk_score', 0)}%\n"
            response += f"• **Total Reports:** {stats.get('total_reports', 0)}\n"
            response += f"• **Reports Today:** {stats.get('reports_today', 0)}\n"
            response += f"• **Online Teachers:** {stats.get('online_teachers', 0)}/{stats.get('total_teachers', 0)}\n"
            
            if stats.get('top_categories'):
                response += "\n**Top Offense Categories:**\n"
                for cat in stats['top_categories']:
                    response += f"• {cat['category__name']}: {cat['count']} reports\n"
            
            if stats.get('stream_breakdown'):
                response += "\n**Stream Breakdown:**\n"
                for name, count in stats['stream_breakdown'].items():
                    response += f"• {name}: {count} students\n"
        
        elif intent['type'] == 'stream' and data:
            stream_data = data
            response = f"📊 **Stream Analysis: {stream_data.get('stream', 'Unknown')}**\n\n"
            response += f"• **Total Students:** {stream_data.get('total_students', 0)}\n"
            response += f"• **Critical:** {stream_data.get('critical_count', 0)}\n"
            response += f"• **Warning:** {stream_data.get('warning_count', 0)}\n"
            response += f"• **Good:** {stream_data.get('good_count', 0)}\n"
            response += f"• **Average Risk:** {stream_data.get('average_risk', 0)}%\n"
            
            if stream_data.get('top_offenders'):
                response += "\n**Top Offenders:**\n"
                for student in stream_data['top_offenders']:
                    response += f"• {student['name']} ({student['admission_number']}): {student['report_count']} reports\n"
        
        else:
            response = "🤖 I'm here to help you with the school discipline system.\n\n"
            response += "**What I can do:**\n"
            response += "• 📊 Show school statistics\n"
            response += "• 👤 Look up student profiles\n"
            response += "• 📋 View discipline reports\n"
            response += "• 📈 Analyze stream/class performance\n"
            response += "• 📚 Answer questions about Kenyan Education Law\n\n"
            response += "**Try asking:**\n"
            response += "• 'Show me student John Doe'\n"
            response += "• 'How many students are in the system?'\n"
            response += "• 'What are the reports for admission 9486?'\n"
            response += "• 'Analyze the Gonza stream'\n"
            response += "• 'What does the Education Act say about discipline?'"
        
        return response
    
    def chat(self, user_message, student_id=None, conversation_history=None):
        """Enhanced chat with full database integration"""
        
        # Parse user intent
        intent = self._parse_user_intent(user_message)
        
        # Get student data if referenced
        student_data = None
        if intent['type'] == 'student':
            query = intent['entities'].get('query')
            admission = intent['entities'].get('admission')
            
            if admission:
                student_data = self.get_student_data(admission=admission)
            elif query:
                student_data = self.get_student_data(name=query)
            elif student_id:
                student_data = self.get_student_data(student_id=student_id)
        
        # Get school stats if needed
        school_stats = None
        if intent['type'] == 'stats':
            school_stats = self.get_school_stats()
        
        # Get stream analysis if needed
        stream_data = None
        if intent['type'] == 'stream':
            stream_name = intent['entities'].get('stream')
            if stream_name:
                stream = Stream.objects.filter(name__icontains=stream_name).first()
                if stream:
                    stream_data = self.get_stream_analysis(stream.id)
        
        # Build context
        context = {
            'intent': intent,
            'student': student_data,
            'stats': school_stats,
            'stream_analysis': stream_data,
            'timestamp': timezone.now().isoformat()
        }
        
        # If student data is not found by AI, fallback to data-driven response
        if not student_data and intent['type'] == 'student':
            fallback_response = self._generate_fallback_response(intent, None)
            return {
                'success': True,
                'response': fallback_response,
                'mode': 'data_fallback',
                'context': context
            }
        
        # If stats requested and we have data
        if intent['type'] == 'stats' and school_stats:
            fallback_response = self._generate_fallback_response(intent, context)
            return {
                'success': True,
                'response': fallback_response,
                'mode': 'data_fallback',
                'context': context
            }
        
        # If stream data requested
        if intent['type'] == 'stream' and stream_data:
            fallback_response = self._generate_fallback_response(intent, context)
            return {
                'success': True,
                'response': fallback_response,
                'mode': 'data_fallback',
                'context': context
            }
        
        # Build messages for AI
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)}
        ]
        
        if conversation_history:
            for msg in conversation_history[-10:]:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})
        
        # Try AI models
        result = self._try_model(messages, self.primary_model)
        
        if result.get('success'):
            return {
                'success': True,
                'response': result['response'],
                'usage': result.get('usage', {}),
                'mode': 'ai',
                'model_used': result.get('model_used'),
                'context': context
            }
        
        # Try fallback models
        for model in [self.fallback_model] + self.backup_models:
            print(f"🔄 Trying fallback model: {model}")
            result = self._try_model(messages, model)
            if result.get('success'):
                return {
                    'success': True,
                    'response': result['response'],
                    'usage': result.get('usage', {}),
                    'mode': 'ai_fallback',
                    'model_used': model,
                    'context': context
                }
        
        # Final fallback - data-driven response
        fallback_response = self._generate_fallback_response(intent, context)
        return {
            'success': True,
            'response': fallback_response,
            'mode': 'data_fallback',
            'context': context
        }
