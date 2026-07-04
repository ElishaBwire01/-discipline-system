# core/views_chat.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg
import json
from .models import Student, DisciplineReport, Stream
from .ai_chat import PollinationAIChat

@login_required
def ai_chat_page(request):
    """Render the AI Chat page"""
    students = Student.objects.filter(is_active=True).select_related('stream')
    streams = Stream.objects.filter(is_active=True).order_by('name')
    
    context = {
        'students': students[:100],  # Limit for performance
        'streams': streams,
        'total_students': students.count(),
    }
    return render(request, 'ai_chat.html', context)

@csrf_exempt
@login_required
def ai_chat_api(request):
    """API endpoint for AI chat"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        student_id = data.get('student_id')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return JsonResponse({'error': 'Please enter a message'}, status=400)
        
        # Initialize AI chat
        ai = PollinationAIChat()
        
        # Get response
        result = ai.chat(
            user_message=user_message,
            student_id=student_id,
            conversation_history=conversation_history
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'response': result['response'],
                'usage': result.get('usage', {})
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def ai_chat_student_context(request):
    """Get student context for AI chat"""
    student_id = request.GET.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'Student ID required'}, status=400)
    
    try:
        student = Student.objects.get(id=student_id, is_active=True)
        reports = student.reports.select_related('category')
        
        data = {
            'id': student.id,
            'name': student.name,
            'admission_number': student.admission_number,
            'stream': student.stream.name if student.stream else 'N/A',
            'form': student.form,
            'risk_score': student.risk_score,
            'risk_level': student.risk_level,
            'total_reports': reports.count(),
            'recent_reports': []
        }
        
        for report in reports.order_by('-reported_at')[:5]:
            data['recent_reports'].append({
                'date': report.reported_at.strftime('%Y-%m-%d %H:%M'),
                'category': report.category.name,
                'rating': report.get_rating_display(),
                'points': report.points
            })
        
        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)