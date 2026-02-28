#!/bin/bash
echo "🛒 ダミーサイト起動中..."
python3 demo_site/app.py &
FLASK_PID=$!
sleep 2
echo "📊 ダッシュボード起動中..."
streamlit run dashboard/app.py --server.port 8501 &
STREAMLIT_PID=$!
echo ""
echo "✅ 起動完了！"
echo "  ダミーサイト:    http://localhost:5001"
echo "  ダッシュボード:  http://localhost:8501"
echo ""
echo "停止: kill $FLASK_PID $STREAMLIT_PID"
wait
