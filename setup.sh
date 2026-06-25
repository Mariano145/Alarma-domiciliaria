#!/bin/bash
# Setup script - Creates .env from template if it doesn't exist

if [ ! -f .env ]; then
  cat > .env << 'EOF'
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=soft_eng_db
POSTGRES_USER=soft_eng_user
POSTGRES_PASSWORD=dev_password_2026
POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
DATABASE_USERNAME=${POSTGRES_USER}
DATABASE_PASSWORD=${POSTGRES_PASSWORD}
FLASK_APP=main:app
FLASK_DEBUG=1
FLASK_ENV=development
FLASK_PORT=5000
FLASK_SECRET_KEY=your_super_secret_key_here_change_in_production
SPRING_PORT=8080
SPRING_PROFILES_ACTIVE=dev
NESTJS_PORT=3000
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:5000
EOF
  echo ".env created successfully"
else
  echo ".env already exists, skipping"
fi
