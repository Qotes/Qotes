# 卡片

## 结构

### 类似Qotes之前的设计,树状卡片/卡片集

```javascript
user = {
    nickname: 'Sy',
    email: 'somarl@live.com',
    cards: [
        'imGrqeQD',
        'mGiqeQrg',
        ...
    ],
    permissions: 0b11111111
}
```

## 操作

### 点击展开，展开以后原卡片到左上角， 子卡片依次排开，再次点击原卡片进行折叠

- request and response

```javascript
// request(cardID/userID) ----> response([currentCard subCard1 subCard2 ...])
requestJson = {
    requestID: 'imGrqeQD',
    requestType: 'card',
    meta: {
        offset: 0,
        limit: 20
    }
}
responseJson = {
    status: 'success',
    request: requestJson,
    data: {
        cards: [
            'imGrqeQD',
            'mGiqeQrg'
            ...
        ]
    }
}
```

### 根目录是用户卡片

## 样式

## 备忘

- 注册选项
