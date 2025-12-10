# n8n Integration Guide

## Simple Endpoints for n8n

The API now has **simple endpoints** that return binary images ready for GPT modules.

## Option 1: Single Page Screenshot (GET - Simplest)

**Endpoint:** `GET /screenshot?url=YOUR_URL`

**In n8n:**
1. Add **HTTP Request** node
2. Set:
   - **Method:** GET
   - **URL:** `https://your-app.onrender.com/screenshot?url={{$json.url}}`
   - **Response Format:** File
   - **Binary Data:** true

3. Connect to **GPT** node
   - The image will be automatically passed as binary

**Example:**
```
https://your-app.onrender.com/screenshot?url=https://example.com
```

## Option 2: Single Page Screenshot (POST)

**Endpoint:** `POST /screenshot-binary`

**In n8n:**
1. Add **HTTP Request** node
2. Set:
   - **Method:** POST
   - **URL:** `https://your-app.onrender.com/screenshot-binary`
   - **Body:** JSON
   ```json
   {
     "url": "https://example.com"
   }
   ```
   - **Response Format:** File
   - **Binary Data:** true

3. Connect to **GPT** node
   - The image will be automatically passed as binary

## Option 3: All Pages Screenshot (ZIP)

**Endpoint:** `POST /screenshot-all-binary`

**In n8n:**
1. Add **HTTP Request** node
2. Set:
   - **Method:** POST
   - **URL:** `https://your-app.onrender.com/screenshot-all-binary`
   - **Body:** JSON
   ```json
   {
     "url": "https://example.com",
     "max_pages": 10
   }
   ```
   - **Response Format:** File
   - **Binary Data:** true

3. Add **Extract from Archive** node to unzip
4. Connect to **GPT** node with each image

## Complete n8n Workflow Example

```
[Webhook/Trigger] 
  → [Set URL variable] 
  → [HTTP Request: GET /screenshot?url={{$json.url}}] 
  → [GPT Vision Node]
```

## Key Points

✅ **No base64 conversion needed** - Images are returned as binary PNG  
✅ **Simple URL parameter** - Just pass the website URL  
✅ **Ready for GPT** - Binary format works directly with GPT vision modules  
✅ **No complex parameters** - Uses sensible defaults  

## Testing Locally

```bash
# Single page (returns PNG binary)
curl "http://localhost:8000/screenshot?url=https://example.com" --output test.png

# Or in browser
http://localhost:8000/screenshot?url=https://example.com
```

## Response Format

- **Single screenshot:** PNG image binary (Content-Type: image/png)
- **All pages:** ZIP file with PNG images (Content-Type: application/zip)

No JSON, no base64 - just pure binary files ready to use!

