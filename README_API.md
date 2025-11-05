# YouTube to MP3 API

API REST service để tải video YouTube và chuyển đổi sang MP3. Dễ dàng tích hợp với n8n, Zapier, Make.com và các automation tools khác.

## Tính năng

- ✅ RESTful API với FastAPI
- ✅ Async processing với background tasks
- ✅ Track tiến độ download real-time
- ✅ Docker support để deploy dễ dàng
- ✅ Tích hợp dễ dàng với n8n, Zapier, Make.com
- ✅ CORS enabled cho frontend integration
- ✅ Swagger UI documentation tự động

## Cài đặt và Chạy

### Cách 1: Chạy với Docker (Khuyến khích)

```bash
# Build và chạy
docker-compose up -d

# Kiểm tra logs
docker-compose logs -f

# Dừng service
docker-compose down
```

API sẽ chạy tại: `http://localhost:8000`

### Cách 2: Chạy trực tiếp với Python

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy API server
python api.py

# Hoặc dùng uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Cách 3: Deploy lên Cloud

#### Railway
```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login và deploy
railway login
railway init
railway up
```

#### Render
1. Tạo new Web Service
2. Connect GitHub repository
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

#### AWS Lambda / Google Cloud Run
- Sử dụng Dockerfile có sẵn để deploy

## API Endpoints

### 1. POST /download
Tạo task download video YouTube

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "no_check_certificate": false
}
```

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "pending",
  "message": "Download task đã được tạo"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### 2. GET /status/{task_id}
Kiểm tra trạng thái task

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "title": "Video Title",
  "file_path": "/path/to/file.mp3",
  "error": null,
  "created_at": "2024-01-01T00:00:00"
}
```

**Status values:**
- `pending`: Task đang chờ
- `downloading`: Đang tải
- `completed`: Hoàn thành
- `failed`: Thất bại

**cURL Example:**
```bash
curl "http://localhost:8000/status/YOUR_TASK_ID"
```

### 3. GET /download/{task_id}
Tải file MP3 về

**Response:** File MP3

**cURL Example:**
```bash
curl "http://localhost:8000/download/YOUR_TASK_ID" -o music.mp3
```

### 4. DELETE /task/{task_id}
Xóa task và file

**Response:**
```json
{
  "message": "Task đã được xóa thành công"
}
```

### 5. GET /tasks
Liệt kê tất cả tasks

**Response:**
```json
{
  "tasks": [...]
}
```

### 6. GET /
Health check endpoint

### 7. GET /docs
Swagger UI documentation (tự động)

## Tích hợp với n8n

### Workflow 1: Basic Download

1. **Trigger Node** (Webhook hoặc Manual)
   - Nhận YouTube URL

2. **HTTP Request Node** - Tạo download task
   - Method: `POST`
   - URL: `http://localhost:8000/download`
   - Body:
   ```json
   {
     "url": "{{$json.youtube_url}}"
   }
   ```

3. **Wait Node**
   - Wait for 5 seconds

4. **HTTP Request Node** - Check status
   - Method: `GET`
   - URL: `http://localhost:8000/status/{{$node["HTTP Request"].json.task_id}}`

5. **IF Node** - Kiểm tra status
   - Condition: `{{$json.status}} === "completed"`

6. **HTTP Request Node** - Download file
   - Method: `GET`
   - URL: `http://localhost:8000/download/{{$json.task_id}}`
   - Response Format: `File`

### Workflow 2: Advanced với Loop

```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "youtube-mp3",
        "method": "POST"
      }
    },
    {
      "name": "Create Download Task",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/download",
        "jsonParameters": true,
        "bodyParametersJson": "={{ {\"url\": $json.body.url} }}"
      }
    },
    {
      "name": "Loop Until Complete",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Check status every 2 seconds\nconst taskId = $input.first().json.task_id;\nconst apiUrl = 'http://localhost:8000';\n\nlet status = 'pending';\nlet attempts = 0;\nconst maxAttempts = 60; // 2 minutes max\n\nwhile (status !== 'completed' && status !== 'failed' && attempts < maxAttempts) {\n  const response = await $http.get(`${apiUrl}/status/${taskId}`);\n  status = response.status;\n  \n  if (status === 'completed') {\n    return { taskId, status, ...response };\n  }\n  \n  if (status === 'failed') {\n    throw new Error(response.error);\n  }\n  \n  await new Promise(resolve => setTimeout(resolve, 2000));\n  attempts++;\n}\n\nif (attempts >= maxAttempts) {\n  throw new Error('Timeout: Download took too long');\n}\n"
      }
    },
    {
      "name": "Download MP3",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "=http://localhost:8000/download/{{$json.taskId}}",
        "responseFormat": "file"
      }
    }
  ]
}
```

### Workflow 3: Batch Processing

Xử lý nhiều YouTube URLs cùng lúc:

