# 🤖 Universal Telegram Bot Template

Telegram botlar uchun universal, kuchli va AI-integrated template.

## ✨ Features

- ✅ Admin panel bilan to'liq bot boshqaruvi
- 📊 Keng qamrovli statistika va analytics
- 🤖 AI-powered tahlil va insights
- 📢 Broadcast system (xabar yuborish)
- 📺 Majburiy obuna (forced subscription)
- 🗄️ PostgreSQL database
- 🚀 Redis caching
- 📈 Real-time analytics tracking
- 🔒 Security va validation

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker (optional)

### 2. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd telegram-bot-template

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env file with your credentials
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 4. Run Bot

```bash
# Development
python -m bot.main

# Production (Docker)
docker-compose up -d
```

## 📁 Project Structure

```
telegram-bot-template/
├── bot/
│   ├── config/          # Configuration
│   ├── database/        # Database models & repositories
│   ├── handlers/        # Message handlers
│   ├── middlewares/     # Middlewares
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── alembic/             # Database migrations
└── docker-compose.yml   # Docker configuration
```

## 🎯 Usage

### Admin Commands

- `/admin` or `/panel` - Admin panelga kirish
- Faqat `ADMIN_USER_ID` da belgilangan user admin

### User Flow

- Oddiy userlar botga yozganda "Tez orada javob beramiz" xabari keladi
- Barcha harakatlar tracking qilinadi (analytics uchun)

## 📊 Database Schema

Quyidagi jadvallar mavjud:

- `users` - Foydalanuvchilar
- `user_interactions` - Har bir harakat tracking
- `user_sessions` - Session tahlili
- `channels` - Majburiy obuna kanallari
- `user_subscriptions` - Obuna tracking
- `broadcasts` - Xabar yuborish
- `broadcast_deliveries` - Yuborish tracking
- `analytics_cache` - Analytics cache
- `bot_settings` - Bot sozlamalari

## 🔧 Configuration

`.env` faylda quyidagi parametrlarni sozlang:

- `BOT_TOKEN` - Telegram bot token
- `ADMIN_USER_ID` - Admin user ID
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_HOST` - Redis host
- `OPENAI_API_KEY` - OpenAI API key (optional)

## 📝 License

MIT License
```