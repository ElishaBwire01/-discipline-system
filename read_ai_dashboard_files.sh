#!/bin/bash

echo "==============================================="
echo "  AI DASHBOARD - ALL RELATED FILES"
echo "==============================================="
echo ""

# 1. AI Dashboard Template
echo "📄 1. AI DASHBOARD TEMPLATE"
echo "==============================================="
cat templates/ai_dashboard.html
echo ""

# 2. AI Dashboard View
echo "📄 2. AI DASHBOARD VIEW"
echo "==============================================="
grep -A 100 "def ai_dashboard" core/views.py
echo ""

# 3. Global Recommendations API
echo "📄 3. GLOBAL RECOMMENDATIONS API"
echo "==============================================="
grep -A 80 "def global_recommendations" core/views.py
echo ""

# 4. AI Chat View
echo "📄 4. AI CHAT VIEW"
echo "==============================================="
grep -A 50 "def ai_chat_page" core/views.py
echo ""

# 5. AI URLs
echo "📄 5. AI URL ROUTES"
echo "==============================================="
grep -A 20 "ai/" core/urls.py
echo ""

# 6. AI JavaScript
echo "📄 6. AI JAVASCRIPT"
echo "==============================================="
cat static/js/ai_recommendations.js 2>/dev/null || echo "File not found"
echo ""

# 7. AI Chat Template
echo "📄 7. AI CHAT TEMPLATE"
echo "==============================================="
cat templates/ai_chat.html 2>/dev/null || echo "File not found"
echo ""

# 8. AI Models (if any)
echo "📄 8. AI MODELS"
echo "==============================================="
grep -A 30 "class.*AI" core/models.py 2>/dev/null || echo "No AI models found"
echo ""

echo "==============================================="
echo "  ALL AI DASHBOARD FILES READ"
echo "==============================================="