1. **Webhook/Manual Trigger** - Nhận array of URLs
2. **Split In Batches Node** - Chia nhỏ URLs
3. **HTTP Request** - Tạo download tasks
4. **Loop** - Check status cho từng task
5. **Merge Node** - Gộp kết quả
6. **Respond to Webhook** - Trả về danh sách files

## Tích hợp với Zapier

1. **Trigger**: Gmail (hoặc bất kỳ trigger nào)
2. **Action**: Webhooks by Zapier
   - Method: POST
   - URL: `https://your-api.com/download`
   - Data: `{"url": "YOUTUBE_URL"}`
3. **Delay**: 10 seconds
4. **Action**: Webhooks by Zapier
   - Method: GET
   - URL: `https://your-api.com/status/{{task_id}}`
5. **Action**: Conditional path dựa trên status
6. **Action**: Download file từ API

## Tích hợp với Make.com (Integromat)

1. **HTTP Module** - Make a Request
   - URL: `https://your-api.com/download`
   - Method: POST
   - Body: `{"url": "{{youtube_url}}"}`

2. **Sleep Module** - 10 seconds

3. **HTTP Module** - Check Status
   - URL: `https://your-api.com/status/{{1.data.task_id}}`

4. **Router Module** - Conditional routing

5. **HTTP Module** - Download File

## Testing API

### Với curl:

```bash
# 1. Tạo download task
TASK_ID=$(curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' | jq -r '.task_id')

echo "Task ID: $TASK_ID"

# 2. Kiểm tra status
curl "http://localhost:8000/status/$TASK_ID"

# 3. Tải file MP3
curl "http://localhost:8000/download/$TASK_ID" -o music.mp3
```

### Với Python:

```python
import requests
import time

# 1. Tạo download task
response = requests.post(
    "http://localhost:8000/download",
    json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
)
task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")

# 2. Polling để check status
while True:
    status_response = requests.get(f"http://localhost:8000/status/{task_id}")
    status_data = status_response.json()

    print(f"Status: {status_data['status']} - Progress: {status_data['progress']}%")

    if status_data["status"] == "completed":
        break
    elif status_data["status"] == "failed":
        print(f"Error: {status_data['error']}")
        exit(1)

    time.sleep(2)

# 3. Tải file MP3
file_response = requests.get(f"http://localhost:8000/download/{task_id}")
with open("music.mp3", "wb") as f:
    f.write(file_response.content)

print("Download completed!")
```

### Với JavaScript:

```javascript
// 1. Tạo download task
const createTask = await fetch('http://localhost:8000/download', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
  })
});
const { task_id } = await createTask.json();
console.log('Task ID:', task_id);

// 2. Polling status
const checkStatus = async () => {
  const response = await fetch(`http://localhost:8000/status/${task_id}`);
  const data = await response.json();

  console.log(`Status: ${data.status} - Progress: ${data.progress}%`);

  if (data.status === 'completed') {
    return data;
  } else if (data.status === 'failed') {
    throw new Error(data.error);
  }

  await new Promise(resolve => setTimeout(resolve, 2000));
  return checkStatus();
};

await checkStatus();

// 3. Tải file
window.location.href = `http://localhost:8000/download/${task_id}`;
```

## Deploy lên Production

### Environment Variables

Tạo file `.env`:
```env
API_HOST=0.0.0.0
API_PORT=8000
DOWNLOADS_DIR=/app/downloads
MAX_CONCURRENT_DOWNLOADS=5
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HTTPS với Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com
```

## Security Best Practices

1. **Rate Limiting**: Thêm middleware để limit requests
2. **Authentication**: Thêm API key hoặc JWT authentication
3. **CORS**: Cấu hình CORS cho production
4. **File Cleanup**: Tự động xóa files cũ
5. **Input Validation**: Validate YouTube URLs
6. **Error Handling**: Log errors properly

## Performance Tips

1. **Caching**: Cache video info để tránh duplicate downloads
2. **Queue System**: Sử dụng Celery hoặc Redis Queue cho large scale
3. **CDN**: Upload files lên S3/CloudFlare để serve tốt hơn
4. **Load Balancing**: Deploy multiple instances với load balancer

## Troubleshooting

**Lỗi "ffmpeg not found":**
- Đảm bảo ffmpeg đã được cài trong Docker image
- Hoặc cài ffmpeg trên host system

**Lỗi SSL Certificate:**
- Sử dụng `"no_check_certificate": true` trong request body

**File không tải được:**
- Kiểm tra permissions của thư mục downloads
- Kiểm tra disk space

**Task bị stuck:**
- Check logs: `docker-compose logs -f`
- Restart service: `docker-compose restart`

## Support

- GitHub Issues: [Link to repo]
- Documentation: http://localhost:8000/docs
- n8n Community: https://community.n8n.io

## License

MIT License
