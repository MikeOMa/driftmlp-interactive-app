#!/bin/sh
set -eu

python /app/tile_proxy.py &
python -m streamlit run /app/streamlit_app.py --server.port=8501 --server.address=127.0.0.1 &
exec nginx -g 'daemon off;'
