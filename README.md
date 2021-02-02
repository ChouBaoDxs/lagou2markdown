# lagou2markdown
使用 python3 将自己购买的拉勾课程转为本地 markdown，课程列表地址：https://kaiwu.lagou.com/learn

## 使用指南
1. 安装依赖
    ```shell
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    ```
2. 根据实际情况修改 config.yml
    ```yaml
    gate_login_token: "{这里填写自己的gate_login_token}" # 网页登陆完拉勾教育之后，填写 cookie 里的 gate_login_token
    course_ids: # 要爬取的课程 id，多个
    - 69 # 分布式技术原理与实战45讲
    - 447 # Kubernetes 原理剖析与实战应用
    save_dir: "book" # 保存目录，默认会在当前目录下新建一个 book 目录
    ```
3. 运行主程序：`python3 main.py`
4. 爬取结果预览：
```
├── book
│   └── 分布式技术原理与实战45讲
│       ├── 1-开篇词：搭建分布式知识体系，挑战高薪 Offer.md
│       ├── 2-第01讲：如何证明分布式系统的 CAP 理论？.md
│       └── img
│           ├── 1
│           │   ├── 1.png
│           │   ├── 2.png
│           │   ├── 3.png
│           │   ├── 4.png
│           │   └── 5.png
│           └── 2
│               ├── 1.png
│               ├── 2.png
│               ├── 3.png
│               └── 4.png
├── config.yml
├── main.py
└── requirements.txt
```