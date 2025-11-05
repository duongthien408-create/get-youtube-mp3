# Hướng dẫn Deploy lên Cloud

Hướng dẫn chi tiết để deploy YouTube to MP3 API lên các cloud platforms phổ biến.

---

## 1. Railway ⭐ (Khuyến khích - Dễ nhất)

**Free tier**: $5 credit/tháng (đủ dùng cho project nhỏ)

### Bước 1: Tạo tài khoản
1. Truy cập: https://railway.app
2. Sign up bằng GitHub
3. Verify email

### Bước 2: Deploy từ GitHub

**Cách 1: Deploy từ GitHub (Khuyến khích)**
```bash
# Push code lên GitHub repository của bạn
git push origin main

# Vào Railway Dashboard
# 1. Click "New Project"
# 2. Chọn "Deploy from GitHub repo"
# 3. Chọn repository: duongthien408-create/get-youtube-mp3
# 4. Railway sẽ tự động detect Dockerfile và deploy
```

**Cách 2: Deploy bằng Railway CLI**
```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login
railway login

# Init project
railway init

# Deploy
railway up

# Lấy URL
railway domain
```

### Bước 3: Cấu hình (nếu cần)
Railway tự động:
- ✅ Detect và build Dockerfile
- ✅ Tạo domain (format: xxx.up.railway.app)
- ✅ Enable HTTPS
- ✅ Auto restart on failure

### Bước 4: Lấy URL
```bash
# Nếu dùng CLI
railway domain

# Hoặc xem trong Dashboard > Settings > Domains
```

**URL API của bạn**: `https://YOUR-APP.up.railway.app`

### Test API:
```bash
curl https://YOUR-APP.up.railway.app/
```

---

## 2. Render (Free tier tốt nhưng cold start chậm)

**Free tier**: Unlimited, nhưng sleep sau 15 phút không dùng

### Bước 1: Tạo tài khoản
1. Truy cập: https://render.com
2. Sign up bằng GitHub

### Bước 2: Deploy

**Cách 1: Từ Dashboard (Dễ)**
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Cấu hình:
   - **Name**: youtube-mp3-api
   - **Region**: Singapore (gần VN nhất)
   - **Branch**: main (hoặc claude/youtube-to-mp3-converter-...)
   - **Root Directory**: (để trống)
   - **Environment**: Docker
   - **Plan**: Free

4. Click "Create Web Service"

**Cách 2: Dùng render.yaml (Tự động)**

File `render.yaml` đã có sẵn trong repo, Render sẽ tự động detect.

### Bước 3: Đợi deploy (5-10 phút lần đầu)

Monitor logs trong Dashboard

### Bước 4: Lấy URL

**URL API**: `https://youtube-mp3-api.onrender.com`

### ⚠️ Lưu ý:
- Free tier sẽ **sleep sau 15 phút** không có request
- Request đầu tiên sau khi sleep sẽ **chậm ~30s** (cold start)
- Nếu cần uptime 24/7, upgrade lên paid ($7/tháng)

### Giữ cho service không sleep (Optional):

Dùng cron job ping mỗi 10 phút:
```bash
# Dùng cron-job.org hoặc UptimeRobot
# Ping URL: https://your-app.onrender.com/
```

---

## 3. Fly.io (Tốt, nhanh, free tier đủ dùng)

**Free tier**: 3 VMs nhỏ, 160GB bandwidth/tháng

### Bước 1: Cài Fly CLI

**macOS:**
```bash
brew install flyctl
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### Bước 2: Login và tạo app

```bash
# Login
fly auth login

# Đi vào thư mục project
cd get-youtube-mp3

# Launch app (fly.toml đã có sẵn)
fly launch --copy-config

# Khi được hỏi:
# - App name: nhấn Enter (dùng random) hoặc nhập tên
# - Region: chọn Singapore (sin)
# - Setup PostgreSQL: NO
# - Deploy now: YES
```

### Bước 3: Deploy

```bash
# Deploy
fly deploy

# Xem status
fly status

# Xem logs
fly logs
```

### Bước 4: Lấy URL

```bash
fly info
```

**URL API**: `https://YOUR-APP.fly.dev`

### Useful commands:

```bash
# Xem logs realtime
fly logs -a your-app-name

# SSH vào machine
fly ssh console

# Scale up/down
fly scale count 1

# Open app in browser
fly open
```

---

## 4. Google Cloud Run (Pay-as-you-go, scale tốt)

**Pricing**: Free 2 triệu requests/tháng

### Bước 1: Setup Google Cloud

```bash
# Cài Google Cloud CLI
# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Init
gcloud init
gcloud auth login
```

### Bước 2: Enable APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Bước 3: Build và Deploy

```bash
# Set project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/youtube-mp3-api

# Deploy to Cloud Run
gcloud run deploy youtube-mp3-api \
  --image gcr.io/$PROJECT_ID/youtube-mp3-api \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10
```

