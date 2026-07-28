# API

## 登录
`POST /api/auth/login`

Request:
```json
{
  "username": "admin",
  "password": "admin"
}
```

Response:
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "is_admin": true,
    "allowed_paths": [""]
  }
}
```

## 当前用户
`GET /api/auth/me`

Header:
`Authorization: Bearer <token>`

## 用户管理（管理员）
- `GET /api/users`
- `POST /api/users`
- `PUT /api/users/{id}`
- `DELETE /api/users/{id}`

## 目录选择（管理员）
- `GET /api/fs/roots`
- `GET /api/fs/list?path=...`

## 集合封面
- `GET /api/collections/{id}/cover` 返回集合封面缩略图（未设置时会自动选择并固定）

## Tree
`GET /api/tree?root=/photos&depth=3`

Response:
```json
{
  "name": "photos",
  "path": "photos",
  "type": "folder",
  "children": [
    {"name": "set1", "path": "photos/set1", "type": "folder", "children": []},
    {"name": "pack.zip", "path": "photos/pack.zip", "type": "archive"}
  ]
}
```

## List Folder
`GET /api/folder?path=/photos/set1&page=1&page_size=60`

Response:
```json
{
  "folder": "photos/set1",
  "folders": [{"name": "sub", "path": "photos/set1/sub"}],
  "images": [{"name": "a.jpg", "path": "photos/set1/a.jpg"}],
  "archives": [{"name": "pack.zip", "path": "photos/set1/pack.zip"}],
  "page": 1,
  "page_size": 60,
  "total_images": 120,
  "has_more": true
}
```

## 集合目录（可选汇总）
`GET /api/collections/{id}/folder?path=...&view=flat`

说明：`view=flat` 会汇总子目录图片（默认只显示当前目录）。

## List Archive
`GET /api/archive?path=/photos/set1/pack.zip&page=1&page_size=80`

Response:
```json
{
  "archive": "photos/set1/pack.zip",
  "files": [{"name": "001.jpg", "path": "folder/001.jpg"}],
  "page": 1,
  "page_size": 80,
  "total_files": 200,
  "has_more": true
}
```

## Image Stream
`GET /api/image?path=/photos/set1/a.jpg`

## Archive Image Stream
`GET /api/archive/image?path=/photos/set1/pack.zip&file=folder/001.jpg`

## Thumbnail
`GET /api/thumb?path=/photos/set1/a.jpg`

## Archive Thumbnail
`GET /api/archive/thumb?path=/photos/set1/pack.zip&file=folder/001.jpg`
