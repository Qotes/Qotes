# 卡片

## 结构

### 类似Qotes之前的设计,树状卡片/卡片集

```javascript
user = {
    nickname: 'Sy',
    email: 'somarl@live.com',
    qotes: [ // 直属卡片
        'imGrqeQD',
        'mGiqeQrg',
        ...
    ],
    _all: [ // 所有卡片
        'imGrqeQD',
        'mGiqeQrg',
        ...
    ],
    permissions: 0b11111111
    // followers/following/registerd/lastseen ...
}
```

```javascript
qote = {
    title: 'Get started', // 自动H1生成
    date: new Date(),
    gist: [ // 自动H2生成
        "What's Qotes",
        'Why do I need it',
        'How to qote'
    ]
    author: 'Sy',
    parent: 'imGrqeQD' // 如果是''则是作者的直属卡片
    permissions: 0b00000001
}
```

### 结构的区分

user作为树的根节点和qote并无太大差别,都是card.

最明显的差别在于qote不记录自身的子node,但是user需要,并且还分别记录直属qotes和下属qotes.

## 操作

### 点击展开，展开以后原卡片到左上角， 子卡片依次排开，再次点击原卡片进行折叠

- request and response

```javascript
// request(cardID/userID) ----> response([currentCard subCard1 subCard2 ...])
requestJson = {
    requestID: 'imGrqeQD',
    requestType: 'qote', // user
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