### Bước 4: Lấy URL

Cloud Run sẽ hiển thị URL sau khi deploy:
```
Service URL: https://youtube-mp3-api-xxx-as.a.run.app
```

---

## 5. DigitalOcean App Platform

**Pricing**: $5/tháng (basic)

### Bước 1: Create App

1. Truy cập: https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect GitHub repository
4. Chọn branch: main

### Bước 2: Cấu hình

- **Type**: Web Service
- **Environment**: Docker
- **HTTP Port**: 8000
- **Region**: Singapore
- **Plan**: Basic ($5/month)

### Bước 3: Deploy

Click "Create Resources" và đợi deploy

**URL**: `https://your-app.ondigitalocean.app`

---

## 6. Vercel (Edge Functions) ❌ Không khuyến khích

⚠️ **Lưu ý**: Vercel không hỗ trợ:
- FFmpeg
- Long-running processes
- File downloads lớn

Không nên dùng Vercel cho project này.

---

## So sánh các platforms:

| Platform | Free Tier | Cold Start | Speed | Difficulty | Recommend |
|----------|-----------|------------|-------|------------|-----------|
| **Railway** | $5 credit/tháng | Không | Rất nhanh | Dễ nhất | ⭐⭐⭐⭐⭐ |
| **Render** | Unlimited* | 30s | Trung bình | Dễ | ⭐⭐⭐⭐ |
| **Fly.io** | 3 VMs | Không | Nhanh | Trung bình | ⭐⭐⭐⭐⭐ |
| **Cloud Run** | 2M req/mo | ~5s | Nhanh | Khó | ⭐⭐⭐⭐ |
| **DigitalOcean** | Không | Không | Nhanh | Dễ | ⭐⭐⭐ |

\* Render free tier sleep sau 15 phút

---

## Sau khi deploy thành công:

### 1. Test API:

```bash
# Health check
curl https://YOUR-API-URL/

# Test download
curl -X POST "https://YOUR-API-URL/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "no_check_certificate": true}'
```

### 2. Xem API docs:

Truy cập: `https://YOUR-API-URL/docs`

### 3. Tích hợp với n8n:

Thay `http://localhost:8000` bằng `https://YOUR-API-URL` trong workflows

---

## Troubleshooting:

### Lỗi "Out of memory"
- Tăng memory limit (Railway: 512MB → 1GB)
- Cloud Run: `--memory 1Gi`

### Lỗi "Build failed"
- Check Dockerfile syntax
- Đảm bảo requirements.txt có đầy đủ dependencies

### Lỗi "Port already in use"
- Đảm bảo dùng `ENV PORT` trong Dockerfile
- Cloud platforms tự set PORT variable

### API chậm
- Check region (chọn Singapore cho VN)
- Upgrade plan nếu cần

### Cold start chậm (Render)
- Dùng Uptime monitoring để ping
- Hoặc upgrade lên paid plan

---

## Monitoring & Logs:

### Railway:
```bash
railway logs
```

### Render:
Dashboard → Logs tab

### Fly.io:
```bash
fly logs -a your-app-name
```

### Cloud Run:
```bash
gcloud run logs tail youtube-mp3-api
```

---

## Custom Domain (Optional):

### Railway:
1. Settings → Domains → Add Custom Domain
2. Add CNAME record: `xxx.railway.app`

### Render:
1. Settings → Custom Domains
2. Add CNAME record

### Fly.io:
```bash
fly certs add yourdomain.com
```

---

## Bảo mật:

### Thêm API Key authentication (Optional):

Sửa file `api.py`:

```python
from fastapi import Header, HTTPException

API_KEY = "your-secret-key"

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/download", dependencies=[Depends(verify_api_key)])
async def download_video(...):
    ...
```

Sử dụng:
```bash
curl -H "X-API-Key: your-secret-key" ...
```

---

## Cost Estimation:

### Railway:
- Free: $5 credit/tháng (~50-100 requests/ngày)
- Hobby: $5/tháng (unlimited)

### Render:
- Free: Unlimited* (sleep sau 15 phút)
- Starter: $7/tháng (no sleep)

### Fly.io:
- Free: ~1000 requests/ngày
- Paid: $1.94/tháng (1 VM)

### Cloud Run:
- Free: 2 triệu requests/tháng
- Paid: $0.00002400/request

---

## Kết luận:

**Recommend cho bạn:**

1. **Nếu cần ngay và dễ**: Railway hoặc Render
2. **Nếu muốn performance tốt**: Fly.io
3. **Nếu expect traffic lớn**: Google Cloud Run
4. **Nếu muốn control nhiều**: DigitalOcean VPS

**Quick start với Railway** (dễ nhất):
```bash
npm i -g @railway/cli
railway login
railway init
railway up
railway domain
```

✅ Xong! API của bạn đã online!
