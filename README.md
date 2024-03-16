# 中大介绍官

本项目是在[Fay](https://github.com/TheRamU/Fay)开源数字人项目的基础上开发而成的，
针对 LLM 部分进行了修改和优化，重构了调用不同 LLM 的逻辑，并引入了向量数据库，
因此实现一个全自动的 24 小时在线的中大介绍官。

## 架构介绍

本项目可以分为三个部分，Controller 以 Webui 的形式供用户操作管理，
Fay Core 部分则处理数字人的核心逻辑，
View 则通过 UE5 游戏引擎将数字人进行可视化。

![structure](./docs/img/structure.drawio.svg)

### Fay Core

此部分是处理数字人的交互逻辑与相应的核心部分。
为了方便理解，我将其划分成几个小部分，并使用不同的颜色进行标注。

-   红色部分: Fay Core 与外部交互的接口，即通过 Webui 与 Microphone 接收外部文本输入，
    处理 Webui 发送的控制信号，
    以及通过 Speaker 与 UE5 与用户输出音频和视觉呈现。

-   绿色部分: 本系统使用的一些外部技术，具体如下。
    在此处，我只列举了核心的几个模块，
    对于情感分析等模块我没有了解与整理。
    而虽然 LLM 也是核心模块，但由于呗封装在 Handler 中，故没有单独指出。

    -   ASR: 将来自 Microphone 输入的文本转换为文本
    -   TTS: 将生成的文本转换为语音
    -   Lip: 通过语音为数字人生成唇形

-   蓝色部分: 本项目的核心处理组件，在下面我将分别详细介绍。

#### 1. Controller

> path: [fay_booter.py](./fay_booter.py)

该组件是对接用户通过 Webui 发送起停信号和消息，
对于前者而言，Controller 实际上控制的是外部输入设备 Microphone，
与 Handler 组件的开启与关闭。
而用户发送的消息，也是通过此处包装成 [`Interact` 对象](./core/interact.py)，
再交给 Interactive Queue 存储等待处理。

#### 2. Interactive Queue

> path: [core/fay_core.py](./core/fay_core.py) self.interactive

此组件用于存储用户从 Webui 输入消息，以及 Microphone 得到语音输入（会通过 ASR 技术转换成文本）。
设计该组件的目的其实与中间件中的消息队列如出一辙，通过队列，
就可以将消息生成与处理两部分进行解藕，通过异步方式进行处理。

#### 3. Handler

> path: [core/fay_core.py](./core/fay_core.py) \_\_auto_speak

该组件会通过轮询的方式处理消息队列中的信息。
当然，这里的死循环忙等是效率低下的，可以通过信号量对其进行优化。

首先，Handler 会通过 `determine_nlp_strategy()` 生成消息的回答，
该函数会通过配置文件中选择的 LLM 类型，调用对应的 bot 来生成回答。
这里使用了简单工厂模式，具体代码可见 [ai_module/enhance](./ai_module/enhance/)。
在原项目中，系统会通过 `__get_answer()` 从已经预设的 QA 文档中寻找问题的答案，
但本项目不希望使用该部分功能，因此废弃以提高效率。

此后，其会调用 `__say()` 函数通过将文本转换为语音，并保存在本地。
随后通过 `__send_or_play_audio()` 播放音频，
该函数中的 send 是指将音频文件通过 Websocket 发送给 UE5 进行播放，
值得注意的是，在发送之前还需要通过唇形算法来生成对应的唇形序列，保证 UE5 数字人自然回答。
而 play_audio 则是在本地进行播放。

至此，一条来自消息队列中的消息就处理完毕了。

### Fay Controller

> path: [`gui/`](gui)

数字人控制器部分是 Webui 的形式，此部分代码主要时使用 Vue + element 前端技术栈编写。
值得注意的是，这里的网页代码并非使用类似 Vite 的项目管理工具编写。
而前端的技术栈不能够直接与 Python 交互，
所以本项目通过 Flask 后端框架搭建 [Web 后端](./gui/flask_server.py)，
通过 RESTful API 与 Fay Core 的 Web 与其交互，
发送控制信息或消息，此后通过 Websocket 接受其状态和反馈信息。
同时，本项目使用 PyQt5 中的 [QtWebEngineWidget](./gui/window.py) 作为 Webui 的载体，
以便程序操控管理。

能够提供的功能如下。

1. 控制数字人启动和停止
2. 向数字人发送信息
3. 修改数字人的相关配置

> **ask 与 send 的区别：**
>
> 在原项目中只提供了`ask` API，其不仅会让 LLM 生成回答，
> 并且还会通过 TTS 模块生成并播放语音。
> 但后续为了调试 LLM 本身的能力，我又编写了`send` API，
> 而它只会让返回文本回答，并不会生成语音消息。
>
> 具体原因是因为前者是调用`fay_booter`，而后者是直接调用 `fay_core`。

Fay Core 通过用户从 Webui 输入消息

## 使用说明

### 1. 安装依赖

请使用一下指令安装 Fay 项目所需要的原来。

```bash
$ pip install -r requirement.txt
```

同时，为了调用 LLM 增强部分的内容，请安装以下额外依赖。

-   pandas: 用于导入 csv 数据
-   openai: 用于调用 ChatGPT 的 API
-   chroma: 向量数据库
-   sentence-transformers: Sentence Embedding 模型

> 由于依赖管理较乱，可能会安装多余的库，或少安装了某些库，
> 请根据实际情况进行调整。

### 2. 配置密钥

由于本项目调用了很多云服务，所以需要配置好调用 API 所需要的 key。

复制项目根目录下的`system.example.conf`中的内容到`system.conf`，
并按照需求填写对应的 key 即可。

注意事项：

1. 如果填写了 ali 的 ASR 密钥，TTS 部分也会调用 ali 的 api
2. LLM 部分只实现了`chatgpt`, `rwkv_api`, `qianfan`

### 3. 运行

若想完全启动本项目的全功能，还需要配合 UE5 使用，在此就不提供使用方法了。
以下，我们提供提供了控制器运行和 CLI 运行两种方式。

#### (1) 控制器运行

在该模式下，不仅可以对话，还可以启动 TTS 服务。

1. 输入 `python main.py`
2. 点击窗口左下角的链接按钮
3. 若左上角提示链接成功，则说明运行成功
4. 在右边的聊天框中输入问题，并按`Ask`发送

#### (2) CLI 运行

我们也提供了一个直接调用 LLM 模块的接口，
以此方便调试 LLM 模块的功能。

1. 输入 `python src/test_gpt.py`
2. 直接输入问题，并回车
3. 输入`exit` 退出
