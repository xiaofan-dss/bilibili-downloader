# 请求头与Referer配置

<cite>
**本文档引用的文件**   
- [config.py](file://config.py)
- [bilibili_cover_crawler_playwright.py](file://bilibili_cover_crawler_playwright.py)
</cite>

## 目录
1. [headers_templates配置详解](#headers_templates配置详解)
2. [referers配置详解](#referers配置详解)
3. [模板适用场景分析](#模板适用场景分析)
4. [自定义配置指导](#自定义配置指导)
5. [Referer配置的重要性](#referer配置的重要性)

## headers_templates配置详解

`headers_templates`配置项定义了多组模拟真实浏览器的请求头模板，用于在发送请求时轮换使用，从而增强爬虫的隐蔽性。该配置位于`config.py`文件中的`VIDEO_DOWNLOAD_CONFIG`字典内，包含三个预定义的模板，分别适用于不同场景。

每个模板都包含一组HTTP请求头字段，如`Accept`、`Accept-Language`、`Accept-Encoding`等，这些字段模拟了真实浏览器的行为。通过轮换使用这些模板，可以有效避免因请求头过于单一而被目标网站识别为自动化爬虫。

**Section sources**
- [config.py](file://config.py#L300-L330)

## referers配置详解

`referers`配置项用于设置随机的Referer来源，防止被识别为爬虫。该配置同样位于`config.py`文件中的`VIDEO_DOWNLOAD_CONFIG`字典内，包含四个预定义的Referer来源，分别是B站首页、用户空间、视频页面和搜索页面。

通过随机选择这些Referer来源，可以模拟用户从不同页面跳转到目标页面的行为，从而降低被反爬虫系统检测到的风险。正确的Referer配置对于访问视频资源尤为重要，因为许多网站会检查Referer头来验证请求的合法性。

**Section sources**
- [config.py](file://config.py#L360-L370)

## 模板适用场景分析

### 通用模板1 - 适合大多数场景
此模板适用于大多数常规请求，如页面浏览、API调用等。它使用通配符`*/*`作为`Accept`头的值，表示接受所有类型的响应内容。同时，设置了`DNT`（Do Not Track）头，模拟用户隐私保护行为。

### 通用模板2 - 视频请求专用
此模板专为视频请求设计，`Accept`头明确指定了视频和音频的MIME类型，如`video/webm`、`video/ogg`等。此外，`Accept-Encoding`头设置为`identity;q=1, *;q=0`，表示优先使用无压缩编码，这在视频流传输中较为常见。

### 通用模板3 - API请求专用
此模板专为API请求设计，`Accept`头设置为`application/json, text/plain, */*`，表示优先接受JSON格式的响应。同时，`Origin`头设置为`https://www.bilibili.com`，模拟跨域请求的来源。

**Section sources**
- [config.py](file://config.py#L300-L350)

## 自定义配置指导

为了进一步增强爬虫的隐蔽性，用户可以根据需要添加自定义的请求头或Referer来源。以下是一些指导建议：

1. **添加自定义请求头**：可以在`headers_templates`列表中添加新的字典，定义所需的请求头字段。例如，可以添加`Cache-Control`、`Pragma`等头来模拟更复杂的浏览器行为。
2. **扩展Referer来源**：可以在`referers`列表中添加更多的Referer来源，如特定的视频分类页面、活动页面等，以增加请求的多样性。
3. **动态生成请求头**：可以通过编程方式动态生成请求头，如随机选择User-Agent、修改`Accept-Language`等，使每次请求的特征都不完全相同。

**Section sources**
- [config.py](file://config.py#L300-L370)

## Referer配置的重要性

正确配置Referer对于访问视频资源至关重要。许多网站，尤其是视频平台，会严格检查Referer头来防止资源被非法盗用。如果Referer头缺失或不正确，服务器可能会拒绝提供视频资源，导致请求失败。

在本项目中，`referers`配置项通过随机选择B站内部的多个页面作为Referer来源，有效地模拟了用户从站内其他页面跳转到视频页面的行为。这种做法不仅提高了请求的成功率，还降低了被反爬虫系统检测到的风险。

**Section sources**
- [config.py](file://config.py#L360-L370)
- [bilibili_cover_crawler_playwright.py](file://bilibili_cover_crawler_playwright.py#L150-L160)